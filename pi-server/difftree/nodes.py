node_id = 0

class Node(object):

    @classmethod
    def next_id(cls):
        global node_id
        _id = node_id
        node_id += 1
        return 'n' + str(_id)

    def __init__(self, children):
        self.children = children
        self.text = ""
        self.nid = self.next_id()
        self.parent = None
        self.crank = None  # self is the crank'th child of its parent
        self.rule = None
        self.node_schema = None
        self.domain = set([])
        self.typ = None
        self.difftree = None
        self.widget = None
        self.last_choice = None
        self.visit_ts = set()
        self.depth = max([0] + [c.depth for c in self.children]) + 1
        self.queries = set()
        for c in self.children:
            self.queries |= c.queries

        for i, c in enumerate(children):
            c.parent = self
            c.crank = i

    # content hash: hash the subtree and the content of the subtree
    # choice node does not have rule, AST node and literal node has its rules.
    def chash(self):
        child_hash = tuple([c.chash() for c in self.children])
        return hash((child_hash, self.__class__))

    def ntype(self):
        return "node"

    def get_text(self):
        if self.children:
            return "".join([c.get_text() for c in self.children])
        else:
            return self.text or ""


    def print(self, indent=0):
        widget = "" if self.widget is None else "# " + self.widget.wtype() + " #"
        print(("|    " * indent) + str(self.nid) + " " + self.ntype() + f"[{self.rule}]" + " " + (
            repr(self.node_schema) if self.node_schema is not None else repr(self.typ)) + widget + " " + str(self.queries))
        for c in self.children:
            c.print(indent + 1)

    def to_spec(self):
        spec = {}
        spec["id"] = self.nid
        spec["type"] = self.ntype()
        spec["value"] = self.text if isinstance(self, LiteralNode) else None
        spec["children"] = []
        if hasattr(self, "delim"):
            spec["delim"] = self.delim
        for c in self.children:
            spec["children"].append(c.to_spec())
        return spec

    def __str__(self):
        return self.get_text()

    def __repr__(self):
        return self.get_text()


class LiteralNode(Node):

    def __init__(self, rule, text, qids):
        super(LiteralNode, self).__init__([])
        self.rule = rule
        self.text = text
        self.queries = set(qids)

    def chash(self):
        return hash((self.rule, self.text, self.__class__))

    def ntype(self):
        return "literal"

    def print(self, indent=0):
        #if self.text.strip():
            print(("|    " * indent) + self.ntype() + f"({self.text.strip()})[{self.rule}]" + " " + str(self.typ) + " " + str(self.queries))


class ASTNode(Node):

    def __init__(self, children, rule):
        super(ASTNode, self).__init__(children)
        self.rule = rule

    def chash(self):
        child_hash = tuple([c.chash() for c in self.children])
        return hash((self.rule, child_hash, self.__class__))

    def get_text(self):
        ch = [c.get_text() for c in self.children]
        ch = list(filter(lambda s: s, ch))
        return " ".join(ch)

    def ntype(self):
        return "ast"


class ListNode(ASTNode):

    def __init__(self, children, delim, rule):
        super(ListNode, self).__init__(children, rule)
        self.delim = delim

    def chash(self):
        child_hash = tuple([c.chash() for c in self.children])
        return hash((self.rule, self.delim, child_hash, self.__class__))

    def get_text(self):
        return (self.delim or "").join([c.get_text() for c in self.children])

    def ntype(self):
        return "list"


class ChoiceNode(Node):

    def __init__(self, children):
        super(ChoiceNode, self).__init__(children)
        self.history = []

    def ntype(self):
        return "choice"


class ANYNode(ChoiceNode):

    def __init__(self, children, default=None):
        super(ANYNode, self).__init__(children)
        self.rule = children[0].rule
        self.default = default

    def get_text(self):
        return "any(" + "|\n".join([c.get_text() for c in self.children]) +\
            " : default = " + (self.default.get_text() if self.default else "N/A") + ")"

    def get_children(self):
        return [c.get_text() for c in self.children]

    def ntype(self):
        return "any"


class VALUENode(ChoiceNode):

    def __init__(self, children):
        super(VALUENode, self).__init__(children)

    def ntype(self):
        return "value"


class CoOPTNode(ChoiceNode):

    def __init__(self, children):
        super(CoOPTNode, self).__init__(children)

    def get_text(self):
        return "coopt(" + "|\n".join([c.get_text() for c in self.children]) + ")"

    def ntype(self):
        return "co-optional"


class OPTNode(ChoiceNode):

    def __init__(self, children, default=None):
        super(OPTNode, self).__init__(children)
        self.default = default

    def get_text(self):
        return "opt(" + "|\n".join([c.get_text() for c in self.children]) +\
            " : default = " + (self.default.get_text() if self.default else "N/A") + ")"

    def ntype(self):
        return "optional"


class FXMULTINode(ChoiceNode):

    def __init__(self, children, rule, delim):
        super(FXMULTINode, self).__init__(children)
        self.rule = rule
        self.delim = delim

    def get_text(self):
        return "fxmt(" + "|\n".join([c.get_text() for c in self.children]) + ")"

    def ntype(self):
        return "fixedmulti"


class MULTINode(ChoiceNode):

    def __init__(self, children, rule, delim, default=None):
        super(MULTINode, self).__init__(children)
        self.rule = rule
        self.delim = delim
        self.default = default

    def get_text(self):
        return "mt(" + "|\n".join([c.get_text() for c in self.children]) + ")"

    def ntype(self):
        return "multi"
