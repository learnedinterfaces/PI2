from random import sample, shuffle, random
import heapq

from interface.visualizations import *
from interface.widgets import *
from interface.interaction import *
from config import Config
from random_mapping import all_schema_entries, collect_candidate_mapping
from interface.interface import Interface

best_mappings = None
best_cost = float("inf")

search_count = 0
best_k_costs = []
best_K = 10
# the optimal solution of exactly covering the widget set
partial_optimal = {}
# the optimal solution of covering the widget set  ( allow duplicates and allow cover extra ones)
cover_optimal = {}

def search_mapping(difftrees, known_best_score):
    global best_mappings, best_cost, best_k_costs, best_K, search_count, partial_optimal
    best_mappings = None
    best_cost = float("inf")

    #best_cost = known_best_score * 1.01
    search_count = 0
    best_k_costs = []
    best_K = 10
    partial_optimal = {}
    cover_optimal = {}

    #print("\n".join([t.root.get_text() for t in difftrees]))
    '''
      vis  : { treeid : Vis}
      wi : widget and interaction list, (class type, node) 
      mapping: a list of object interaction/ widget
    '''
    mappings = dict(

        vis={},
        wi=[],
        mappings=[],
    )

    import time
    now = time.time()
    search_vis(difftrees, 0, mappings, cur_cost=0)

    #print(time.time() - now)

    for rec in best_k_costs:
        cur_mappings = rec.mappings

        mappings["vis"] = cur_mappings["vis"]
        mappings["wi"] = cur_mappings["wi"]
        mappings["mappings"] = []

        for tree in difftrees:
            tree.vis = cur_mappings["vis"][tree.tid]
        iacts = set()
        for item, node in cur_mappings["wi"]:
            if isinstance(item, Interaction):
                item.map_node(node)
                if item.iid not in iacts:
                    mappings["mappings"].append(item)
                    iacts.add(item.iid)
                    item.vis.m = item
            else:
                mappings["mappings"].append(item(node))

        search_layout(difftrees, mappings)

        for item, node in cur_mappings["wi"]:
            if isinstance(item, Interaction):
                if item.iid in iacts:
                    iacts.discard(item.iid)
                    item.vis.m = None
                item.nodes.pop()
            else:
                node.widget = None

        for tree in difftrees:
            tree.vis = None

    print("search time: ", time.time() - now, search_count)


    # re-create the widgets and fix the layout ref to new ids.
    # may be not necessary ..TODO( check whether it can be deleted)
    for tree in difftrees:
        try:
            tree.vis = best_mappings["vis"][tree.tid]
        except:
            import sys
            sys.stderr.write(str(Config.config) + "\n")
    mappings = []
    iacts = set()
    for item, node in best_mappings["wi"]:
        if isinstance(item, Interaction):
            item.map_node(node)
            if item.iid not in iacts:
                mappings.append(item)
                iacts.add(item.iid)
                item.vis.m = item
        else:
            mappings.append(item(node))

    def fix_layout(layout):
        if isinstance(layout, (Horizontal, Vertical)):
            layout.children = list([fix_layout(c) for c in layout.children])
            if layout.widget is not None:
                layout.widget = fix_layout(layout.widget)
            return layout
        elif isinstance(layout, Visualization):
            return layout.difftree.vis
        else:
            return layout.node.widget if not isinstance(layout, Label) else layout

    return fix_layout(best_mappings["layout"]), mappings


def search_vis(difftrees, next, mappings, cur_cost):
    global search_count

    if cur_cost > best_cost: return
    if best_k_costs and cur_cost > best_k_costs[0].cost: return

    if next == len(difftrees):
        all_entries = all_schema_entries(difftrees)
        candidates = collect_candidate_mapping(difftrees)
        entry_list = sorted(list(all_entries))
        shuffle(entry_list)
        iacts = set()
        search_interaction(difftrees, all_entries, candidates, entry_list, iacts, 0, mappings, cur_cost=cur_cost)
    else:
        difft = difftrees[next]
        cands = candidate_visualizations(difft)
        for V, enc in cands:
            difft.vis = V(difft, enc)
            mappings["vis"][difft.tid] = difft.vis
            search_vis(difftrees, next + 1, mappings, cur_cost + difft.vis.cost)
            difft.vis = None

class MapRec:
    def __init__(self, cost, mappings):
        self.cost = cost
        self.mappings = mappings
    def __lt__(self, other):
        return self.cost > other.cost


'''
all_entries: a set of entries that have not been mapped 
entry list: all the choice node list 

'''

def search_interaction(difftrees, all_entries, candidates, entry_list, iacts, next, mappings, cur_cost):
    global best_k_costs, best_K, search_count
    if next == len(entry_list):
        for cost, maps in search_widget(difftrees, all_entries, candidates, entry_list, iacts, 0):
            if cur_cost + cost >= best_cost: break
            if len(best_k_costs) == best_K and cur_cost + cost >= best_k_costs[0].cost: break
            cur_mappings = dict(vis={}, wi=[], layout={})
            for v in mappings["vis"]:
                cur_mappings["vis"][v] = mappings["vis"][v]
            for w in mappings["wi"]:
                cur_mappings["wi"].append(w)
            cur_mappings["wi"] += maps
            heapq.heappush(best_k_costs, MapRec(cur_cost + cost, cur_mappings))

            if len(best_k_costs) > best_K: 
                heapq.heappop(best_k_costs)
    else:
        entry = entry_list[next]

        if entry not in all_entries:
            return search_interaction(difftrees, all_entries, candidates, entry_list, iacts, next + 1, mappings, cur_cost)
        else:
            widget_entries = []
            for e in entry_list[:next]:
                if e in all_entries:
                    widget_entries.append(e)
            wcost = search_cover(difftrees, set(widget_entries), candidates, entry_list, iacts, 0)

            if cur_cost + wcost >= best_cost: return
            if len(best_k_costs) == best_K and cur_cost + wcost >= best_k_costs[0].cost: return

            cands = []
            for item, node, covers in candidates:
                if covers.issubset(all_entries) and entry in covers:
                    if isinstance(item, Interaction):
                        if not item.vis.m:
                            cands.append((item, node, covers))
                        elif item.vis.m == item:
                            same_tree = False
                            for nd in item.vis.m.nodes:
                                if nd.difftree == node.difftree: same_tree = True
                            if not same_tree:
                                cands.append((item, node, covers))

            def ckey(cand):
                item, _, _ = cand
                if item.mtype == MType.BRUSHXY:
                    return 0
                elif item.mtype == MType.BRUSHX or item.mtype == MType.BRUSHY:
                    return 1
                else:
                    return 2
    
            cands.sort(key=ckey)

            for item, node, covers in cands:
                all_entries -= covers
                mappings["wi"].append((item, node))

                item.map_node(node)
                new_add = False
                if item.iid not in iacts:
                    mappings["mappings"].append(item)
                    iacts.add(item.iid)
                    item.vis.m = item
                    new_add = True

                search_interaction(difftrees, all_entries, candidates, entry_list, iacts, next + 1, mappings, 
                            cur_cost=(cur_cost + mappings["mappings"][-1].cost()) if new_add else cur_cost)

                if new_add:
                    mappings["mappings"].pop()
                    iacts.discard(item.iid)
                    item.vis.m = None
                item.nodes.pop()

                mappings["wi"].pop()
                all_entries |= covers

            search_interaction(difftrees, all_entries, candidates, entry_list, iacts, next + 1, mappings,  cur_cost)


'''
estimate the lowest bound of covering all_entries with widgets. 
the optimal solution of covering the widget set Ns  ( allow duplicates and allow cover extra ones)
	G[Ns] = {
		Let smallest_cost = +inf
		Let n := the first node in Ns,
		For n’s candidate widgets w:
			smallest_cost >?= G[Ns-w.covers] + w.cost
		Return smallest_cost
	}
'''
def search_cover(difftrees, all_entries, candidates, entry_list, iacts, next):
    global best_k_costs, best_K, search_count, partial_optimal, cover_optimal

    all_entries_hash = hash(tuple(sorted(list(all_entries))))

    if all_entries_hash in cover_optimal:
        return cover_optimal[all_entries_hash]

    if len(all_entries) == 0: return 0

    entry = entry_list[next]
    if entry not in all_entries:
        return search_cover(difftrees, all_entries, candidates, entry_list, iacts, next + 1)
    else:
        cands = []
        for item, node, covers in candidates:
            if isinstance(item, Interaction):
                continue
            if entry in covers:
                cands.append((item, node, covers))

        cover_cost = float("inf")
        for item, node, covers in cands:
            new_entries = all_entries - covers

            widget = item(node)
            wcost = widget.cost()

            cost = search_cover(difftrees, new_entries, candidates, entry_list, iacts, next + 1)
            cover_cost = min(cover_cost, cost + wcost)

            node.widget = None

        cover_optimal[all_entries_hash] = cover_cost

        return cover_optimal[all_entries_hash]

# the optimal solution of exactly covering the widget set
def search_widget(difftrees, all_entries, candidates, entry_list, iacts, next):
    global best_k_costs, best_K, search_count, partial_optimal

    all_entries_hash = hash(tuple(sorted(list(all_entries))))

    if all_entries_hash in partial_optimal:
        return partial_optimal[all_entries_hash]

    if len(all_entries) == 0:
        return [(0, [])]

    entry = entry_list[next]
    if entry not in all_entries:
        return search_widget(difftrees, all_entries, candidates, entry_list, iacts, next + 1)
    else:
        cands = []
        for item, node, covers in candidates:
            if covers.issubset(all_entries) and entry in covers:
                if isinstance(item, Interaction):
                    continue
                else:
                    cands.append((item, node, covers))

        mappings = []
        for item, node, covers in cands:
            all_entries -= covers
            widget = item(node)
            wcost = widget.cost()

            for cost, maps in search_widget(difftrees, all_entries, candidates, entry_list, iacts, next + 1):
                mappings.append((cost + wcost, maps + [(item, node)]))

            node.widget = None
            all_entries |= covers

        mappings.sort(key=lambda s: s[0])

        partial_optimal[all_entries_hash] = mappings[:best_K]

        return partial_optimal[all_entries_hash]

def build_layout_tree(node):

    # build label for inner's radio node's children.

    widgets = []
    widgets_with_label = []
    if node.widget is not None and not isinstance(node.widget, Label):
        widget = node.widget
        for c in node.children:
            if c.parent != node: continue
            cw = build_layout_tree(c)
            if cw is None:
                if isinstance(node.widget, (CRadio, Toggle, Adder)) and c.node_schema is not None:
                    # Interaction
                    widgets.append(Label('Interaction'))
                    widgets_with_label.append(Label('Interaction'))
                else:
                    # c is a label
                    widgets_with_label.append(Label(c))
            else:
                widgets.append(cw)
                widgets_with_label.append(cw)
        # if the children has one widget, then we create the label for
        # the children without widgets.
        if widgets:
            widgets = widgets_with_label
    else:
        widget = None
        for c in node.children:
            if c.parent != node: continue
            cw = build_layout_tree(c)
            if cw is not None:
                widgets.append(cw)

    if len(widgets) == 0:
        return widget
    else:
        if widget is None:
            if len(widgets) == 1:
                return widgets[0]
            else:
                return Unknown(widgets)
        else:
            return Unknown(widgets, widget)

def build_layout_trees(difftrees):
    layout_trees = []

    for tree in difftrees:
        widget_tree = build_layout_tree(tree.root)
        if widget_tree is not None:
            un = Unknown([tree.vis, widget_tree])
            layout_trees.append(un)
        else:
            layout_trees.append(tree.vis)
    if len(layout_trees) == 1:
        return layout_trees[0]
    else:
        return layout_trees

all_costs = []

def permutation(eles):
    if not eles: yield []
    else:
        for i, e in enumerate(eles):
            for rest in permutation(eles[0:i] + eles[i+1:]):
                yield [e] + rest

def find_first_unknown(node, par):
    if isinstance(node, Unknown):
        return (node, par)
    if isinstance(node, (Horizontal, Vertical)):
        for i, c in enumerate(node.children):
            c.layout_parent = node
            un = find_first_unknown(c, (node, i))
            if un is not None:
                return un
        return None
    else:
        return None

'''
    record the answer
'''

def duplicate_layout(layout):
    children = []
    if isinstance(layout, Vertical):
        for c in layout.children:
            children.append(duplicate_layout(c))
        return Vertical(children, layout.widget)
    elif isinstance(layout, Horizontal):
        for c in layout.children:
            children.append(duplicate_layout(c))
        return Horizontal(children, layout.widget)
    else:
        return layout


def search_layout_tree(difftrees, layout, mappings, depth=0):
    global best_mappings, best_cost
    global all_costs, search_count

    first = find_first_unknown(layout, None)
    if first is not None:
        ui = Interface(difftrees, layout, mappings["mappings"], Config)
        ui_cost = ui.cost()[0]
        if ui_cost > best_cost: return
        node, par = first
        for L in [Vertical, Horizontal]:
            if par is None:
                layout = L(layout.children, layout.widget)
                search_layout_tree(difftrees, layout, mappings, depth+1)
                layout = Unknown(layout.children, layout.widget)
            else:
                p, i = par
                p.children[i] = L(p.children[i].children, p.children[i].widget)
                pp = p
                pp.update_size()
                while hasattr(pp, "layout_parent"):
                    pp = pp.layout_parent
                    pp.update_size()
                search_layout_tree(difftrees, layout, mappings, depth+1)
                p.children[i] = Unknown(p.children[i].children, p.children[i].widget)
    else:
        # finish search, the layout tree without unknown
        ui = Interface(difftrees, layout, mappings["mappings"], Config)
        ui_cost = ui.cost()[0]
        if ui_cost < best_cost:
            best_cost = ui_cost
            best_mappings = dict(vis={}, wi=[], layout={})
            for v in mappings["vis"]:
                best_mappings["vis"][v] = mappings["vis"][v]
            for w in mappings["wi"]:
                best_mappings["wi"].append(w)
            best_mappings["layout"] = duplicate_layout(layout)


def search_layout(difftrees, mappings):
    sketch = build_layout_trees(difftrees)
    if isinstance(sketch, list):
        for order in permutation(sketch):
            layout = Unknown(order)
            search_layout_tree(difftrees, layout, mappings)
    else:
        search_layout_tree(difftrees, sketch, mappings)
