from interface.widgets import *
from interface.interaction import *


class Visualization(Layout):

    def __init__(self, difftree, encoding):
        super().__init__()
        self.difftree = difftree
        self.encoding = encoding
        self.m = None
        self.x = 0
        self.y = 0

    def push_xy(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def candidate_encodings(cls, difft):
        projs = list([t.type for t in difft.sql_schema.items])
        func_deps = difft.catalog.get_functional_dependencies()
        catalog = difft.catalog

        # projs: [Type]
        # func_deps: [((x, u, v, w), y)]

        candidates = []

        #transform type to quantitative, ordinal, temporary
        vis_variable = []
        for t in range(len(projs)):
            vis_variable.append([])
            if projs[t].type == EType.ADVANCED:
                vis_variable[t].append(catalog.get_attribute_field(projs[t].attr))
                if projs[t].ctype == EType.NUMBER and difft.cardinality(t) < 20:
                    vis_variable[t].append('ordinal')
            elif projs[t].type == EType.NUMBER:
                vis_variable[t].append('quantitative')
                if difft.cardinality(t) < 20:
                    vis_variable[t].append('ordinal')
            elif projs[t].type == EType.STRING:
                vis_variable[t].append('ordinal')
            elif projs[t].type == EType.TEMPORAL:
                vis_variable[t].append('temporal')
            elif projs[t].type == EType.GEOJSON:
                vis_variable[t].append('geojson')
       

        def _gen_mapping(cur_mapping, remain_attrs):
            nonlocal projs, candidates
            if len(remain_attrs) == 0:
                required_satisfied = True
                for a in cls.attributes:
                    if a not in cur_mapping and cls.attributes[a][0] == "required":
                        required_satisfied = False
                if required_satisfied:
                        mapping = {}
                        for k, v in cur_mapping.items():
                            mapping[k] = (projs[v], v)
                        if cls.test_dependency(mapping, func_deps):
                            candidates.append(mapping)
            else:
                s, rem = remain_attrs[0], remain_attrs[1:]

                for a in cls.attributes:
                    if a in cur_mapping: continue

                    # key is the index of the table, key is mapped only when index is selected in the sqlschema.
                    if (a != "key" and (set(cls.attributes[a][1]) & set(vis_variable[s]))) or\
                       (a == "key" and difft.data_source != "__unknown__" and projs[s].type == EType.ADVANCED and\
                            catalog.get_table_index(difft.data_source) == difft.select_content[s]):
                        cur_mapping[a] = s
                        _gen_mapping(cur_mapping, rem)
                        del cur_mapping[a]

        _gen_mapping({}, list(range(len(projs))))

        return candidates

    def candidate_interactions(self):
        interacts = []
        for mtype, mspace, names, types, cons in self.manipulations:
            '''
            data space interaction but data source is unknown 
                eg. the from clause is a subquery 
                eg. it is from multiple tables. 
            '''
            if mspace == MSpace.DATA and self.difftree.data_source == "__unknown__":
                continue
            schema = []
            '''
            construct candidate interaction's schema and domain
            interaction requires all the schema to be advanced type
            '''
            alladvanced = True
            for name, typ in zip(names, types):
                if typ == EType.ADVANCED:
                    if name == "__index__":
                        # deal with index for the connect use case.
                        attr = self.difftree.catalog.get_table_index(self.difftree.data_source)
                        typ = self.difftree.catalog.get_attribute_type(attr, self.difftree.data_source)
                    else:
                        dim = self.event_table[name]
                        if dim in self.encoding:
                            typ = deepcopy(self.encoding[dim][0])
                            if typ.type != EType.ADVANCED:
                                alladvanced = False
                                break
                else:
                    alladvanced = False
                    break
                schema.append(TypeSchema(typ))
            if not alladvanced: continue

            if len(schema) == 1:
                schema = schema[0]
            else:
                schema = ListSchema(schema)
            if cons == "*":
                schema = StarSchema(schema)
            if cons == "?":
                schema = OptionSchema(schema)

            domain = set()
            results = self.difftree.sample_outputs
            try:
                for result in results:
                    dims = tuple([self.encoding[self.event_table[name]][1] for name in names])
                    domain |= result.get_by_col_ids(dims)
                interacts.append(Interaction(self, mtype, mspace, names, schema, domain))
            except:
                pass
        return interacts

    def to_spec(self):
        spec = {}

        spec["id"] = str(self.vid)
        spec["type"] = self.name
        spec["data"] = {"backend": f"difftree_{self.difftree.tid}",
                        "query": self.difftree.default_query(self.difftree.root, {})}
        spec["mapping"] = {}
        for v, i in self.encoding.items():
            spec["mapping"][v] = f"${i[1]}"

        spec['schema'] = {}
        for v, i in self.encoding.items():
            if i[0].type == EType.ADVANCED:
                spec['schema'][v] = Type.to_str(i[0].ctype)
            else:
                spec['schema'][v] = Type.to_str(i[0].type)

        spec["label"] = {}
        for v, i in self.encoding.items():
            spec["label"][v] = self.difftree.select_content[i[1]]

        if hasattr(self, "width"):
          spec['width'] = self.width - 10
        if hasattr(self, "height"):
          spec['height'] = self.height - 10
        return spec

    def get_text(self):
        text = self.name + "(" + ",".join([(v + ":" + self.difftree.select_content[i[1]]) for v, i in self.encoding.items()]) + ")"
        return text

    def layout_to_spec(self):
        spec = {}
        spec["id"] = str(self.vid)
        spec["width"] = self.width
        spec["height"] = self.height
        spec["type"] = "ref"
        spec["ref"] = str(self.vid)
        return spec


class Bar(Visualization):
    attributes = {
        "x": ("required", ["ordinal"]),
        "y": ("required", ["quantitative"]),
        "color": ("optional", ["ordinal"]),
        "key": ("optional", ["ordinal"]),
    }

    manipulations = [
        (MType.SINGLE, MSpace.MARK, ("x",), (EType.ADVANCED,), "1"),
        (MType.SINGLE, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "1"),
        (MType.MULTI, MSpace.MARK, ("x",), (EType.ADVANCED,), "*"),
        (MType.BRUSHX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
    ]

    event_table = {
        "x": "x",
        "xmin": "x",
        "xmax": "x",
        "__index__": "key",
    }

    def __init__(self, difftree, encoding):
        super(Bar, self).__init__(difftree, encoding)


    def wtype(self):
        return "Bar"

    @property
    def name(self):
        return "Bar"

    @property
    def height(self):
        return 300

    @property
    def width(self):
        return 600

    @property
    def cost(self):
        return 300


    @classmethod
    def test_dependency(cls, mapping, func_deps):
        y = mapping["y"]
        if y[0].type != EType.ADVANCED:
            if y[0].lca_list == []:
                return False
            else:
                for _y in y[0].lca_list:
                    mapping['y'] = (_y, y[1])
                    if not cls.test_dependency(mapping, func_deps):
                        mapping['y'] = y
                        return False
                mapping['y'] = y
                return True

        if y[0].agg:
            return True

        others = set([(t[0].table, t[0].attr) for t in mapping.values() if t[0].type == EType.ADVANCED]) - {(y[0].table, y[0].attr)}
        for keys, target in func_deps:
            if (target.table, target.attr) == (y[0].table, y[0].attr) and set([(t.table, t.attr) for t in keys]).issubset(others):
                return True
        return False


class Line(Visualization):
    attributes = {
        "x": ("required", ["quantitative", 'temporal']),
        "y": ("required", ["quantitative"]),
        "color": ("optional", ["ordinal"]),
        "key": ("optional", ["ordinal"]),
    }

    manipulations = [
        (MType.SINGLE, MSpace.MARK, ("x",), (EType.ADVANCED,), "1"),
        (MType.SINGLE, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "1"),
        (MType.BRUSHX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
    ]

    event_table = {
        "x": "x",
        "xmin": "x",
        "xmax": "x",
        "y": "y",
        "ymin": "y",
        "ymax": "y",
        "__index__": "key",
    }


    def __init__(self, difftree, encoding):
        super(Line, self).__init__(difftree, encoding)

    def wtype(self):
        return 'Line'

    @property
    def name(self): return "Line"

    @property
    def height(self): return 300

    @property
    def width(self): return 600

    @property
    def cost(self):
        return 300


    @classmethod
    def test_dependency(cls, mapping, func_deps):
        y = mapping["y"]
        if y[0].type != EType.ADVANCED:
            if y[0].lca_list == []:
                return False
            else:
                for _y in y[0].lca_list:
                    mapping['y'] = (_y, y[1])
                    if not cls.test_dependency(mapping, func_deps):
                        mapping['y'] = y
                        return False
                mapping['y'] = y
                return True

        '''
            if y[0].agg, then aggregate function as the y axis, always return True. 
            limitation: if there are multiple aggregation in project clause, may not always be true. 
        '''
        if y[0].agg:
            return True

        others = set([(t[0].table, t[0].attr) for t in mapping.values() if t[0].type == EType.ADVANCED]) - {(y[0].table, y[0].attr)}
        for keys, target in func_deps:
            if (target.table, target.attr) == (y[0].table, y[0].attr) and set([(t.table, t.attr) for t in keys]).issubset(others):
                return True
        return False


class Point(Visualization):
    attributes = {
        "x": ("required", ["quantitative", 'temporal']),
        "y": ("required", ["quantitative"]),
        "color": ("optional", ["ordinal"]),
        "key": ("optional", ["ordinal"])
    }

    manipulations = [
        (MType.SINGLE, MSpace.MARK, ("x",), (EType.ADVANCED,), "1"),
        (MType.SINGLE, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "1"),
        (MType.MULTI, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "*"),
        (MType.BRUSHX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.BRUSHY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.BRUSHXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
    ]

    event_table = {
        "x": "x",
        "xmin": "x",
        "xmax": "x",
        "y": "y",
        "ymin": "y",
        "ymax": "y",
        "__index__": "key",
    }

    def __init__(self, difftree, encoding):
        super(Point, self).__init__(difftree, encoding)


    def wtype(self):
        return 'Point'

    @property
    def name(self): return "Point"


    @property
    def cost(self):
        return 500

    @property
    def height(self):
        return 300

    @property
    def width(self):
        return 600

    @classmethod
    def test_dependency(cls, mapping, func_deps):
        return True


class Circle(Visualization):
    attributes = {
        "x": ("required", ["quantitative", 'temporal']),
        "y": ("required", ["quantitative"]),
        "color": ("optional", ["ordinal"]),
        "key": ("optional", ["ordinal"])
    }

    manipulations = [
        (MType.SINGLE, MSpace.MARK, ("x",), (EType.ADVANCED,), "1"),
        (MType.SINGLE, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "1"),
        (MType.MULTI, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "*"),
        (MType.BRUSHX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.BRUSHY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.BRUSHXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
    ]

    event_table = {
        "x": "x",
        "xmin": "x",
        "xmax": "x",
        "y": "y",
        "ymin": "y",
        "ymax": "y",
        "__index__": "key",
    }

    def __init__(self, difftree, encoding):
        super(Circle, self).__init__(difftree, encoding)


    def wtype(self):
        return 'Circle'

    @property
    def name(self): return "Circle"


    @property
    def cost(self):
        return 500

    @property
    def height(self):
        return 300

    @property
    def width(self):
        return 600

    @classmethod
    def test_dependency(cls, mapping, func_deps):
        return True


class Square(Visualization):
    attributes = {
        "x": ("required", ["quantitative", 'temporal']),
        "y": ("required", ["quantitative"]),
        "color": ("optional", ["ordinal"]),
        "key": ("optional", ["ordinal"])
    }

    manipulations = [
        (MType.SINGLE, MSpace.MARK, ("x",), (EType.ADVANCED,), "1"),
        (MType.SINGLE, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "1"),
        (MType.MULTI, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "*"),
        (MType.BRUSHX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.BRUSHY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.BRUSHXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
    ]

    event_table = {
        "x": "x",
        "xmin": "x",
        "xmax": "x",
        "y": "y",
        "ymin": "y",
        "ymax": "y",
        "__index__": "key",
    }

    def __init__(self, difftree, encoding):
        super(Square, self).__init__(difftree, encoding)


    def wtype(self):
        return 'Square'

    @property
    def name(self): return "Square"


    @property
    def cost(self):
        return 500

    @property
    def height(self):
        return 300

    @property
    def width(self):
        return 600

    @classmethod
    def test_dependency(cls, mapping, func_deps):
        return True


class Area(Visualization):
    attributes = {
        "x": ("required", ["quantitative", 'temporal']),
        "y": ("required", ["quantitative"]),
        "color": ("optional", ["ordinal"]),
        "key": ("optional", ["ordinal"]),
    }

    manipulations = [
        (MType.SINGLE, MSpace.MARK, ("x",), (EType.ADVANCED,), "1"),
        (MType.SINGLE, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "1"),
        (MType.BRUSHX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.BRUSHY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.BRUSHXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.PANXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMX, MSpace.MARK, ("xmin", "xmax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMY, MSpace.MARK, ("ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED), "1"),
        (MType.ZOOMXY, MSpace.MARK, ("xmin", "xmax", "ymin", "ymax"), (EType.ADVANCED, EType.ADVANCED, EType.ADVANCED, EType.ADVANCED), "1"),
    ]

    event_table = {
        "x": "x",
        "xmin": "x",
        "xmax": "x",
        "y": "y",
        "ymin": "y",
        "ymax": "y",
        "__index__": "key",
    }

    def __init__(self, difftree, encoding):
        super(Area, self).__init__(difftree, encoding)

    def wtype(self):
        return 'Area'

    @property
    def name(self): return "Area"

    @property
    def height(self): return 300

    @property
    def width(self): return 600

    @property
    def cost(self):
        return 400


    @classmethod
    def test_dependency(cls, mapping, func_deps):
        y = mapping["y"]
        if y[0].type != EType.ADVANCED:
            if y[0].lca_list == []:
                return False
            else:
                for _y in y[0].lca_list:
                    mapping['y'] = (_y, y[1])
                    if not cls.test_dependency(mapping, func_deps):
                        mapping['y'] = y
                        return False
                mapping['y'] = y
                return True

        '''
            if y[0].agg, then aggregate function as the y axis, always return True. 
            limitation: if there are multiple aggregation in project clause, may not always be true. 
        '''
        if y[0].agg:
            return True

        others = set([(t[0].table, t[0].attr) for t in mapping.values() if t[0].type == EType.ADVANCED]) - {(y[0].table, y[0].attr)}
        for keys, target in func_deps:
            if (target.table, target.attr) == (y[0].table, y[0].attr) and set([(t.table, t.attr) for t in keys]).issubset(others):
                return True
        return False

class Geoshape(Visualization):
    attributes = {
        "geography": ("required", ["geojson"]),
        "color": ("optional", ["quantitative", "ordinal"]),
        "key": ("optional", ["ordinal"])
    }

    manipulations = [
        (MType.SINGLE, MSpace.MARK, ("color",), (EType.ADVANCED,), "1"),
        (MType.MULTI, MSpace.MARK, ("color",), (EType.ADVANCED,), "*"),
        (MType.SINGLE, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "1"),
        (MType.MULTI, MSpace.DATA, ("__index__",), (EType.ADVANCED,), "*"),
    ]

    event_table = {
        "geography": "geography",
        "color": "color",
        "__index__": "key",
    }

    def __init__(self, difftree, encoding):
        super(Geoshape, self).__init__(difftree, encoding)


    def wtype(self):
        return 'Geoshape'

    @property
    def name(self): return "Geoshape"


    @property
    def cost(self):
        return 400

    @property
    def height(self):
        return 300

    @property
    def width(self):
        return 600

    @classmethod
    def test_dependency(cls, mapping, func_deps):
        return True


class Table(Visualization):

    def __init__(self, difftree, encoding):
        super(Table, self).__init__(difftree, encoding)

    def wtype(self):
        return "Table"

    @property
    def name(self): return "Table"

    @property
    def height(self):
        sample_max_rows = max([len(out.data) for out in self.difftree.sample_outputs])
        if sample_max_rows == 1:
            return 70
        else:
            return sample_max_rows * 20 + 500

    @property
    def width(self):
        sample_max_cols = max([len(out.data.columns) for out in self.difftree.sample_outputs])
        if sample_max_cols == 1 : 
            return 150
        else: 
            return sample_max_cols * 60

    @property
    def cost(self):
        return 500

    @classmethod
    def candidate_encodings(cls, difft):
        projs = list([t.type for t in difft.sql_schema.items])

        enc = {}
        for i, p in enumerate(projs):
            enc[f"${i}"] = (p, i)
        return [enc]

    def candidate_interactions(self):
        return []


Visualizations = [
    Bar,
    Line,
    Point,
    Circle,
    Square,
    Area,
    Geoshape,
    Table
]


def candidate_visualizations(difft):
    candidates = []

    for vis in Visualizations:
        if vis == Table and len(candidates) > 0:
            continue

        for enc in vis.candidate_encodings(difft):
            candidates.append((vis, enc))

    return candidates
