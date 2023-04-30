from interface.visualizations import *
from interface.interaction import *
from random import sample, shuffle, random
from difftree.nodes import *

def get_schema_entries(schema, entries):
    if hasattr(schema, "node") and schema.node is not None:
        entries.add(schema.node.nid)
    if hasattr(schema, "schema_list"):
        for c in schema.schema_list:
            get_schema_entries(c, entries)
    if hasattr(schema, "sub_schema"):
        get_schema_entries(schema.sub_schema, entries)

def all_schema_entries(difftrees):
    entries = set([])
    for tree in difftrees:
        if tree.root.node_schema is not None:
            get_schema_entries(tree.root.node_schema, entries)
    return entries

def collect_candidate_mapping(difftrees):
    candidates = []
    for tree in difftrees:
        # get_widget candidates
        for node in tree.unique_schemas.values():
            if node.node_schema is not None:
                if isinstance(node.node_schema, ListSchema):
                    map_entry = set([s.node.nid for s in node.node_schema.schema_list])
                elif isinstance(node.node_schema, OptionSchema):
                    map_entry = set()
                    map_entry.add(node.node_schema.node.nid)
                    tmp = node.node_schema
                    while(isinstance(tmp.sub_schema, OptionSchema)) and \
                        (isinstance(tmp.node.children[0], (OPTNode, CoOPTNode))):
                        map_entry.add(tmp.sub_schema.node.nid)
                        tmp = tmp.sub_schema
                else:
                    map_entry = {node.node_schema.node.nid}
                for c in candidate_widgets(node):
                    candidates.append((c, node, map_entry))

        #get interaction candidates
        for interact in tree.vis.candidate_interactions():
                for other_tree in difftrees:
                    for node in other_tree.unique_schemas.values():
                        if interact.valid_mapping(node):
                            map_entry = set()
                            get_schema_entries(node.node_schema, map_entry)
                            candidates.append((interact, node, map_entry))
    return candidates

def random_layout(difftrees):

    def _random_layout_node():
        return sample([Vertical, Horizontal], 1)[0]

    def _random_layout(node):
        widgets = []
        widgets_with_label = []
        if node.widget is not None and not isinstance(node.widget, Label):
            widget = node.widget
            for c in node.children:
               if c.parent != node: continue
               cw = _random_layout(c)
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
                cw = _random_layout(c)
                if cw is not None:
                    widgets.append(cw)

        if len(widgets) == 0:
            return widget
        else:
            if widget is None:
                if len(widgets) == 1:
                    return widgets[0]
                else:
                    return _random_layout_node()(widgets)
            else:
                return _random_layout_node()(widgets, widget)

    layout_trees = []
    for tree in difftrees:
        widget_tree = _random_layout(tree.root)
        if widget_tree is not None:

            layout_trees.append(_random_layout_node()([tree.vis, widget_tree]))
        else:
            layout_trees.append(tree.vis)

    shuffle(layout_trees)
    return _random_layout_node()(layout_trees)

def random_mapping(difftrees, fully_random=False):

    # map visualization
    for difft in difftrees:
        cands = candidate_visualizations(difft)
        if cands:
            V, enc = sample(cands, 1)[0]
            difft.vis = V(difft, enc)
        else:
            return None, None

    all_entries = all_schema_entries(difftrees)
    # candidates = [  (widget/interaction, node, all the entries it covers}]
    candidates = collect_candidate_mapping(difftrees)

    mappings = []
    # all the choice nodes.
    entry_list = sorted(list(all_entries))
    shuffle(entry_list)
    def ckey(cand):
        item, _, _ = cand
        if isinstance(item, Interaction):
            if item.mtype == MType.BRUSHXY:
                return 0 + random()
            elif item.mtype == MType.BRUSHX or item.mtype == MType.BRUSHY:
                return 1 + random()
            else:
                return 2 + random()
        else:
            return 3 + random()

    iacts = set()
    # random mapping.
    for entry in entry_list:
        if entry not in all_entries: continue
        cands = []
        for item, node, covers in candidates:
            if covers.issubset(all_entries) and entry in covers:
                if isinstance(item, Interaction):
                    if not item.vis.m:
                        cands.append((item, node, covers))
                    elif item.vis.m == item:
                        # interaction can map to different difftree's choice node,
                        # but can not map to diff choice nodes in one tree.
                        same_tree = False
                        for nd in item.vis.m.nodes:
                            if nd.difftree == node.difftree: same_tree = True
                        if not same_tree:
                            cands.append((item, node, covers))
                else:
                    cands.append((item, node, covers))
        if fully_random:
            shuffle(cands)
        else:
            sorted_cands = sorted(list([(ckey(c), c) for c in cands]))
            cands = list([c[1] for c in sorted_cands])

        if not cands:
            return None, None
        item, node, covers = cands[0]
        all_entries -= covers
        if isinstance(item, Interaction):
            item.map_node(node)
            if item.iid not in iacts:
                mappings.append(item)
                iacts.add(item.iid)
            item.vis.m = item
        else:
            mappings.append(item(node))
    
    return random_layout(difftrees), mappings
