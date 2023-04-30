import sqlite3
import pandas as pd


class Backend:
    pass


class DB(Backend):

    def __init__(self, dburi):
        self.dburi = dburi

    def to_sql(self, q):
      return q

    def query(self, q):
        print(q)
        db = sqlite3.connect(self.dburi)
        data = pd.read_sql_query(q, db)
        cols = data.columns
        rows = []
        for index, row in data.iterrows():
            d = {}
            visit_time = dict()
            for i, c in enumerate(cols):
                visit_time.setdefault(c, -1)
                visit_time[c] += 1
                if isinstance(row[c], pd.core.series.Series):
                    d[c] = str(row[c][visit_time[c]])
                    d[f"${i}"] = str(row[c][visit_time[c]])
                else:
                    d[c] = str(row[c])
                    d[f"${i}"] = str(row[c])
            rows.append(d)
        print(rows[0] if rows else "null")
        return rows

class Node:
    NODE = 0
    LITERAL = 1
    AST = 2
    CHOICE = 3
    ANY = 4
    VALUE = 5
    OPT = 6
    CoOPT = 7
    FXMT = 8
    MULTI = 9
    LIST = 10
    to_type = {
        "node": NODE,
        "literal": LITERAL,
        "ast": AST,
        "choice": CHOICE,
        "any": ANY,
        "value": VALUE,
        "optional": OPT,
        "co-optional": CoOPT,
        "fixedmulti": FXMT,
        "multi": MULTI,
        "list": LIST
    }

    def __init__(self, bid, typ, value, children, delim):
        self.id = bid
        self.type = self.to_type[typ]
        self.value = value
        self.children = children
        self.delim = delim or ""

    def max_num(self, node, binding):
        mn = list([self.max_num(c, binding) for c in node.children])
        mn.append(len(binding[node.id]) if node.id in binding else 0)
        return max(mn)

    def find_optional(self, node):
        if node.type == self.OPT:
            yield node
        else:
            for c in node.children:
                for op in self.find_optional(c):
                    yield op

    def to_query(self, binding, ids="", num=0, selected=True):
        if self.type == Node.AST:
            sub_queries = list(map(lambda n: n.to_query(binding, ids, num), self.children))
            return " ".join(sub_queries)

        if self.type == Node.LIST:
            sub_queries = list(map(lambda n: n.to_query(binding, ids, num), self.children))
            return (" " + self.delim + " ").join(filter(lambda s: len(s) > 0, sub_queries))

        elif self.type == self.LITERAL:
            return self.value

        elif self.type == self.ANY:
            choice = binding[self.id][num]
            if choice == "inf":
                return '9e999'
            elif choice == "-inf":
                return '-9e999'
            if isinstance(choice, int):
                if self.id in ids and selected:
                    return "~$" + self.children[choice].to_query(binding, ids, num) + "$~"
                return self.children[choice].to_query(binding, ids, num)
            else:
                try:
                    choice = str(int(choice))
                except:
                    try:
                        choice = str(float(choice))
                    except:
                        choice = "'" + choice + "'"
                if self.id in ids and selected:
                    return "~$" + choice + "$~"
                return choice

        elif self.type == self.OPT:
            choice = binding[self.id][num]
            if choice in [1, "selected"]:
                if self.id in ids:
                    return "~$" + self.children[0].to_query(binding, ids, num, False) + "$~"
                return self.children[0].to_query(binding, ids, num)
            else:
                return ""

        elif self.type == self.CoOPT:
            show = False
            for c in self.find_optional(self):
                if binding[c.id][num] in [1, "selected"]:
                    show = True
            if not show:
                return ""
            else:
                if self.id in ids:
                    return "~$" + self.children[0].to_query(binding, ids, num, False) + "$~"
                return self.children[0].to_query(binding, ids, num)

        elif self.type == self.FXMT:
            sub_queries = []
            for i in binding[self.id]:
                sub_queries.append(self.children[i].to_query(binding, ids, num))
            return (" " + self.delim + " ").join(sub_queries)

        elif self.type == self.MULTI:
            sub_queries = []
            for n in range(self.max_num(self, binding)):
                sub_queries.append(self.children[0].to_query(binding, ids, n))
            return (" " + self.delim + " ").join(sub_queries)

        else:
            # TODO: other cases?
            return str(self.value)


class DiffTree(Backend):

    def parse_tree(self, root):
        children = list(map(lambda n: self.parse_tree(n), root["children"]))
        if root["id"] in self.node_map:
            node = self.node_map[root["id"]]
        else:
            node = Node(root["id"], root["type"], root["value"], children, root.get("delim", ""))
            self.node_map[root["id"]] = node
        return node

    def __init__(self, root, db):
        self.node_map = {}
        self.tree = self.parse_tree(root)
        self.db = db
        self.last_query = ""

    def to_sql(self, binding):
      return self.tree.to_query(binding)

    def query(self, binding, ids=None):
        if ids is None:
            self.last_query = self.tree.to_query(binding)
        else:
            self.last_query = self.tree.to_query(binding, ids)
        return self.db.query(self.tree.to_query(binding))

    def to_preview(self, binding, ids):
        return self.tree.to_query(binding, ids)


class Engine:

    def parse_backend(self, spec):
        for back in spec["backends"]:
            bid = back["id"]
            typ = back["type"]
            if typ == "db":
                self.backends[bid] = DB(back["dburi"])
            elif typ == "difftree":
                db = self.backends[back["backend"]]
                self.backends[bid] = DiffTree(back["difftree"], db)
            else:
                print("backend not implemented:", bid, typ)

    def __init__(self, spec):
        self.backends = {}
        self.parse_backend(spec)
        print("$" * 80)
        print(" " * 80)
        print("Cost : ", spec["cost"])
        print(" " * 80)
        print("$" * 80)

    def to_sql(self, q):
      return self.backends[q["backend"]].to_sql(q['binding'])

    def query(self, q):
        print(q)
        if len(q['ids']) > 0:
            return self.backends[q["backend"]].query(q["binding"], q['ids'])
        else:
            return self.backends[q["backend"]].query(q["binding"])

    def to_preview(self, q):
        '''
        Similar to to_sql() but passes in array of node ids where something was changed by a widget
        :param q: query object
        :return: query string with delimiters around changed area (for identification)
        '''

        return self.backends[q["backend"]].to_preview(q['binding'], q['ids'])
