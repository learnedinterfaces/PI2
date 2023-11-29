from ast import AST
from difftree.nodes import *
from interface.visualizations import *
from difftree.difftree import Difftree
import random

def json_to_difftree(obj, catalog, db):
    tree = to_difftree(obj, catalog, db)
    assert(isinstance(tree, ASTNode) and tree.children[-1].get_text() == "<EOF>")
    tree.children = tree.children[:-1]
    table_info = infer_table(tree)
    convert_domain(tree, table_info, catalog, db)
    infer_type(tree, catalog)
    queries, sample_outputs = sample_queries(tree, catalog, db)
    difft = Difftree(tree, catalog, queries, sample_outputs)
    if len(table_info.values()) == 1:
        difft.data_source = list(table_info.values())[0]
    else:
        difft.data_source = "__unknown__"
    return difft

def is_number(s):
    """ Returns True is string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False

def find_nodes(node, rule):
    if isinstance(node, ASTNode) and rule in eval(node.rule):
        yield node
    else:
        if isinstance(node, (ASTNode, ChoiceNode)):
            for c in node.children:
                for n in find_nodes(c, rule):
                    yield n

def convert_range(range_children):
    range = list(find_nodes(range_children[0], "number"))
    begin = str(range[0])
    end = str(range[1])
    if "." in begin or "." in end:
        # is float
        begin, end = float(begin), float(end)
    else:
        # is int
        begin, end = int(begin), int(end)
    return [LiteralNode("number", str(begin), []), LiteralNode("number", str(end), [])]

def to_difftree(obj, catalog, db):
    if "children" in obj:
        children = [to_difftree(c, catalog, db) for c in obj["children"]]
    else:
        children = []

    if obj["node_type"] == "ast":
        return ASTNode(children, str(obj["rule"]))
    elif obj["node_type"] == "choice":
        if obj["choice_node_type"] == "Any":
            if len(children) == 1 and "range" == eval(children[0].rule)[-1]:
                children = convert_range(children)
            if obj["default"]:
                default = to_difftree(obj["default"], catalog, db)
                return ANYNode(children, default)
            else:
                return ANYNode(children)
        elif obj["choice_node_type"] == "Optional":
            if obj["default"]:
                default = to_difftree(obj["default"], catalog, db)
                return OPTNode(children, default)
            else:
                return OPTNode(children)
        elif obj["choice_node_type"] == "Multi":
            return MULTINode(children, obj["rule"], obj["delim"])
        else:
            assert(obj["choice_node_type"] == "Subset")
            return FXMULTINode(children, obj["rule"], obj["delim"])
    elif obj["node_type"] == "terminal":
        text = obj["text"]
        rule = "number" if is_number(text) else "string"
        return LiteralNode(rule, text, [])

def infer_table(tree):
    # TODO: support subquery and any{table_names}
    from_cl = list(find_nodes(tree, "source_table"))

    info = {}
    for src in from_cl:
        table = str(list(find_nodes(src, "name"))[0])
        if len(src.children) == 2:
            alias = str(list(find_nodes(src.children[1], "name"))[0])
        else:
            alias = table
        info[alias] = table
    
    return info

def convert_domain(node, table_info, catalog, db):
    if isinstance(node, ANYNode):
        children = node.children
        if len(children) == 1 and "domain" == eval(children[0].rule)[-1]:
            col = list(find_nodes(node.children[0], "col_ref"))[0]
            if len(col.children) == 2:
                table = str(list(find_nodes(col.children[0], "name"))[0])
                assert(table in table_info)
                table = table_info[table]
                attr = str(list(find_nodes(col.children[1], "name"))[0])
            else:
                assert(len(table_info) == 1)
                table = list(table_info.values())[0]
                attr = str(list(find_nodes(col, "name"))[0])
            res = db.execute(f"select {attr} from {table}")
            res = sorted(list(res.data[attr].unique()))
            node.children = [LiteralNode("number" if is_number(r) else "string", f"'{r}'", []) for r in res]
    else:
        if isinstance(node, (ASTNode, ChoiceNode)):
            for c in node.children:
                convert_domain(c, table_info, catalog, db)

def infer_type(tree, catalog):
    info = {}
    info["tables"] = {}
    info["in_from_clause"] = False
    # 1: infer table name
    infer_type_from_clause(tree, info)
    info["in_col_ref"] = False
    # 2: infer column name which is in the catalog
    infer_type_col_ref(tree, info, catalog)
    # 3: bottom up collect the type.
    infer_type_collect_type(tree)
    # 4: broadcast the type
    infer_type_broadcast(tree, None, catalog)

def infer_type_from_clause(node, info):
    if isinstance(node, LiteralNode):
        if info["in_from_clause"]:
            node.typ = Type(EType.NONE)
    elif isinstance(node, ASTNode):
        if "single_source" in eval(node.rule):
            names = node.get_text().split(" as ")
            if len(names) == 1:
                name = names[0].strip()
                info["tables"][name] = None
            else:
                name = names[0].strip()
                alias = names[1].strip()
                info["tables"][alias] = name
            info["in_from_clause"] = True
        for c in node.children:
            infer_type_from_clause(c, info)
        if "single_source" in eval(node.rule):
            info["in_from_clause"] = False

def infer_type_col_ref(node, info, catalog):
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
            elif catalog.is_attribute(node.text):
                attr = node.text
                table = info["attr_table"]
                if table is None:
                    for table in info["tables"]:
                        table = info['tables'][table] or table
                        node.typ = catalog.get_attribute_type(attr, table) or node.typ
                else:
                    node.typ = catalog.get_attribute_type(attr, table)
            else:
                node.typ = Type(EType.NONE)
    elif isinstance(node, (ASTNode, ChoiceNode)):
        if isinstance(node, ASTNode) and "col_ref" in eval(node.rule):
            info["in_col_ref"] = True
            info["attr_table"] = None
        for c in node.children:
            infer_type_col_ref(c, info, catalog)
        if isinstance(node, ASTNode) and "col_ref" in eval(node.rule):
            info["in_col_ref"] = False

def infer_type_collect_type(node, in_expr=False):
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
    if isinstance(node, (ASTNode, ChoiceNode)):
        if isinstance(node, ASTNode) and "expr" in eval(node.rule):
            in_expr = True
        node.typ = None
        for c in node.children:
            infer_type_collect_type(c, in_expr)
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

def infer_type_broadcast(node, typ, catalog):
    '''
        after bottom up inferring the type, broadcast the type--typ heritaged from it parent
            to node in a top to bottom manner.
        last step: reassign the internal node by bottom up inference again.
    '''
    if isinstance(node, LiteralNode):
        # left, right parenthesis and function name does not have a type
        if node.text in ['(', ')',  '+' , '-' , '*' , '/' , '==' , '=' , '<>' , '!=' , '<=' , '>=' , '<' , '>' , 
                         'like' , 'LIKE', 'and', 'AND', 'or', 'OR', 'count', 'sum', 'min', 'max']:
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

    elif isinstance(node, (ASTNode, ChoiceNode)):
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
            infer_type_broadcast(c, typ, catalog)
            if c.typ.type != EType.NONE:
                types.append(c.typ)

        if isinstance(node, ASTNode) and 'arg_list' in eval(node.rule) and node.get_text() == '*':
            # solve the count(*) or sum(*) case
            node.typ = Type(EType.ADVANCED, attr="agg(*)", table="", ctype=EType.NUMBER)
        # operator 'in': type number
        elif isinstance(node, ASTNode) and 'biexpr' in eval(node.rule) and node.children[1].get_text().lower() == "in":
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
        elif isinstance(node, ASTNode) and 'biexpr' in eval(node.rule) and node.children[1].get_text().strip() in ["+", "-", "*", "/"]:
            '''
                biexpr
                (num)
                /    |    |
            X   (+-*/) y
            (num) (string)   (num)
            '''
            # in will return 0 or 1
            node.typ = Type(EType.NUMBER)
        elif isinstance(node, ASTNode) and set(eval(node.rule)) & set(('sel_res_val', 'sel_res_col')):
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

            if isinstance(node, ASTNode) and "function" in eval(node.rule):
                node.typ.agg = True
        else:
            for t in types:
                if t.type != EType.ADVANCED or t.attr != catalog.get_table_index(t.table):
                    node.typ = Type(EType.AST)
                    if isinstance(node, ASTNode) and "function" in eval(node.rule):
                        node.typ.agg = True
                    return
            # every attribute are advanced type -- id
            # limitation: id could be two or more table's id
            node.typ = types[0]
            if isinstance(node, ASTNode) and "function" in eval(node.rule):
                node.typ.agg = True

def sample_node(node, qid, history, choices):
    node.queries.add(qid)
    if isinstance(node, ChoiceNode):
        history.setdefault(node.nid, set())
        choices.setdefault(node.nid, set())
        if isinstance(node, ANYNode):
            if len(history[node.nid] | choices[node.nid]) == len(node.children):
                c = random.randint(0, len(node.children)-1)
                choices[node.nid].add(c)
                return sample_node(node.children[c], qid, history, choices)
            else:
                c = random.sample(set(range(0, len(node.children))) - history[node.nid] - choices[node.nid], 1)[0]
                choices[node.nid].add(c)
                return sample_node(node.children[c], qid, history, choices)
        elif isinstance(node, OPTNode):
            if len(history[node.nid] | choices[node.nid]) == 2:
                c = random.randint(0, 1)
                choices[node.nid].add(c)
                if c == 1:
                    return sample_node(node.children[0], qid, history, choices)
                else:
                    return LiteralNode("string", "", [])
            else:
                c = random.sample(sorted(set([0,1]) - history[node.nid] - choices[node.nid]), 1)[0]
                choices[node.nid].add(c)
                if c == 1:
                    return sample_node(node.children[0], qid, history, choices)
                else:
                    return LiteralNode("string", "", [])
        elif isinstance(node, FXMULTINode):
            if len(history[node.nid] | choices[node.nid]) == len(node.children):
                c = random.randint(0, len(node.children)-1)
                choices[node.nid].add(c)
                return sample_node(node.children[c], qid, history, choices)
            else:
                c = random.sample(sorted(set(range(0, len(node.children))) - history[node.nid] - choices[node.nid]), 1)[0]
                choices[node.nid].add(c)
                ret = ASTNode([sample_node(node.children[c], qid, history, choices)], node.rule)
        elif isinstance(node, MULTINode):
            choices[node.nid].add(1)
            ret = ASTNode([sample_node(node.children[0], qid, history, choices)], node.rule)
    elif isinstance(node, LiteralNode):
        ret = LiteralNode(node.rule, node.text, [])
    else:
        children = [sample_node(c, qid, history, choices) for c in node.children]
        ret = ASTNode(children, node.rule)
    return ret

def remain(node, history):
    rem = 0
    if isinstance(node, ChoiceNode):
        rem += sum([remain(c, history) for c in node.children])
        if isinstance(node, ANYNode):
            rem += len(node.children) - len(history.get(node.nid, []))
        elif isinstance(node, OPTNode):
            rem += 2 - len(history[node.nid])
        elif isinstance(node, FXMULTINode):
            rem += len(node.children) - len(history.get(node.nid, []))
        elif isinstance(node, MULTINode):
            rem += 1 - len(history.get(node.nid, []))
    elif isinstance(node, LiteralNode):
        return 0
    else:
        rem += sum([remain(c, history) for c in node.children])
    return rem

def clear_node(node, qid):
    if isinstance(node, (ASTNode, ChoiceNode)):
        for c in node.children:
            clear_node(c, qid)
    if qid in node.queries:
        node.queries.remove(qid)


def sample_queries(tree, catalog, db):
    history = {}

    queries = []
    sample_outputs = []

    qid = 1
    num_retries = 1000000
    while remain(tree, history) > 0:
        num_retries -= 1
        assert(num_retries > 0)
        choices = {}
        #tree.print()
        sample = sample_node(tree, qid, history, choices)
        infer_type(sample, catalog)
        query = sample.get_text()
        try:
            out = db.execute(query)
        except:
            raise Exception("invalid sample query " + query)

        queries.append((sample, qid))
        sample_outputs.append(out)
        for nid in choices:
            history[nid] |= choices[nid]
        qid += 1
    return queries, sample_outputs
