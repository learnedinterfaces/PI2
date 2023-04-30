import enum
from copy import deepcopy


class EType(enum.Enum):
    NONE = 0
    NUMBER = 1
    STRING = 2
    TEMPORAL = 3
    AST = 4
    ADVANCED = 5
    GEOJSON = 6


class Type:

    def __init__(self, type, agg=False, attr=None, table=None, ctype=None, lca_list=[]):
        '''
            type = EType.ADVANCED, ctype is the fundamental type
            type = fundamental type, ctype == type.
        '''
        self.type = type
        self.ctype = ctype or type
        self.agg = agg
        self.lca_list = lca_list
        self.attr = attr
        self.table = table

    def __eq__(self, other):
        if self.type != other.type: return False
        if self.agg != other.agg: return False
        if self.type == EType.ADVANCED:
            if self.attr != other.attr: return False
            if self.table != other.table: return False
            if self.ctype != other.ctype: return False
        return True

    def lca(self, other):
        if other.type == EType.NONE:
            return deepcopy(self)
        if self.type == EType.NONE:
            return deepcopy(other)
        if self == other:
            return deepcopy(self)
        agg = self.agg and other.agg
        typ1 = self.ctype if self.type == EType.ADVANCED else self.type
        typ2 = other.ctype if other.type == EType.ADVANCED else other.type
        compat = {EType.NUMBER: {EType.NUMBER},
                  EType.TEMPORAL: {EType.TEMPORAL},
                  EType.STRING: {EType.NUMBER, EType.STRING},
                  EType.GEOJSON: {EType.GEOJSON},
                  EType.AST: {EType.NUMBER, EType.STRING, EType.AST, EType.TEMPORAL, EType.GEOJSON}}
        for typ in [EType.NUMBER, EType.STRING, EType.AST, EType.TEMPORAL, EType.GEOJSON]:
            if typ1 in compat[typ] and typ2 in compat[typ]:
                break
        T = Type(typ, agg)
        T.lca_list = [self, other] + self.lca_list + other.lca_list
        Ts = {}
        for t in T.lca_list:
            Ts[(t.type, t.attr, t.table)] = t
        T.lca_list = list(Ts.values())

        return T

    @classmethod
    def to_str(self, typ):
        return {EType.NONE: "none", EType.NUMBER: "num", EType.STRING: "str", EType.TEMPORAL: "temporal", EType.GEOJSON: "geojson", EType.AST: "ast", EType.ADVANCED: "advance"}[typ]

    def __str__(self):
        return {True: "agg-", False: ""}[self.agg] + self.to_str(self.type) + \
               (("-" + str(self.table) + "-" + str(self.attr) + "-" + self.to_str(
                   self.ctype)) if self.type == EType.ADVANCED else "")

    def __repr__(self):
        return str(self)

'''
([b, [a, c]?] | c* )
= 
OrSchema (
    [ListSchema(
     [TypeSchema(b),
         OptionSchema(
            [TypeSchema(a),
             TypeSchema(c)])]),
    StarSchema(TypeSchema(c))]

)
'''
class Schema(object):
    pass

# A
class TypeSchema(Schema):

    def __init__(self, typ, node=None):
        self.type = typ
        self.node = node

    def __eq__(self, other):
        if isinstance(other, TypeSchema):
            return self.type.ctype == other.type.ctype
        else:
            return False

    def compatible(self, other):
        if self.type.type == EType.AST:
            return isinstance(other, Schema)
        else:
            if isinstance(other, TypeSchema):
                return self.type.lca(other.type) == self.type
            else:
                return False

    def shash(self):
        return hash((TypeSchema, self.node))

    def __str__(self):
        return  "{" + str(self.type) + "}"

    def __repr__(self):
        return "{" + repr(self.type) + "}"


# [A B]
class ListSchema(Schema):

    def __init__(self, schema_list):
        self.schema_list = schema_list

    def __eq__(self, other):
        if isinstance(other, ListSchema):
            if len(self.schema_list) == len(other.schema_list):
                for a, b in zip(self.schema_list, other.schema_list):
                    if a != b:
                        return False
                return True
            else:
                return False
        else:
            return False

    def compatible(self, other):
        if isinstance(other, ListSchema):
            if len(self.schema_list) == len(other.schema_list):
                for a, b in zip(self.schema_list, other.schema_list):
                    if not a.compatible(b):
                        return False
                return True
            else:
                return False
        else:
            return False

    def shash(self):
        return hash(tuple([c.shash() for c in self.schema_list]))

    def __str__(self):
        return "[" + (" ".join([str(c) for c in self.schema_list])) + "]"

    def __repr__(self):
        return "[" + (" ".join([str(c) for c in self.schema_list])) + "]"

# A*
class StarSchema(Schema):

    def __init__(self, sub_schema, node=None):
        self.sub_schema = sub_schema
        self.node = node

    def __eq__(self, other):
        if isinstance(other, StarSchema):
            self_schema = self.sub_schema
            node_schema = other.sub_schema
            while True:
                if type(node_schema) != type(self_schema):
                    return False
                if isinstance(node_schema, TypeSchema):
                    return node_schema.type.ctype == self_schema.type.ctype
                elif isinstance(node_schema, ListSchema):
                    return node_schema == self_schema
                elif isinstance(node_schema, StarSchema):
                    node_schema = node_schema.sub_schema
                    self_schema = self.schema.sub_schema
                elif isinstance(node_schema, OptionSchema):
                    return node_schema == self_schema
                elif isinstance(node_schema, OrSchema):
                    return node_schema == self_schema
        else:
            return False

    def compatible(self, other):
        if isinstance(other, StarSchema):
            return self.sub_schema.compatible(other.sub_schema)
        else:
            return False

    def shash(self):
        return hash((StarSchema, self.sub_schema.shash(), self.node))

    def __str__(self):
        return str(self.sub_schema) + "*"

    def __repr__(self):
        return str(self.sub_schema) + "*"

# A?
class OptionSchema(Schema):

    def __init__(self, sub_schema, node=None):
        self.sub_schema = sub_schema
        self.node = node

    def __eq__(self, other):
        if isinstance(other, OptionSchema):
            return self.sub_schema == other.sub_schema
        else:
            return False

    def compatible(self, other):
        if isinstance(other, OptionSchema):
            return self.sub_schema.compatible(other.sub_schema)
        else:
            return False

    def shash(self):
        return hash((OptionSchema, self.sub_schema.shash(), self.node))

    def __str__(self):
        return str(self.sub_schema) + "?"

    def __repr__(self):
        return str(self.sub_schema) + "?"


# (A|B)
class OrSchema(Schema):

    def __init__(self, schema_list, node=None):
        self.schema_list = schema_list
        self.node = node

    def __eq__(self, other):
        if isinstance(other, OrSchema):
            if len(self.schema_list) == len(other.schema_list):
                for a, b in zip(self.schema_list, other.schema_list):
                    if a != b:
                        return False
                return True
            else:
                return False
        else:
            return False

    def compatible(self, other):
        if isinstance(other, OrSchema):
            if len(self.schema_list) == len(other.schema_list):
                for a, b in zip(self.schema_list, other.schema_list):
                    if not a.compatible(b):
                        return False
                return True
            else:
                return False
        else:
            return False

    def shash(self):
        return hash((OrSchema, self.node))


class SQLSchemaItem(object):

    def __init__(self, type):
        self.type = type

    def __eq__(self, other):
        return self.type == other.type

    def __str__(self):
        return str(self.type)

    def __repr__(self):
        return repr(self.type)


class SQLSchema(object):

    def __init__(self, items):
        self.items = items

    def __str__(self):
        return str(self.items)

    def __repr__(self):
        return repr(self.items)

    def __eq__(self, other):
        if len(self.items) != len(other.items): return False
        for a, b in zip(self.items, other.items):
            if a != b: return False
        return True

    def __str__(self):
        return "(" + ("|".join([str(c) for c in self.schema_list])) + ")"

    def __repr__(self):
        return "(" + ("|".join([str(c) for c in self.schema_list])) + ")"
