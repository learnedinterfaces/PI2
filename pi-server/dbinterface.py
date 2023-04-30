import sqlite3
import pandas as pd
import sqlalchemy as sa
from difftree.schema import *
from sqlalchemy import create_engine


class Result:
    def __init__(self, data):
        self.data = data

    '''
    input: (idx_1, idx_2, ...)
    output: { (content_1, content_2, ...) }
    '''
    def get_by_col_ids(self, cols):
        data = []
        for c in cols:
            data.append(tuple(self.data[self.data.columns[c]]))
        data = set([tuple(map(repr, d)) for d in zip(*data)])
        return data


class Database:
    def __init__(self, path_to_db):
        self.db = sqlite3.connect(path_to_db)

    def execute(self, query):
        data = pd.read_sql_query(query, self.db)
        return Result(data)


class Catalogue:
    def __init__(self):
        pass

    def get_attribute_domain(self, attr, table=None, db=None):
        # return a list
        pass

    def get_attribute_type(self, attr, table=None, db=None):
        pass

    def get_table_index(self, table):
        pass

    def is_table(self, name):
        pass

    def is_attribute(self, name):
        pass

    def ord_or_quant(self, typ):
        pass

'''
schema of the car table 
CREATE TABLE IF NOT EXISTS "cars" (
    "index" INTEGER,
      "Name" TEXT,
      "Miles_per_Gallon" REAL,
      "Cylinders" INTEGER,
      "Displacement" REAL,
      "Horsepower" REAL,
      "Weight_in_lbs" INTEGER,
      "Acceleration" REAL,
      "Year" TEXT,
      "Origin" TEXT
    );
'''



class TestCatalogue(Catalogue):
    '''
    TODO:
      ordinal inference: if varchar or if the cardinarlity is < 10,
      quantitative: int, float
  '''

    def __init__(self):
        self.tables = {}

        self.tables["flights"] = \
            {"hour": (EType.NUMBER, "ordinal"),
             "bin_delay": (EType.NUMBER, "quantitative"),
             "bin_distance": (EType.NUMBER, "quantitative"),
             "idx": (EType.NUMBER, "quantitative")}
        self.tables["galaxy"] = \
            {"objID": (EType.NUMBER, "ordinal"),
             "u": (EType.NUMBER, "quantitative"),
             "g": (EType.NUMBER, "quantitative"),
             "r": (EType.NUMBER, "quantitative"),
             "i": (EType.NUMBER, "quantitative"),
             "z": (EType.NUMBER, "quantitative")}
        self.tables["specObj"] = \
            {"bestObjID": (EType.NUMBER, "ordinal"),
             "z": (EType.NUMBER, "quantitative"),
             "ra": (EType.NUMBER, "quantitative"),
             "dec": (EType.NUMBER, "quantitative")}
        self.tables["sales"] = \
            {"date": (EType.TEMPORAL, "temporal"),
             "city": (EType.STRING, "ordinal"),
             "product_line": (EType.STRING, "ordinal"),
             "total": (EType.NUMBER, "quantitative"),
             "branch": (EType.STRING, "ordinal")}
        self.tables["cars"] = \
            {"Name": (EType.STRING, "ordinal"),
             "Miles_per_Gallon": (EType.NUMBER, "quantitative"),
             "Cylinders": (EType.NUMBER, "quantitative"),
             "Displacement": (EType.STRING, "quantitative"),
             "Horsepower": (EType.NUMBER, "quantitative"),
             "Weight_in_lbs": (EType.NUMBER, "quantitative"),
             "Acceleration": (EType.NUMBER, "quantitative"),
             "Year": (EType.NUMBER, "quantitative"),
             "Origin": (EType.STRING, "ordinal"),
             "Idx": (EType.NUMBER, "key")}
        self.tables["sp500"] = \
            {"date": (EType.TEMPORAL, "temporal"),
             "price": (EType.NUMBER, "quantitative")}
        self.tables["covid"] = \
            {"date": (EType.TEMPORAL, "temporal"),
             "cases": (EType.NUMBER, "quantitative"),
             "cases_raw": (EType.NUMBER, "quantitative"),
             "cases_avg": (EType.NUMBER, "quantitative"),
             "deaths": (EType.NUMBER, "quantitative"),
             "state": (EType.STRING, "ordinal")}
        self.tables["regions"] = \
            {"region": (EType.STRING, "ordinal"),
             "state": (EType.STRING, "ordinal")}
        self.tables["idebench"] = \
            {"CARRIER": (EType.STRING, "ordinal"),
             "DEPDELAY": (EType.NUMBER, "quantitative"),
             "ORIGINSTATE": (EType.STRING, "ordinal"),
             "ARRDELAY": (EType.NUMBER, "quantitative")}
        self.tables["state_shapes"] = \
            {"state": (EType.STRING, "ordinal"),
             "shape": (EType.GEOJSON, "geojson")}
        self.tables["states"] = \
            {"state": (EType.STRING, "ordinal"),
             "cases": (EType.NUMBER, "quantitative"),
             "death": (EType.NUMBER, "quantitative"),
             "geography": (EType.GEOJSON, "geojson")}

        self.func_deps = [
            # [ ([a1, a2], b), ([a3, a4], c) ]
            ([("flights", "hour")], ("flights", "idx")),
            ([("flights", "bin_distance")], ("flights", "idx")),
            ([("flights", "bin_delay")], ("flights", "idx")),
            ([("sales", "date")], ("sales", "total")),
            ([("sales", "city")], ("sales", "total")),
            ([("sp500", "date")], ("sp500", "price")),
            ([("covid", "date")], ("covid", "cases")),
            ([("covid", "date")], ("covid", "cases_avg")),
            ([("covid", "date")], ("covid", "cases_raw")),
            ([("covid", "date")], ("covid", "deaths")),
        ]

    '''
    return the primary key of a table
    '''
    def get_table_index(self, table):
        if table == "cars": return "Idx"
        elif table == "state_shapes": return "state"
        elif table == "states": return "state"
        else: return None

    def get_attribute_type(self, attr, table=None, db=None):
        if table is not None:
            if table not in self.tables: return None
            if attr not in self.tables[table]: return None
            return Type(EType.ADVANCED, False, attr, table, self.tables[table][attr][0])
        else:
            for t in self.tables:
                if attr in self.tables[t]:
                    return Type(EType.ADVANCED, False, attr, t, self.tables[t][attr][0])
        return None

    def get_attribute_field(self, attr, table=None, db=None):
        # if aggregate function, we only consider quantitative functions
        if attr == "agg(*)":
            return "quantitative"
        if table is not None:
            if table not in self.tables: return None
            if attr not in self.tables[table]: return None
            return self.tables[table][attr][1]
        else:
            for t in self.tables:
                if attr in self.tables[t]:
                    return self.tables[t][attr][1]
        return None

    def is_table(self, name):
        return name in self.tables

    def is_attribute(self, name):
        for t in self.tables:
            if name in self.tables[t]:
                return True
        return False

    def is_ordinal(self, typ):
        if typ.type == EType.STRING: return True
        if typ.type == EType.ADVANCED:
            if typ.table not in self.tables: return False
            if typ.attr not in self.tables[typ.table]: return False 
            return self.tables[typ.table][typ.attr][1] == "ordinal"
        return False 

    def is_quantitative(self, typ):
        if typ.type == EType.NUMBER: return True
        if typ.type == EType.ADVANCED:
            if typ.table not in self.tables: return False
            if typ.attr not in self.tables[typ.table]: return False 
            return self.tables[typ.table][typ.attr][1] == "quantitative"
        return False 

    def load_fds(self):
        return self.func_deps

    def get_functional_dependencies(self):
        fdep = []
        for xs, y in self.func_deps:
            xs = [Type(EType.ADVANCED, False, x[1], x[0], self.tables[x[0]][x[1]][0]) for x in xs]
            y = Type(EType.ADVANCED, False, y[1], y[0], self.tables[y[0]][y[1]][0])
            fdep.append((xs, y))
        return fdep



class DBCatalogue(TestCatalogue):
  NUMERIC = [sa.types.BigInteger, sa.types.Numeric, sa.types.Integer, 
      sa.types.Float]
  TEMPORAL = [sa.types.Date, sa.types.DateTime, sa.types.Time]

  def __init__(self, dburi):
    """
    Use Sqlalchemy's ORM api to extract list of tables and schema infos
    """

    self.dburi = dburi
    print(f"engine: {dburi}")
    engine = create_engine(dburi)

    insp = sa.inspect(engine)

    self.tables = { table: dict() for table in insp.get_table_names() }
    for table_name in self.tables:
      self.tables[table_name] = self.fetch_schema(insp, table_name)


    self.func_deps = self.load_fds()


  def is_numeric(self, col):
    return any(isinstance(col.type, t) for t in DBCatalogue.NUMERIC)

  def is_temporal(self, col):
    return any(isinstance(col.type, t) for t in DBCatalogue.TEMPORAL)

  def is_ordinal(self, col):
    names = ["hour", "objId", "bestObjID"]
    return col.name in names
  def fetch_schema(self, insp, table_name):
    md = sa.MetaData()
    t = sa.Table(table_name, md)
    schema = {}

    insp.reflecttable(t, None)
    for col in t.columns:
      if not isinstance(col, sa.sql.schema.Column): 
        continue

      if self.is_numeric(col):
        etype = EType.NUMBER
        dtype = "quantitative"
      elif self.is_temporal(col):
        etype = EType.TEMPORAL
        dtype = "temporal"
      else:
        etype = EType.STRING
        dtype = "ordinal"

      # SPECIAL CASES (HACKS)
      if self.is_ordinal(col):
        dtype = "ordinal"
      if col.name == "Idx":
        dtype = "key"

      schema[col.name] = (etype, dtype)
    return schema

  def load_fds(self):
    # TODO: infer from database/constraints
    return [
        # [ ([a1, a2], b), ([a3, a4], c) ]
        #
        # means
        #   (a1,a2) -> b
        #   (a3,a4) -> c
        #
        ([("flights", "hour")], ("flights", "idx")),
        ([("flights", "bin_distance")], ("flights", "idx")),
        ([("flights", "bin_delay")], ("flights", "idx")),
        ([("sales", "date")], ("sales", "total")),
        ([("sales", "city")], ("sales", "total")),
        ([("sp500", "date")], ("sp500", "price")),
        ([("covid", "date")], ("covid", "cases")),
        ([("covid", "date")], ("covid", "deaths")),
    ]



