from difftree.nodes import *
from copy import copy, deepcopy

def _any_node(children):
    if len(children) == 1:
        return children[0]
    else:
        opt = False
        for i, c in enumerate(children):
            if c.get_text() == '':
                children.pop(i)
                opt = True
                break
        if opt:
            return OPTNode([ANYNode(children)])
        else:
            return ANYNode(children)

class Rule(object):

    @classmethod
    def test(cls, state, node):
        return []

    @classmethod
    def apply(cls, state, info):
        pass

    @classmethod
    def restore(cls, state, reverse):
        pass

    @classmethod
    def is_static(cls, node):
        for c in node.children:
            if not cls.is_static(c):
                return False
        return not isinstance(node, ChoiceNode)

    @classmethod
    def merge(cls, nodes):
        new_node = copy(nodes[0])
        new_node.domain = set([])
        new_node.visit_ts = set([])
        new_node.nid = Node.next_id()
        new_node.history = []

        new_children = []
        for i in range(len(nodes[0].children)):
            new_children.append(cls.merge([n.children[i] for n in nodes]))
        new_node.children = new_children
        for i, c in enumerate(new_children):
            c.parent = new_node
            c.crank = i
        new_node.queries = set()
        for n in nodes:
            new_node.queries |= n.queries
        return new_node

    @classmethod
    def update_root(cls, roots, node, new_node):
        for i in range(len(roots)):
            if roots[i] == node:
                roots[i] = new_node
                return i

class PushDownAny(Rule):

    @classmethod
    def test(cls, state, node):
        # test whether the node can be pushde down or not.
        # return [] if not , [(node, None)] is yes.
        roots, _, _ = state
        # node is any
        if not isinstance(node, ANYNode): return []
        # childen are the same rule
        for i in range(len(node.children)):
            if isinstance(node.children[i], ChoiceNode): return []
            if node.children[i].rule != node.children[0].rule: return []
        # if children are list node, then childen's List delim is compatible
        max_children_num = max([len(c.children) for c in node.children])
        if max_children_num == 0: return []
        if isinstance(node.children[0], ListNode):
            delim = None
            for c in node.children:
                if delim is not None and c.delim is not None and delim != c.delim: return []
                if c.delim is not None: delim = c.delim
        return [(node, None)]


    @classmethod
    def pushdown_node(cls, state, node):

        children = []

        max_children_num = max([len(c.children) for c in node.children])
        for j in range(max_children_num):
            any_children = []
            optional = False
            for c in node.children:
                if len(c.children) > j:
                    any_children.append(c.children[j])
                else:
                    optional = True
            distinct_children = {}
            for c in any_children:
                hs = c.chash()
                distinct_children.setdefault(hs, [])
                distinct_children[hs].append(c)
            any_children = []
            for chchs in distinct_children.values():
                any_children.append(chchs[0] if len(chchs) == 1 else cls.merge(chchs))
            any_node = _any_node(any_children)
            if optional:
                any_node = OPTNode([any_node])
            children.append(any_node)
        if isinstance(node.children[0], ListNode):
            delim = None
            for c in node.children:
                if c.delim is not None: delim = c.delim
            new_node = ListNode(children, delim, node.children[0].rule)
        else:
            new_node = ASTNode(children, node.children[0].rule)

        # recursive push down the children.
        for i, c in enumerate(children):
            if PushDownAny.test(state, c) and not FixedMulti.test(state, c):
                n = cls.pushdown_node(state, c)
                n.parent = new_node
                n.crank = i
                new_node.children[i] = n
        return new_node

    @classmethod
    def apply(cls, state, info):

        roots, _, hashs = state
        node, _ = info
        reverse = [node, None]

        new_node = cls.pushdown_node(state, node)

        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            # if node is root, reverse keeps in index of the node in roots for further restore
            reverse[1] = cls.update_root(roots, node, new_node)

        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore_node(cls, node):
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
            cls.restore_node(c)

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        # restore node's children's pointer.
        cls.restore_node(node)

        hashs.pop()
        return state

class NoopANY(Rule):

    @classmethod
    def test(cls, state, node):
        roots, _, _ = state
        # node is any
        if not isinstance(node, ANYNode): return []
        # childen are exactly the same
        for i in range(1, len(node.children)):
            if node.children[i].chash() != node.children[0].chash(): return []
        return [(node, None)]

    @classmethod
    def apply(cls, state, info):
        roots, _, hashs = state
        node, _ = info
        reverse = [node, None]

        new_node = node.children[0] if len(node.children) == 1 else cls.merge(node.children)
        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            reverse[1] = cls.update_root(roots, node, new_node)
        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
        hashs.pop()
        return state


class NoopOPT(Rule):

    @classmethod
    def test(cls, state, node):
        roots, _, _ = state
        # node is any
        if not isinstance(node, OPTNode): return []
        # child is empty
        if node.children[0].get_text() == '':
            return [(node, None)]
        else:
            return []

    @classmethod
    def apply(cls, state, info):
        roots, _, hashs = state
        node, _ = info
        reverse = [node, None]

        new_node = node.children[0]
        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            reverse[1] = cls.update_root(roots, node, new_node)
        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
        hashs.pop()
        return state

class FixedMulti(Rule):

    @classmethod
    def test(cls, state, node):
        roots, _, _ = state
        # node is any
        if not isinstance(node, ANYNode): return []
        # childen are ASTNode with the same role
        delim = None
        for i in range(len(node.children)):
            if not isinstance(node.children[i], ListNode): return []
            if node.children[i].delim:
                if delim and delim != node.children[i].delim: return []
                delim = node.children[i].delim
            if node.children[i].rule != node.children[0].rule: return []
        # delim is determined
        if delim is None: return []
        children = []
        for c in node.children:
            children += c.children
        # at least two different children
        if len(set([c.chash() for c in children])) < 2: return []
        # childen's children are ALL the same role
        for c in children:
            if c.rule != children[0].rule: return []
        return [(node, delim)]

    @classmethod
    def apply(cls, state, info):
        roots, _, hashs = state
        node, delim = info
        reverse = [node, None]

        nodes = {}
        for c in node.children:
            for ch in c.children:
                hs = ch.chash()
                nodes.setdefault(hs, [])
                nodes[hs].append(ch)
        children = []
        for chchs in nodes.values():
            children.append(chchs[0] if len(chchs) == 1 else cls.merge(chchs))
        new_node = FXMULTINode(children, node.children[0].rule, delim)

        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            reverse[1] = cls.update_root(roots, node, new_node)
        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
        for c in node.children:
            for i, cc in enumerate(c.children):
                cc.parent = c
                cc.crank = i
        hashs.pop()
        return state

class Multi(Rule):

    @classmethod
    def test(cls, state, node):
        roots, _, _ = state
        # root is fixedmulti
        if isinstance(node, FXMULTINode):
            return [(node, None)]
        else:
            return []

    @classmethod
    def apply(cls, state, info):
        roots, _, hashs = state
        node, _ = info
        reverse = [node, None]
        new_node = _any_node(node.children)
        new_node = MULTINode([new_node], node.rule, node.delim)
        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            reverse[1] = cls.update_root(roots, node, new_node)

        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
        hashs.pop()
        return state

class MergeAny(Rule):

    @classmethod
    def test(cls, state, node):
        roots, _, _ = state
        # node is any
        if not isinstance(node, ANYNode): return []
        # childen are any
        for i in range(len(node.children)):
            if isinstance(node.children[i], ANYNode): return [(node, None)]
        return []

    @classmethod
    def apply(cls, state, info):
        roots, _, hashs = state
        node, _ = info
        reverse = [node, None]

        distinct_children = {}
        for c in node.children:
            if isinstance(c, ANYNode):
                for ch in c.children:
                    hs = ch.chash()
                    distinct_children.setdefault(hs, [])
                    distinct_children[hs].append(ch)
            else:
                hs = c.chash()
                distinct_children.setdefault(hs, [])
                distinct_children[hs].append(c)
        children = []
        for chchs in distinct_children.values():
            children.append(chchs[0] if len(chchs) == 1 else cls.merge(chchs))
        new_node = _any_node(children)
        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            reverse[1] = cls.update_root(roots, node, new_node)
        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
        for c in node.children:
            for i, cc in enumerate(c.children):
                cc.parent = c
                cc.crank = i
        hashs.pop()
        return state

class Merge(Rule):

    @classmethod
    def test(cls, state, _):
        roots, schemas, _ = state
        cands = []
        for i, root in enumerate(roots):
            schema = schemas[i]
            for j in range(i + 1, len(roots)):
                if schema is not None and schemas[j] is not None and schemas[j] == schema:
                    cands.append((i, j))
        return cands

    @classmethod
    def apply(cls, state, info):
        roots, schemas, hashs = state
        i, j = info
        reverse = (i, j)

        new_node = _any_node([roots[i], roots[j]])
        roots.pop(j)
        roots.pop(i)
        roots.append(new_node)
        schemas.pop(j)
        sch = schemas.pop(i)
        schemas.append(sch)

        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, schemas, hashs = state
        i, j = reverse
        node = roots[-1]
        sch = schemas[-1]
        roots.pop()
        schemas.pop()
        ra, rb = node.children[0], node.children[1]
        ra.parent = None
        rb.parent = None
        roots.insert(i, ra)
        roots.insert(j, rb)
        schemas.insert(i, sch)
        schemas.insert(j, sch)
        hashs.pop()
        return state

class Split(Rule):

    @classmethod
    def split(cls, node, queries):
        new_node = copy(node)
        new_node.domain = set([])
        new_node.visit_ts = set([])
        new_node.nid = Node.next_id()
        new_node.history = []

        if isinstance(node, LiteralNode):
            if node.queries & queries:
                new_node.queries = node.queries & queries
                return new_node
            else:
                return None
        else:
            new_children = []
            new_queries = set()
            for c in node.children:
                ch = cls.split(c, queries)
                if ch is not None:
                    new_children.append(ch)
                    new_queries |= ch.queries
            if new_children:
                if isinstance(new_node, OPTNode) and new_queries == queries:
                    return new_children[0]
                else:
                    new_node.children = new_children
                    new_node.queries = new_queries
                    for i, c in enumerate(new_children):
                        c.parent = new_node
                        c.crank = i
                    return new_node
            else:
                return None

    @classmethod
    def test(cls, state, node):
        roots, schemas, _ = state
        cands = []
        # split option
        if isinstance(node, OPTNode):
            query_a = node.queries
            root = node
            while root.parent:
                if isinstance(root.parent, ChoiceNode):
                    return []
                root = root.parent
            for i in range(len(roots)):
                if roots[i] == root:
                    query_b = roots[i].queries - query_a
                    if query_a and query_b:
                        cands.append((query_a, query_b, i))
        return cands

    @classmethod
    def apply(cls, state, info):
        roots, schemas, hashs = state
        query_a, query_b, i = info
        sch = schemas[i]
        reverse = (roots[i], sch, i)

        roota, rootb = cls.split(roots[i], query_a), cls.split(roots[i], query_b)
        roots.pop(i)
        schemas.pop(i)
        roots.append(roota)
        roots.append(rootb)
        schemas.append(sch)
        schemas.append(sch)

        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, schemas, hashs = state
        root, sch, i = reverse

        roots.pop()
        roots.pop()
        schemas.pop()
        schemas.pop()
        roots.insert(i, root)
        schemas.insert(i, sch)

        hashs.pop()
        return state

class OptPushDownList(Rule):

    @classmethod
    def test(cls, state, node):
        roots, _, _ = state
        if isinstance(node, OPTNode) and isinstance(node.children[0], ListNode):
            return [(node, None)]
        else:
            return []

    @classmethod
    def apply(cls, state, info):
        roots, _, hashs = state
        node, _ = info
        reverse = [node, None]

        children = []
        lst = node.children[0]
        for c in lst.children:
            children.append(OPTNode([c]))
        new_node = ListNode(children, lst.delim, lst.rule)
        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            reverse[1] = cls.update_root(roots, node, new_node)
        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
        for c in node.children:
            for i, cc in enumerate(c.children):
                cc.parent = c
                cc.crank = i
        hashs.pop()
        return state

class OptPushDownAST(Rule):

    @classmethod
    def test(cls, state, node):
        roots, _, _ = state
        if isinstance(node, OPTNode) and isinstance(node.children[0], ASTNode):
            chs = None
            for i, c in enumerate(node.children[0].children):
                if not cls.is_static(c):
                    if chs is not None: return []
                    chs = i
            if chs is not None:
                return [(node, chs)]
            else:
                return []
        else:
            return []

    @classmethod
    def apply(cls, state, info):
        roots, _, hashs = state
        node, i = info
        reverse = [node, None]

        children = []
        ast = node.children[0]
        for c in ast.children:
            children.append(c)
        children[i] = OPTNode([children[i]])
        new_node = ASTNode(children, ast.rule)
        new_node = CoOPTNode([new_node])
        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            reverse[1] = cls.update_root(roots, node, new_node)
        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
        for c in node.children:
            for i, cc in enumerate(c.children):
                cc.parent = c
                cc.crank = i
        hashs.pop()
        return state

class Partition(Rule):

    @classmethod
    def test(cls, state, node):
        roots, _, _ = state
        # node is any
        if not isinstance(node, ANYNode): return []
        # childen are in different rules
        rules = dict()
        for i in range(len(node.children)):
            if isinstance(node.children[i], ChoiceNode): return []
            rule = node.children[i].rule
            if not rule: return []
            rules.setdefault(rule, [])
            rules[rule].append(node.children[i])
        if len(rules) == 1: return []
        return [(node, rules)]

    @classmethod
    def apply(cls, state, info):
        roots, _, hashs = state
        node, rules = info
        reverse = [node, None]

        children = []
        for rule, chs in rules.items():
            children.append(_any_node(chs))
        new_node = _any_node(children)
        new_node.parent = node.parent
        new_node.crank = node.crank
        if node.parent is not None:
            node.parent.children[node.crank] = new_node
        else:
            reverse[1] = cls.update_root(roots, node, new_node)
        hashs.append(hash(tuple([t.chash() for t in roots])))
        return state, reverse

    @classmethod
    def restore(cls, state, reverse):
        roots, _, hashs = state
        node, ith = reverse
        if node.parent is None:
            roots[ith] = node
        else:
            node.parent.children[node.crank] = node
        for i, c in enumerate(node.children):
            c.parent = node
            c.crank = i
        hashs.pop()
        return state

rule_list = [
    PushDownAny,
    NoopANY,
    NoopOPT,
    FixedMulti,
    Multi,
    MergeAny,
    Merge,
    Split,
    OptPushDownAST,
    OptPushDownList,
    Partition
]
