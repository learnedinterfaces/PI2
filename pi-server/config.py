import json
import pandas as pd
from sqlalchemy import *


class Config:
  can_debug = False
  recs_iter = []
  recs_exp = [{}]

  config = None
  usecase = None
  run = None
  uct_c = None
  iter_per_merge = None
  iter_number = None
  rand_map = None
  proc_number = None
  early_stop = None

  max_width = 800
  max_height = 600


  seed = None
  tmcts = None
  tmerge = 0
  tmapping = None
  toverall = None
  cost_num = None
  difftree = None
  shorthand = None
  final_cost = None
  nav_cost = None
  spec = None
  final_timestamp = None

  @classmethod
  def init_config(cls, config):
    cls.config = config
    cls.usecase = config['usecase']
    cls.run = config['run']
    cls.uct_c = config['mcts']['uct_c']
    cls.iter_per_merge = config['mcts']['iteration_per_merge']
    cls.iter_number = config['mcts']['iteration_number']
    cls.rand_map = config['mcts']['rand_map']
    cls.proc_number = config['mcts']['process_number']
    cls.early_stop = config['mcts']['early_stop']

    cls.max_width = config.get('max_width', 800)
    cls.max_height = config.get('max_height', 600)



    # XXX: create new exp record?
    cls.new_experiment()
    cls.recs_exp[-1]["usecase"] = config['usecase']
    cls.recs_exp[-1]["run"] = config['run']
    cls.recs_exp[-1]["uct_c"] = config['mcts']['uct_c']
    cls.recs_exp[-1]["iter_per_merge"] = config['mcts']['iteration_per_merge']
    cls.recs_exp[-1]["iter_number"] = config['mcts']['iteration_number']
    cls.recs_exp[-1]["rand_map"] = config['mcts']['rand_map']
    cls.recs_exp[-1]["proc_number"] = config['mcts']['process_number']
    cls.recs_exp[-1]["early_stop"] = config['mcts']['early_stop']
    cls.recs_exp[-1]["tmerge"] = cls.tmerge

  @classmethod
  def log_iter(cls, rec):
    rec.update({
      "usecase": cls.usecase,
      "iter_per_merge": cls.iter_per_merge,
      "iter_number": cls.iter_number,
      "uct_c": cls.uct_c,
      'rand_map': cls.rand_map,
      'run': cls.run,
      'proc_number': cls.proc_number,
      'early_stop': cls.early_stop
    })
    cls.recs_iter.append(rec)

  @classmethod
  def log_seed(cls, seed):
      cls.seed = seed
      cls.recs_exp[-1]['seed'] = seed

  @classmethod
  def log_tmcts(cls, time):
      cls.tmcts = time
      cls.recs_exp[-1]["tmcts"] = time

  @classmethod
  def log_tmerge(cls, time):
      cls.tmerge += time
      d = cls.recs_exp[-1]
      d["tmerge"] = d.get("tmerge", 0) + time

  @classmethod
  def log_tmapping(cls, time):
      cls.tmapping = time
      cls.recs_exp[-1]["tmapping"] = time

  @classmethod
  def log_toverall(cls, time):
      cls.toverall = time
      cls.recs_exp[-1]["toverall"] = time

  @classmethod
  def log_cost_num(cls, cost_num):
      cls.cost_num = cost_num
      cls.recs_exp[-1]["cost_num"] = cost_num

  @classmethod
  def log_difftrees(cls, difftree):
      cls.difftree = difftree
      cls.recs_exp[-1]["difftree"] = difftree

  @classmethod
  def log_shorthand(cls, shorthand):
      cls.shorthand = shorthand
      cls.recs_exp[-1]["shorthand"] = shorthand

  @classmethod
  def log_spec(cls, spec):
      cls.spec = spec
      cls.recs_exp[-1]["spec"] = json.dumps(spec)

  @classmethod
  def log_final_cost(cls, cost):
      cls.final_cost = cost[0]
      cls.nav_cost = cost[1]
      cls.recs_exp[-1]["final_cost"] = cost[0]
      cls.recs_exp[-1]["nav_cost"] = cost[1]


  @classmethod
  def log_final_timestamp(cls, time):
      cls.final_timestamp = time
      cls.recs_exp[-1]["final_timestamp"] = time

  @classmethod
  def new_experiment(cls):
    rexpr = {
        "usecase": cls.usecase,
        "iter_per_merge": cls.iter_per_merge,
        "iter_number": cls.iter_number,
        "uct_c": cls.uct_c,
        'rand_map': cls.rand_map,
        'run': cls.run,
        'proc_number': cls.proc_number,
        'early_stop': cls.early_stop,
        "seed": cls.seed,
        "tmcts": cls.tmcts,
        "tmerge": cls.tmerge,
        "tmapping": cls.tmapping,
        "toverall": cls.toverall,
        "cost_num": cls.cost_num,
        "difftree": cls.difftree,
        "shorthand": cls.shorthand,
        "final_cost": cls.final_cost,
        "nav_cost": cls.nav_cost,
        "spec": json.dumps(cls.spec),
        "final_timestamp": cls.final_timestamp
    }
    cls.recs_exp.append(rexpr)

  @classmethod
  def record(cls):
    """
    Ends an experiment, stores current records, clears records
    """
    db = create_engine("sqlite:///%s" % cls.config["log_db"])
    dexpr = pd.DataFrame(data=cls.recs_exp[-1:])
    dexpr.to_sql("res", db, if_exists="append", index=False)
    if cls.recs_iter:
      diter = pd.DataFrame(data=cls.recs_iter)
      diter.to_sql("iter", db, if_exists='append', index=False)

    cls.recs_iter = []
    cls.recs_exp = []
    cls.new_experiment()

