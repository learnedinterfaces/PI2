from parsimonious.grammar import Grammar
from difftree.nodes import ASTNode, LiteralNode, ListNode
from difftree.schema import *


class PIParser:

    # initialize a parsimonious parse
    def __init__(self, grammar_file, catalog):
        self.grammar = Grammar("".join(open(grammar_file).readlines()))
        self.catalog = catalog

    def find_delim(self, node):
        if node.expr.name == "AND":
            return " AND "
        elif node.expr.name == "OR":
            return " OR "
        else:
            for c in node.children:
                d = self.find_delim(c)
                if d is not None: return d
            return None

    def find_components(self, node):
        if node.expr.name == "expr":
            yield node
        else:
            for c in node.children:
                for n in self.find_components(c):
                    yield n

    # recursively convert a parsimonious tree to a AST tree
    def to_ast(self, node, qid):
        if not node.children:
            node = LiteralNode(node.expr.name, node.text, [qid])
        elif node.expr.name == "listexpr":
            delim = ","
            children = list([self.to_ast(n, qid) for n in self.find_components(node)])
            node = ListNode(children, delim, "expr_list")
            children = [LiteralNode("lparen", "(", [qid])] + [node] + [LiteralNode("rparen", ")", [qid])]
            node = ASTNode(children, "listexpr")
        elif node.expr.name == "where_list":
            delim = self.find_delim(node) or None
            children = list([self.to_ast(n, qid) for n in self.find_components(node)])
            node = ListNode(children, delim, "where_list")
        else:
            children = [self.to_ast(n, qid) for n in node.children]
            node = ASTNode(children, node.expr.name)
        return node

    # parse a string
    def parse(self, s, qid):
        root = self.grammar.parse(s.strip())
        root = self.to_ast(root, qid)
        self.infer_types(root)
        return root

    def infer_types(self, root):

        info = {}
        info["tables"] = {}
        info["in_from_clause"] = False
        # 1: infer table name
        self.infer_type_from_clause(root, info)
        info["in_col_ref"] = False
        # 2: infer column name which is in the catalog
        self.infer_type_col_ref(root, info)
        # 3: bottom up collect the type.
        self.infer_type_collect_type(root)
        # 4: broadcast the type
        self.infer_type_broadcast(root, None)

    def infer_type_from_clause(self, node, info):
        if isinstance(node, LiteralNode):
            if info["in_from_clause"]:
                node.typ = Type(EType.NONE)
        elif isinstance(node, ASTNode):
            if node.rule == "single_source":
                names = node.get_text().split("as")
                if len(names) == 1:
                    name = names[0].strip()
                    info["tables"][name] = None
                else:
                    name = names[0].strip()
                    alias = names[1].strip()
                    info["tables"][alias] = name
                info["in_from_clause"] = True
            for c in node.children:
                self.infer_type_from_clause(c, info)
            if node.rule == "single_source":
                info["in_from_clause"] = False

    def infer_type_col_ref(self, node, info):
        '''
        Infer advanced type
        '''
        if isinstance(node, LiteralNode):
            if info["in_col_ref"]:
                '''
                For any table_name, attr_name, table_name <> attr_name
                '''
                if node.text in info['tables'].keys():
                    info["attr_table"] = info['tables'][node.text] or node.text
                    node.typ = Type(EType.NONE)
                elif self.catalog.is_attribute(node.text):
                    attr = node.text
                    table = info["attr_table"]
                    if table is None:
                        for table in info["tables"]:
                            table = info['tables'][table] or table
                            node.typ = self.catalog.get_attribute_type(attr, table) or node.typ
                    else:
                        node.typ = self.catalog.get_attribute_type(attr, table)
                else:
                    node.typ = Type(EType.NONE)
        elif isinstance(node, ASTNode):
            if node.rule == "col_ref":
                info["in_col_ref"] = True
                info["attr_table"] = None
            for c in node.children:
                self.infer_type_col_ref(c, info)
            if node.rule == "col_ref":
                info["in_col_ref"] = False

    def infer_type_collect_type(self, node, in_expr=False):
        '''
            propagate type from bottom to up in expr scope shown in the ()

                  node2
                 (None)
                /   |   \
             node1  +    node3
             (a)         (b)
            /  |        /  |
            a + 1      b + 1
           (a)        (b)

        '''
        if isinstance(node, ASTNode):
            if node.rule == "expr":
                in_expr = True
            node.typ = None
            for c in node.children:
                self.infer_type_collect_type(c, in_expr)
                if in_expr:
                    '''
                    children's: c.typ has been inferred and is not None.
                    if all children are of the same type, then parent has the same type 
                    else node.type is None (unknown) 
                    '''
                    if c.typ is not None and c.typ.type != EType.NONE:
                        if node.typ is None:
                            node.typ = c.typ
                        elif node.typ != c.typ:
                            node.typ = Type(EType.NONE)

    def infer_type_broadcast(self, node, typ):
        '''
            after bottom up inferring the type, broadcast the type--typ heritaged from it parent
             to node in a top to bottom manner.
            last step: reassign the internal node by bottom up inference again.
        '''
        if isinstance(node, LiteralNode):
            # left, right parenthesis and function name does not have a type
            if node.rule in ['fname', 'lparen', 'rparen', 'binary_nontext_op', 'binary_text_op']:
                node.typ = Type(EType.NONE)
            if node.text.strip() == "":
                node.typ = Type(EType.NONE)
            if node.typ is None:
                # parent has type
                if typ is not None and typ.type != EType.NONE:
                    node.typ = typ
                else:
                    if node.rule == "number":
                        node.typ = Type(EType.NUMBER)
                    elif node.rule == "string":
                        node.typ = Type(EType.STRING)
                    else:
                        node.typ = Type(EType.NONE)

        elif isinstance(node, ASTNode):

            if node.typ is not None:
                '''
                 choose the local type( node1 should be of type a instead of None) 
                    
                  node2
                 (None)
                /   |   \     
             node1  +    node3       
             (a)         (b)   
            /  |        /  |  
            a + 1      b + 1
           (a)        (b)   
                '''

                typ = node.typ
            types = []
            for c in node.children:
                self.infer_type_broadcast(c, typ)
                if c.typ.type != EType.NONE:
                    types.append(c.typ)

            if node.rule == 'arg_expr' and node.get_text() == '*':
                # solve the count(*) or sum(*) case
                node.typ = Type(EType.ADVANCED, attr="agg(*)", table="", ctype=EType.NUMBER)
            # operator 'in': type number
            elif node.rule == 'biexpr' and 'in' in set(node.get_text().split(' ')):
                '''
                   biexpr
                    (num)
                 /   |    |
                id   in   listexpr
               (id) (string) (id)
                          /  |  |
                        ( 1, 2, 3 )
                            (id)

                '''
                # in will return 0 or 1
                node.typ = Type(EType.NUMBER)
            elif node.rule == 'biexpr' and len(node.children) == 3 and node.children[1].get_text().strip() in ["+", "-", "*", "/"]:
                '''
                   biexpr
                    (num)
                 /    |    |
                X   (+-*/) y
               (num) (string)   (num)
              '''
                # in will return 0 or 1
                node.typ = Type(EType.NUMBER)
            elif node.rule in set(('sel_res_val', 'sel_res_col')) and 'as' in set(node.get_text().split(' ')):
                node.typ = types[0]
            elif len(types) == 0:
                node.typ = Type(EType.NONE)
            elif len(types) == 1:
                node.typ = types[0]
                # sum(sales)
                '''
                    function 
                    agg = True, type = (sales) 
                    /  |   |  |
                 sum (  sales  )  
                None   (sales)
                '''

                if node.rule == "function":
                    node.typ.agg = True
            else:
                for t in types:
                    if t.type != EType.ADVANCED or t.attr != self.catalog.get_table_index(t.table):
                        node.typ = Type(EType.AST)
                        if node.rule == "function":
                            node.typ.agg = True
                        return
                # every attribute are advanced type -- id
                # limitation: id could be two or more table's id
                node.typ = types[0]
                if node.rule == "function":
                    node.typ.agg = True
