from enum import Enum
from difftree.schema import *


class MType(Enum):
    SINGLE = 1
    MULTI = 2
    BRUSHX = 3
    BRUSHY = 4
    BRUSHXY = 5
    PANX = 6
    PANY = 7
    PANXY = 8
    ZOOMX = 9
    ZOOMY = 10
    ZOOMXY = 11


class MSpace(Enum):
    PIXEL = 1
    DATA = 2
    MARK = 3


class M(object):
    def __init__(self, mtype, mspace, encodings):
        self.type = mtype
        self.space = mspace
        self.encodings = encodings


class Interaction(object):

    interact_id = 0

    def __init__(self, vis, mtype, mspace, names, schema, domain):
        self.vis = vis
        self.mtype = mtype
        self.mspace = mspace
        self.names = names
        self.schema = schema
        self.domain = domain  # candidate domains from sample queries
        self.nodes = []
        self.iid = None

    def wtype(self):
      return str(self.mtype)

    def valid_mapping(self, node):
        '''
            Return True if node can be mapped to self.interaction.
        '''
        if node.node_schema is None: return False
        if isinstance(node.node_schema, OptionSchema):
            node = node.node_schema.node.children[0]

        if node.node_schema != self.schema:
            return False
        try:
            if self.mtype in [MType.PANX, MType.PANY]:
                #if node.difftree != self.vis.difftree: return False
                sel_min = [float(c.get_text()) for c in node.node_schema.schema_list[0].node.children]
                sel_max = [float(c.get_text()) for c in node.node_schema.schema_list[1].node.children]
                if len(sel_min) == len(sel_max):
                    for i in range(len(sel_min)):
                        if sel_max[i] - sel_min[i] != sel_max[0] - sel_min[0]:
                            return False
                    return True
                else:
                    return False
            elif self.mtype == MType.PANXY:
                #if node.difftree != self.vis.difftree: return False
                sel_min_x = [float(c) for c in [h[0] for h in node.node_schema.schema_list[0].node.history]]
                sel_max_x = [float(c) for c in [h[0] for h in node.node_schema.schema_list[1].node.history]]
                sel_min_y = [float(c) for c in [h[0] for h in node.node_schema.schema_list[2].node.history]]
                sel_max_y = [float(c) for c in [h[0] for h in node.node_schema.schema_list[3].node.history]]
                for i in range(max(len(sel_min_x), len(sel_max_x), len(sel_min_y), len(sel_max_y))):
                    if sel_max_x[i] - sel_min_x[i] != sel_max_x[0] - sel_min_x[0]:
                        return False
                    if sel_max_y[i] - sel_min_y[i] != sel_max_y[0] - sel_min_y[0]:
                        return False
                return True
            elif self.mtype in [MType.ZOOMX, MType.ZOOMY]:
                #if node.difftree != self.vis.difftree: return False
                sel_min = [float(c.get_text()) for c in node.node_schema.schema_list[0].node.children]
                sel_max = [float(c.get_text()) for c in node.node_schema.schema_list[1].node.children]
                # if the interval is all the same, then it would be better to choose pan.
                if len(sel_min) == len(sel_max):
                    all_same = True
                    for i in range(len(sel_min)):
                        if sel_max[i] - sel_min[i] != sel_max[0] - sel_min[0]:
                            all_same = False
                    return not all_same
                else:
                    return False
            elif self.mtype == MType.ZOOMXY:
                #if node.difftree != self.vis.difftree: return False
                sel_min_x = [float(c) for c in [h[0] for h in node.node_schema.schema_list[0].node.history]]
                sel_max_x = [float(c) for c in [h[0] for h in node.node_schema.schema_list[1].node.history]]
                sel_min_y = [float(c) for c in [h[0] for h in node.node_schema.schema_list[2].node.history]]
                sel_max_y = [float(c) for c in [h[0] for h in node.node_schema.schema_list[3].node.history]]
                all_same = True
                for i in range(max(len(sel_min_x), len(sel_max_x), len(sel_min_y), len(sel_max_y))):
                    if sel_max_x[i] - sel_min_x[i] != sel_max_x[0] - sel_min_x[0]:
                        all_same = False
                    if sel_max_y[i] - sel_min_y[i] != sel_max_y[0] - sel_min_y[0]:
                        all_same = False
                    if abs((sel_max_x[i] - sel_min_x[i]) / (sel_max_y[i] - sel_min_y[i]) - (sel_max_x[0] - sel_min_x[0]) / (sel_max_y[0] - sel_min_y[0])) > 100000:
                        return False
                return not all_same
            else:

                if node.difftree == self.vis.difftree: return False
                if node.domain is not None:
                    def to_float(d):
                        try:
                            return float(d)
                        except:
                            return d
                    def to_tuple(d):
                        if not isinstance(d, tuple):
                            return tuple([d])
                        else:
                            return d
                    d = len(list(self.domain)[0])
                    '''
                    Todo: Change it to each tuple in node.domain, there is one in vis.domain 
                    which is able to express them. Current one enumerates the dimension which is 
                    equivalent. 
                    '''
                    for i in range(d):
                        dnode = set([to_float(to_tuple(s)[i]) for s in node.domain])
                        dvis = set([to_float(to_tuple(s)[i]) for s in self.domain])
                        if self.mtype in [MType.BRUSHX, MType.BRUSHY, MType.BRUSHXY]:
                            if min(dnode) < min(dvis) or max(dnode) > max(dvis):
                                return False
                        else:
                            if not dnode.issubset(dvis):
                                return False
                    return True
            return False
        except Exception as e:
            return False

    def map_node(self, node):
        self.iid = str(Interaction.interact_id)
        Interaction.interact_id += 1
        self.nodes.append(node)

    def cost(self):
        if self.mtype in [MType.PANX, MType.PANY, MType.PANXY, MType.BRUSHX, \
                          MType.BRUSHY, MType.BRUSHXY]:
            return 10
        elif self.mtype in [MType.ZOOMX, MType.ZOOMY, MType.ZOOMXY]:
            return 20
        else:
            return 30

    def to_spec(self):
        specs = []
        for i, node in enumerate(self.nodes):
            spec = {}
            spec["id"] = self.iid + "-" + str(i)
            spec["source"] = str(self.vis.vid)
            spec["target"] = str(node.difftree.vis.vid)
            spec["m"] = {}
            spec["m"]["type"] = {MType.SINGLE: "SINGLE", MType.MULTI: "MULTI",
                                 MType.BRUSHX: "BRUSHX", MType.BRUSHY: "BRUSHY", MType.BRUSHXY: "BRUSHXY",
                                 MType.PANX: "PANX", MType.PANY: "PANY", MType.PANXY: "PANXY",
                                 MType.ZOOMX: "ZOOMX", MType.ZOOMY: "ZOOMY", MType.ZOOMXY: "ZOOMXY"}[self.mtype]
            spec["m"]["space"] = {MSpace.PIXEL: "pixel", MSpace.MARK: "mark", MSpace.DATA: "data"}[self.mspace]
            spec["h"] = {}
            for i, name in enumerate(self.names):
                if name == "__index__": name = "key"
                sch = node.node_schema
                if isinstance(sch, OptionSchema):
                    spec["h"][str(sch.node.nid)] = "selected"
                    sch = sch.sub_schema
                if isinstance(sch, StarSchema):
                    sch = sch.sub_schema
                if isinstance(sch, ListSchema):
                    spec["h"][str(sch.schema_list[i].node.nid)] = name
                else:
                    spec["h"][str(sch.node.nid)] = name
            specs.append(spec)
        return specs
