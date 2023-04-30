from difftree.nodes import *
from interface.visualizations import *

class Difftree(object):

    tree_id = 0

    def __init__(self, root, catalog, queries, sample_outputs):
        self.tid =  't' + str(Difftree.tree_id)
        Difftree.tree_id += 1
        self.root = root
        self.bind_all_nodes(self.root)
        self.catalog = catalog
        self.queries = list([q for q, _ in queries])
        self.sample_outputs = sample_outputs

        self.data_source = None
        self.choices = []
        self.unique_schemas = {}
        self.infer_schema(self.root)

        self.visit_ts = 0
        for q, i in queries:
            dom = self.infer_domain(self.root, q, i)

        self.select_content = []
        self.infer_sql_schema(self.root)

        self.vis = None

    def bind_all_nodes(self, node):
        for c in node.children:
            self.bind_all_nodes(c)
        node.difftree = self

    def infer_schema(self, node):
        node.node_schema = None
        # bottom-up infer schema
        for c in node.children:
            self.infer_schema(c)

        if isinstance(node, ASTNode):
            # AST.schema = child_1.schema ++ child_2.schema ++ ...
            schemas = []
            for c in node.children:
                if c.node_schema:
                    if isinstance(c.node_schema, ListSchema):
                        schemas += c.node_schema.schema_list
                    else:
                        schemas.append(c.node_schema)
            if schemas:
                if len(schemas) == 1:
                    node.node_schema = schemas[0]
                else:
                    node.node_schema = ListSchema(schemas)
            elif node.typ is None:
                # fill in missing types
                types = list([c.typ for c in node.children if c.typ.type != EType.NONE])
                if len(types) == 1:
                    node.typ = types[0]
                else:
                    node.typ = Type(EType.AST)

            # data_source
            rule = eval(node.rule) if node.rule.startswith("[") and node.rule.endswith("]") else [node.rule]
            if set(rule) & set(['gb_clause', 'source_func', 'source_subq']):
                self.data_source = "__unknown__"
            elif 'source_table' in rule:
                table = node.get_text().split(" as ")[0]
                if self.data_source is None:
                    self.data_source = table
                elif self.data_source != table:
                    self.data_source = "__unknown__"

        elif isinstance(node, ANYNode):
            types = []
            schemas = []
            for c in node.children:
                if c.typ is not None:
                    types.append(c.typ)
                else:
                    schemas.append(c.node_schema)
            typ = None
            if types:
                typ = types[0]
                for t in types[1:]:
                    typ = typ.lca(t)
            if schemas:
                for typ in types:
                    schemas.append(TypeSchema(typ, None))
                node.node_schema = OrSchema(schemas, node)
            else:
                node.node_schema = TypeSchema(typ, node)
            self.choices.append(node)

        elif isinstance(node, VALUENode):
            # schema = children.types.lca
            typ = node.children[0].typ
            for c in node.children[1:]:
                if typ.type == EType.NONE:
                    typ = c.typ
                else:
                    typ = typ.lca(c.typ)
            node.node_schema = TypeSchema(typ, node)
            self.choices.append(node)

        elif isinstance(node, OPTNode):
            if node.children[0].node_schema is None:
                typ = deepcopy(node.children[0].typ)
                node.node_schema = OptionSchema(TypeSchema(typ, None), node)
            else:
                node.node_schema = OptionSchema(node.children[0].node_schema, node)
            self.choices.append(node)

        elif isinstance(node, CoOPTNode):
            node.node_schema = node.children[0].node_schema

        elif isinstance(node, FXMULTINode):
            schemas = []
            for c in node.children:
                if c.node_schema:
                    schemas.append(OptionSchema(c.node_schema, node))
                else:
                    schemas.append(OptionSchema(TypeSchema(c.typ, None), node))
            node.node_schema = ListSchema(schemas)
            self.choices.append(node)

        elif isinstance(node, MULTINode):
            if node.children[0].node_schema is None:
                typ = deepcopy(node.children[0].typ)
                node.node_schema = StarSchema(TypeSchema(typ, None), node)
            else:
                node.node_schema = StarSchema(node.children[0].node_schema, node)
            self.choices.append(node)

        # get the deepest unique schema
        if node.node_schema is not None and node.node_schema.shash() not in self.unique_schemas:
            self.unique_schemas[node.node_schema.shash()] = node

    def clear_optional(self, node, qidx):
        if isinstance(node, OPTNode):
            if node.last_choice != 0:
                node.last_choice = 0
                node.visit_ts.add((qidx, self.visit_ts))
                self.visit_ts += 1
        else:
            for c in node.children:
                self.clear_optional(c, qidx)

    def cardinality(self, c):
        card = set()
        for out in self.sample_outputs:
            out = out.get_by_col_ids([c])
            out = set(map(lambda c: c[0], out))
            card |= out
        return len(card)

    def infer_domain(self, node, query, qidx):
        if isinstance(node, LiteralNode):
            return None

        elif isinstance(node, ASTNode):
            vals = []
            for node_c, query_c in zip(node.children, query.children):
                if not query_c.get_text():
                    continue
                val = self.infer_domain(node_c, query_c, qidx)
                if val is not None:
                    if isinstance(val, tuple):
                        vals += list(val)
                    else:
                        vals.append(val)
            # assume there must be optional nodes
            for c in node.children[len(query.children):]:
                self.clear_optional(c, qidx)

            if vals:
                node.domain.add(tuple(vals))
                return tuple(vals)
            else:
                return None

        elif isinstance(node, ANYNode):
            print("ANYNode.get_text():", node.get_text())
            if isinstance(node.node_schema, TypeSchema):
                text = query.get_text()
                node.domain.add(text)
                node.history.append((text, qidx))
            else:
                text = None
                for i, c in enumerate(node.children):
                    if qidx in c.queries:
                        text = i
                        node.domain.add(i)
                        node.history.append((i, qidx))
                        self.infer_domain(c, query, qidx)
            if text is not None and node.last_choice != text:
                node.visit_ts.add((qidx, self.visit_ts))
                self.visit_ts += 1
                node.last_choice = text

            return text

        elif isinstance(node, VALUENode):
            text = query.get_text()
            node.domain.add(text)
            node.history.append((text, qidx))
            if node.last_choice != text:
                node.visit_ts.add((qidx, self.visit_ts))
                self.visit_ts += 1
                node.last_choice = text
            return text

        elif isinstance(node, OPTNode):
            val = self.infer_domain(node.children[0], query, qidx)
            node.domain.add(val)
            node.history.append((val, qidx))
            if node.last_choice != 1:
                node.last_choice = 1
                node.visit_ts.add((qidx, self.visit_ts))
                self.visit_ts += 1
            return val

        elif isinstance(node, CoOPTNode):
            val = self.infer_domain(node.children[0], query, qidx)
            node.domain.add(val)
            node.history.append((val, qidx))
            return val

        elif isinstance(node, FXMULTINode):
            vals = []
            # assume fxmulti's chilren are all static nodes
            for c in query.children:
                vals.append(c.get_text())
            val = tuple(vals)
            node.domain.add(val)
            node.history.append((val, qidx))
            node.visit_ts.add((qidx, self.visit_ts))
            self.visit_ts += 1
            return val

        elif isinstance(node, MULTINode):
            vals = []
            for c in query.children:
                node.visit_ts.add((qidx, self.visit_ts))
                self.visit_ts += 1
                val = self.infer_domain(node.children[0], c, qidx)
                if isinstance(val, tuple):
                    vals += list(val)
                else:
                    vals.append(val)
            val = tuple(vals)
            node.domain.add(val)
            node.history.append((val, qidx))
            return val

    def infer_sql_schema(self, node):

        # infer one query's SQLSchema
        def _infer(node, schema, content):
            if isinstance(node, ASTNode):
                rule = eval(node.rule) if node.rule.startswith("[") and node.rule.endswith("]") else [node.rule]
                if set(rule) & set(['from_clause', 'where_clause', 'gb_clause', 'having_clause']):
                    return []
                if 'select_result' in rule:
                    # get the last item if there is an AS
                    c = node.get_text().split(" as ")

                    content.append(c[-1])

                    schema.append(node.typ)

                else:
                    for c in node.children:
                        _infer(c, schema, content)

        schemas = []
        contents = []
        for q in self.queries:
            q_schema, q_content = [], []
            _infer(q, q_schema, q_content)
            schemas.append(q_schema)
            contents.append(q_content)

        schema = []
        content = []
        for ss in zip(*schemas):
            item = ss[0]

            for s in ss:
                item = item.lca(s)
            schema.append(SQLSchemaItem(item))

        for cc in zip(*contents):
            content.append("/".join(list(set(cc))))

        self.select_content = content
        self.sql_schema = SQLSchema(schema)

    def default_query(self, node, query):
        for c in node.children:
            self.default_query(c, query)

        if isinstance(node, ANYNode):
            query[str(node.nid)] = [0]

        elif isinstance(node, OPTNode):
            query[str(node.nid)] = [0]

        elif isinstance(node, FXMULTINode):
            query[str(node.nid)] = [0]

        elif isinstance(node, MULTINode):
            query[str(node.nid)] = []

        return query

    def to_spec(self, backend):
        spec = {}

        spec["id"] = f"difftree_{self.tid}"
        spec["type"] = "difftree"
        spec["difftree"] = self.root.to_spec()
        spec["backend"] = backend
        return spec
