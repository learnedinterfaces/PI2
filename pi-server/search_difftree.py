import time
from rules import *
from mcts import MCTS, MCTSTask

from difftree.difftree import Difftree
# from difftree.param_difftree import Difftree

from random_mapping import random_mapping
from search_mapping import search_mapping
from config import Config
from interface.interface import Interface
from interface.interaction import Interaction
import random
from generalize import *
from copy import deepcopy


class DifftTask(MCTSTask):

    def __init__(self, catalog, sample_outputs, parse_queries,db, prefer_generalize):
        self.catalog = catalog
        self.sample_outputs = sample_outputs
        self.parse_queries = parse_queries
        self.finished = False
        self.db = db
        self.prefer_generalize = prefer_generalize

    def get_choice_nodes(self, node):
        # get all the choice node in the difftree
        # transformation rules only targets at the choice nodes
        chs = []
        for c in node.children:
            chs += self.get_choice_nodes(c)
        if isinstance(node, ChoiceNode):
            chs.append(node)
        return chs

    def get_actions(self, state, rw=False):
        # state =  [[tree1, ..], [sqlschema1, ...], [hash, ..]]
        # tree1 are current state,
        # hash is for trees , records the path of states transition.
        trees, _, hashs = state
        cands = []
        # skip --> finished
        if self.finished:
            return []
        if len(hashs) > len(set(hashs)): return []

        # rw: random walk will not allow split and merge
        # random walk heuristic: random walk until there is no rule to apply, would be better
        # in most cases.  -- strategy:  skip rule has a 0.01 probability to apply.
            # filter case:  should apply Optpushdownlist to the end
            # where c > 0 and c < 1: should not apply Optpushdownlist to the end
        # for opypushdownlist:
        for root in state[0]:
            if Merge in rule_list:
                infos = Merge.test(state, None)
                for info in infos:
                    cands.append(((Merge, info), 0 if rw else 1))
            for node in self.get_choice_nodes(root):
                for rule in rule_list:
                    if rule == Merge: continue
                    infos = rule.test(state, node)
                    for info in infos:
                        if rule in [NoopOPT, NoopANY]:
                            return [((rule, info), 1)]
                        # Assign a low possibility to FIXEDMulti rule
                        cands.append(((rule, info), 0 if rw and rule == Split else (0.1 if rule == FixedMulti else 1)))

        if cands:
            cands.append((("Skip", None), 0.01))
            pass
        else:
            cands = [(("Skip", None), 1.0)]
        return cands

    def apply(self, state, act):
        rule, info = act
        if rule == "Skip":
            self.finished = True
            return state, (rule, None)
        else:
            state, reverse = rule.apply(state, info)

            '''
            print(rule)
            for tree in state[0]:
                print(tree.print())
                print(tree.get_text())
                print("-" * 50)
            print("=" * 100)
            '''

            '''
            if __debug__:
                if self.check_id_unique(state) == False:
                    print("not unique"  + str(act))
            '''

            return state, (rule, reverse)

    def restore(self, state, reverse):
        rule, reverse = reverse
        if rule == "Skip":
            self.finished = False
            return state
        else:
            state = rule.restore(state, reverse)
            '''
            if __debug__:
                if self.check_id_unique(state) == False:
                    print("not unique"  + str(rule))     
            '''
            return state

    def check_id_unique(self, state):
        trees = state[0]
        node_id = set()
        duplicate = False

        def collect_node_id(tree):
            nonlocal node_id, duplicate
            if tree.nid in node_id:
                #print("duplicate nid", str(tree))
                duplicate = True
            node_id.add(tree.nid)
            for c in tree.children:
                collect_node_id(c)

        for t in trees:
            collect_node_id(t)
        return not duplicate

    '''
        Evaluate a given difftree. 
    '''
    def evaluate(self, state):
        trees, _, hashs = state

        difftrees = []
        merged = []

        for tree in trees:
            parsed = [(self.parse_queries[i], i) for i in sorted(list(tree.queries))]
            sample = [self.sample_outputs[i] for i in sorted(list(tree.queries))]
            difft = Difftree(tree, self.catalog, parsed, sample)

            def merge(node, base_node):
                if node == node.difftree.root:
                    node.difftree.root = base_node
                else:
                    node.parent.children[node.crank] = base_node

            # merge duplicate choice nodes: heuristic: it two choice nodes always have the same choice, merge.
            for i in range(len(difft.choices)):
                node = difft.choices[i]
                for j in range(i):
                    base_node = difft.choices[j]
                    if node.node_schema == base_node.node_schema and node.history == base_node.history:
                        del difft.unique_schemas[node.node_schema.shash()]
                        merge(node, base_node)
                        merged.append(node)
                        break
            difft.choices = []
            difft.unique_schemas = {}
            difft.infer_schema(difft.root)

            difftrees.append(difft)

        def clear_widgets(node):
            for c in node.children:
                clear_widgets(c)
            node.widget = None

        layouts, mappings = random_mapping(difftrees)

        if layouts is None:
            cost = 1000000000
            mappings = None
        else:
            if self.prefer_generalize:
                generalized_nodes = []
                difftrees = generalize( difftrees, self.db, self.catalog, generalized_nodes)
            ui = Interface(difftrees, layouts, mappings, Config)
            cost = ui.cost()[0]

        def clear_node(node):
            for c in node.children:
                clear_node(c)
            node.domain = set()
            node.visit_ts = set()
            node.history = []
            node.widget = None
            node.last_choice = None

        # restore to the state before evaluation.
        for n in reversed(merged):
            n.parent.children[n.crank] = n

        # restore if generalized
        if self.prefer_generalize:
            #  if generalized, delete the newly generated nodes
            for node in generalized_nodes:
                parent = node.parent
                parent.children.remove(node)

        for n in trees:
            clear_node(n)

        tree_text = "\n".join([t.root.get_text() for t in difftrees])
        chars = {}
        for c in tree_text:
            chars.setdefault(c, 0)
            chars[c] += 1
        return (-cost, tuple(sorted(list(chars.items())))), mappings

def search_difftree(clusters, catalog, sample_outputs, parse_queries, db, pre_generalize):
    trees = []
    schemas = []
    for cluster, sqlschema in clusters:
        if len(cluster) == 1:
            trees.append(cluster[0])
            schemas.append(sqlschema)
        else:
            tree = ANYNode(cluster)
            trees.append(tree)
            schemas.append(sqlschema)
    state = (trees, schemas, [hash(tuple([t.chash() for t in trees]))])
    state2 = deepcopy(state)


    searcher = MCTS(state, DifftTask(catalog, sample_outputs, parse_queries, db, pre_generalize))
    (trees, _, _), score = searcher.play()
    rule_list.remove(Merge)
    rule_list.remove(Split)
    searcher = MCTS(state2, DifftTask(catalog, sample_outputs, parse_queries, db, pre_generalize))
    (trees2, _, _), score2 = searcher.play()
    if score2[0] > score[0]:
        trees = trees2
        score = score2
    return trees, -score[0]
