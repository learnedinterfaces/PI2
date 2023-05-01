import json
from .widgets import *
from .costpreference import *
from .interaction import *
import math
import time
import os

COST_NUM = 0
cost_dist = [[], []]
stat_t = time.time()

estimation_time = 0

def reset_cost_stat():
    global COST_NUM, cost_dist, stat_t
    stat_t = time.time()
    COST_NUM = 0
    cost_dist = [[], []]

class Interface(object):

    def __init__(self, difftrees, layouts, mappings, Conf):
        self.difftrees = difftrees
        self.layouts = layouts
        self.mappings = mappings
        self.Conf = Conf
        layouts.push_xy(0, 0)

    def obtain_ts(self, schema):
        ts = set()
        if hasattr(schema, "node") and schema.node is not None:
            ts |= schema.node.visit_ts
        if hasattr(schema, "schema_list"):
            for c in schema.schema_list:
                ts |= self.obtain_ts(c)
        if hasattr(schema, "sub_schema"):
            ts |= self.obtain_ts(schema.sub_schema)
        return ts

    def contains_unknown(self, node):
        if isinstance(node, Unknown):
            return True
        if isinstance(node, (Horizontal, Vertical)):
            for c in node.children:
                if self.contains_unknown(c):
                    return True

    '''
     input: node in layout tree 
     dists[(vid, vid)] store the distance between a view vid and the other view vid'
     return: the dict of widgets with its boundary distance 
    '''
    def compute_distance(self, node, dists, required):
        widgets = {}
        if not isinstance(node, (Horizontal, Vertical, Unknown)):
            widgets[node.vid] = { "left": 0, "up": 0, "right": node.width, "down": node.height}
            dists[(node.vid, node.vid)] = 0
        else:
            children = []
            for c in node.children:
                subwidgets = self.compute_distance(c, dists, required)
                children.append(subwidgets)
            '''
            i and j are two subtrees of the node, enumerate the widget (a, b) in these subtrees
            if (a, b) are required ( in the trace of user manipulation), then compute the distance 
            of (a, b)
            '''
            for i in range(len(children)):
                inter_dist_h = 0
                inter_dist_v = 0
                for j in range(i+1, len(children)):
                    if j - 1 > i:
                        inter_dist_h += node.children[j-1].width
                        inter_dist_v += node.children[j-1].height
                    for a in children[i]:
                        for b in children[j]:
                            if (a, b) in required or (b, a) in required:
                                dists[(a, b)] = float("inf")
                                dists[(b, a)] = float("inf")
                                if isinstance(node, (Horizontal, Unknown)):
                                    dists[(a, b)] = min(dists[(a, b)], children[i][a]["right"] + \
                                                    inter_dist_h + children[j][b]["left"])
                                if isinstance(node, (Vertical, Unknown)):
                                    dists[(a, b)] = min(dists[(a, b)], children[i][a]["down"] + \
                                                    inter_dist_v + children[j][b]["up"])
                                dists[(b, a)] = dists[(a, b)]
                                required -= {(a, b), (b, a)}

            '''
                update the widget boundary estimation 
            '''
            required_widgets = set([a[0] for a in required]) | set([a[1] for a in required])
            for i in range(len(children)):
                for w in children[i]:
                    if w in required_widgets:
                        widgets[w] = {"left": float("inf"), "up": float("inf"), "right": float("inf"), "down": float("inf")}

            sum_height = sum_width = 0
            for i in range(len(children)):
                for w in children[i]:
                    if w in widgets:
                        if isinstance(node, (Horizontal, Unknown)):
                            widgets[w]["left"] = min(widgets[w]["left"], children[i][w]["left"] + (node.widget.width if node.widget else 0) + sum_width)
                            widgets[w]["up"] = min(widgets[w]["up"], children[i][w]["up"])
                        if isinstance(node, (Vertical, Unknown)):
                            widgets[w]["up"] = min(widgets[w]["up"], children[i][w]["up"] + sum_height)
                            widgets[w]["left"] = min(widgets[w]["left"], children[i][w]["left"] + (node.widget.width if node.widget else 0))
                sum_height += max(node.children[i].height, node.widget.height if node.widget else 0)
                sum_width += node.children[i].width + (node.widget.width if node.widget else 0)

            sum_height = sum_width = 0
            for i in range(len(children)-1, -1, -1):
                for w in children[i]:
                    if w in widgets:
                        if isinstance(node, (Horizontal, Unknown)):
                            widgets[w]["right"] = min(widgets[w]["right"], children[i][w]["right"] + sum_width)
                            widgets[w]["down"] = min(widgets[w]["down"], max(children[i][w]["down"], node.height))
                        if isinstance(node, (Vertical, Unknown)):
                            widgets[w]["right"] = min(widgets[w]["right"], max(children[i][w]["right"], node.width - (node.widget.width if node.widget else 0)))
                            widgets[w]["down"] = min(widgets[w]["down"], children[i][w]["down"] + sum_height)
                sum_height += max(node.children[i].height, node.widget.height if node.widget else 0)
                sum_width += node.children[i].width + (node.widget.width if node.widget else 0)

            '''
                the node.widget is set to be the leftupper corner of the container.  
                dists[(node.widget.vid, c)] computes the distance between the node.wiget(radio) and its children.  
            '''
            if node.widget:
                for c in widgets:
                    dists[(node.widget.vid, c)] = min(widgets[c]["left"], widgets[c]["up"])
                    dists[(c, node.widget.vid)] = dists[(node.widget.vid, c)]
                widgets[node.widget.vid] = { "left": 0, "up": 0, "right": node.width, "down": node.height}
                dists[(node.widget.vid, node.widget.vid)] = 0

        return widgets

    def cost(self):
        global COST_NUM
        global cost_dist
        global stat_t
        #if self.layouts.width > 1000: return 100000

        # TODO: measure cost based on effort to express the options in the diff tree
        widget_cost = sum([t.vis.cost for t in self.difftrees]) 
        widget_cost += sum([m.cost() for m in self.mappings])

        visit_cost = 0
        visits = []
        for m in self.mappings:
            if isinstance(m, Widget):
                for v in self.obtain_ts(m.node.node_schema):
                    visits.append((v, m))
            else:
                for node in m.nodes:
                    for v in self.obtain_ts(node.node_schema):
                        visits.append((v, m.vis))

        visits.sort(key=lambda s: s[0])
        if self.contains_unknown(self.layouts):
            '''
            for i in range(len(visits)):
                dx = visits[i][1].x - (visits[i - 1][1].x if i > 0 else 0)
                dy = visits[i][1].y - (visits[i - 1][1].y if i > 0 else 0)
                visit_cost += min(abs(dx), abs(dy))
                #visit_cost += math.sqrt(dx * dx + dy * dy)
            '''
            if visits:
                required_distances = set([(visits[i][1].vid, visits[i-1][1].vid) for i in range(1, len(visits))])
                required_distances.add((0, visits[0][1].vid))
                dists = {}
                global estimation_time
                import time
                now = time.time()
                boundary_dists = self.compute_distance(self.layouts, dists, required_distances)
                estimation_time += time.time() - now
                for i in range(1, len(visits)):
                    visit_cost += dists[(visits[i][1].vid, visits[i-1][1].vid)]/ min(visits[i][1].width, visits[i][1].height)
                visit_cost += min(boundary_dists[visits[0][1].vid]["left"], boundary_dists[visits[0][1].vid]["up"])/ min(visits[0][1].width, visits[0][1].height)
        else:
            for i in range(len(visits)):
                dx = visits[i][1].x - (visits[i - 1][1].x if i > 0 else 0)
                dy = visits[i][1].y - (visits[i - 1][1].y if i > 0 else 0)
                if PREFERHORIZONTAL: 
                    visit_cost += math.sqrt(dy * dy )/ min(visits[i][1].width, visits[i][1].height)
                else: 
                    visit_cost += math.sqrt(dx * dx + dy * dy )/ min(visits[i][1].width, visits[i][1].height)
        nav_cost = 50 * math.log(visit_cost + 1)

        w = max(self.layouts.width - self.Conf.max_width, 0) * 0.01 + 1
        h = max(self.layouts.height - self.Conf.max_height, 0) * 0.01 + 1
        h_penalty = self.layouts.height * 0.0001
        size_cost = (w * h) + h_penalty
        #print(f"size cost {size_cost}, rest cost {widget_cost+nav_cost}")
        cost = widget_cost + nav_cost
        COST_NUM += 1
        # cost_dist[0].append(time.time()-stat_t)
        # cost_dist[1].append(cost)
        return cost, nav_cost

    def to_spec(self):
        spec = {}
        backend = []

        spec["cost"] = self.cost()[0]

        db = {}
        db["id"] = "database"
        db["type"] = "db"
        db["dburi"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../examples/pi.db")
        backend.append(db)

        for difft in self.difftrees:
            backend.append(difft.to_spec("database"))

        spec["backends"] = backend

        spec["layout"] = self.layouts.layout_to_spec()

        views = []
        for difft in self.difftrees:
            if difft.vis is not None:
                views.append(difft.vis.to_spec())

        for item in self.mappings:
            if isinstance(item, Interaction):
              continue
            # if isinstance(item, CRadio):
            #    pass
            # else:
            views.append(item.to_spec())

        spec["views"] = views

        interactions = []

        for item in self.mappings:
            if isinstance(item, Interaction):
                interactions += item.to_spec()
            else:
                interactions += item.interaction_to_spec()

        spec["interactions"] = interactions

        return json.dumps(spec)
