from multiprocessing import Process, Manager, Queue
import random
import math
from config import Config
import time


'''
    MCTSTask defines the problem that MCTS is going to solve and 
    is instantiated as DifftTask in search_difftree.py.
'''
class MCTSTask:
    def get_actions(self, state):
        pass

    def apply(self, state, action):
        pass

    def restore(self, state, reverse):
        pass

    def evaluate(self, state):
        pass


class MCTSNode:
    def __init__(self, parent, crank, c):
        self.uct = 0
        self.times = 0
        self.max_score = None
        self.sum_score = 0
        self.sum_sqr_score = 0
        self.parent = parent
        # crank: the #crank child of the parent.
        self.crank = crank
        self.children = []
        self.c = c
        self.is_new = True

    def update_uct(self):
        if len(self.children) == 0:
            return
        D = 10000
        for c in self.children:
            c.uct = 0
            if c.times == 0:
                c.uct = float("inf")
            else:
                c.uct = (
                    (c.sum_score / c.times)
                    + self.c * math.sqrt(math.log(self.times) / c.times)
                    + math.sqrt(
                        abs(c.sum_sqr_score - c.sum_score * c.sum_score / c.times + D)
                        / c.times
                    )
                )


def random_next_action(actions):
    idx = list(range(len(actions)))
    # sample according to a prob distribution, skip {1, 0.01}, random walk, split and merge is zero.
    prob = list([a[1] for a in actions])
    ch = random.choices(idx, prob)[0]
    return ch

#from graphviz import Digraph


class SingleStepMCTS:
    def __init__(self, state, task, root, proc, n_iters, start_time, max_iters):
        self.state = state
        self.task = task
        self.get_actions = task.get_actions
        self.apply = task.apply
        self.restore = task.restore
        self.eval = task.evaluate
        self.iter_per_merge = Config.iter_per_merge
        self.uct_c = Config.uct_c
        self.rand_map = Config.rand_map
        self.root = root
        self.proc = proc
        self.n_iters = n_iters
        self.max_iters = max_iters
        self.start_time = start_time
        self.record = {}


    def count_tree(self, node):
        nodeno = 1
        depth = 1
        for c in node.children:
            n, d = self.count_tree(c)
            nodeno += n
            depth = max(depth, d + 1)
        return nodeno, depth

    def set_old(self, node):
        for c in node.children:
            self.set_old(c)
        node.is_new = False

    def draw(self, node, g, n):
        g.node_attr.update(style="filled")
        g.node(
            f"{n}",
            f"{node.max_score}/{node.uct}",
            color=("grey" if node.is_new else "white"),
        )
        gn = str(n)
        n += 1
        for c in node.children:
            cn, n = self.draw(c, g, n)
            g.edge(gn, cn)

        return gn, n

    def one_step_search(self, seed, q2me, q2controller):
        random.seed(seed)
        for self.n_iters in range(self.max_iters):
          # maybe use while?
          if not q2me.empty():
            msg = q2me.get()
            if msg[0] == "STOP": 
              # should send latest root to controller when stop
              q2controller.put(("STATE", self.root))
              print(self.proc, "got STOP msg")
              break
            if msg[0] == "STATE":
              self.root = msg[1]

          self.set_old(self.root)
          self.one_iteration()
          now = time.time()
          nodeno, depth = self.count_tree(self.root)
          self.record.update(dict(
            proc=self.proc,
            iter=self.n_iters,
            cost= -self.root.max_score[0], # TODO
            time=now - self.start_time,
            nodeno=nodeno, 
            depth=depth, 
            timestamp=now
          ))

          q2controller.put(("HEARTBEAT", self.n_iters, self.root.max_score, self.record))
          self.record = {}
          if self.n_iters > 1 and self.n_iters % self.iter_per_merge == 0:
            q2controller.put(("STATE", self.root))
            # XXX: uncomment to add barrier between merge stages
            msg = q2me.get()
            if msg[0] == "STOP": break
            self.root = msg[1]

        q2controller.put(("DONE", time.time()))
        q2me.close()
        q2controller.close()
        q2me.join_thread()
        q2controller.join_thread()
        print(self.proc, "STOP")

    def one_iteration(self):
        reverse_items = []
        node = self.root

        # selection

        while len(node.children) > 0:
            actions = self.get_actions(self.state)
            next = 0
            for i in range(1, len(node.children)):
                if node.children[i].uct > node.children[next].uct:
                    next = i
            self.state, reverse = self.apply(self.state, actions[next][0])
            reverse_items.append(reverse)
            node = node.children[next]

        # expansion
        actions = self.get_actions(self.state)
        if actions:
            for i in range(len(actions)):
                node.children.append(MCTSNode(node, i, self.uct_c))
            next = random_next_action(actions)
            self.state, reverse = self.apply(self.state, actions[next][0])
            reverse_items.append(reverse)
            node = node.children[next]

        simulation_path = []


        # simulation
        simulate_steps = 0
        while True:
            actions = self.get_actions(self.state, rw=True)
            if len(actions) == 0:
                break
            next = random_next_action(actions)
            simulation_path.append(next)
            self.state, reverse = self.apply(self.state, actions[next][0])
            reverse_items.append(reverse)
            simulate_steps += 1


        best_cost, best_mappings = None, None

        for _ in range(self.rand_map):
          cost, mappings = self.task.evaluate(self.state)
          if not best_cost or cost > best_cost:
            best_cost, best_mappings = cost, mappings

        roots, _, _ = self.state

        if 1:
          print("%s # %s score: %s" % (self.proc, self.n_iters, best_cost))
        else:
          print("=" * 100)
          print("%s # %s score: %s" % (self.proc, self.n_iters, best_cost))
          print("=" * 100)

          for tree in roots:
              print(tree.get_text())
              print("-" * 50)
          print(",".join([m.wtype() + ' ' + str(m.cost()) for m in best_mappings]))
          print("=" * 100)
        self.record["tree"] = "\n".join([tree.get_text() for tree in roots])
        if best_mappings is not None:
            self.record["mapping"] = ",".join([m.wtype() for m in best_mappings])
        else:
            self.record["mapping"] = ""

        if not self.root.max_score or best_cost >= self.root.max_score:
            for _ in range(simulate_steps):
                reverse = reverse_items.pop()
                self.state = self.restore(self.state, reverse)
            for next in simulation_path:
                actions = self.get_actions(self.state, rw=True)
                self.state, reverse = self.apply(self.state, actions[next][0])
                reverse_items.append(reverse)
                for i in range(len(actions)):
                    node.children.append(MCTSNode(node, i, self.uct_c))
                node = node.children[next]
            simulate_steps = 0

        # backpropagation
        for _ in range(simulate_steps):
            reverse = reverse_items.pop()
            self.state = self.restore(self.state, reverse)
        while node is not None:
            node.is_new = True
            node.times += 1
            node.max_score = best_cost if not node.max_score else max(best_cost, node.max_score)
            node.sum_score += best_cost[0] # TODO: assume best_cost is tuple and the first value is score
            node.sum_sqr_score += best_cost[0] * best_cost[0]
            node.update_uct()
            if reverse_items:
                reverse = reverse_items.pop()
                self.state = self.restore(self.state, reverse)
            node = node.parent

# enter point of subprocesses.
def execute_single_step(task, q2me, q2controller):
    single, seed = task
    single.one_step_search(seed, q2me, q2controller)


class MCTS:
    def __init__(self, state, task):
        self.state = state
        self.task = task
        self.get_actions = task.get_actions
        self.apply = task.apply
        self.restore = task.restore
        self.eval = task.evaluate
        self.n_procs = Config.proc_number
        self.start_time = time.time()

        self.root = MCTSNode(None, -1, Config.uct_c)

    def can_stop(self, heartbeats):
      """
      Check that the past K costs from every process has converged to the same val
      """
      costs = set()
      for pairs in heartbeats:
        if len(pairs) < Config.early_stop: return False
        for rec in pairs[-Config.early_stop:]: costs.add(rec[1][1])
      return len(set(costs)) == 1

    def play(self):
      heartbeats = [[] for i in range(self.n_procs)]
      dones = [False] * self.n_procs
      roots = [None] * self.n_procs
      seeds = list([random.randint(0, 100000000) for _ in range(self.n_procs)])
      tasks = [
          SingleStepMCTS(
              self.state, self.task, self.root, i, 0, 
              self.start_time, Config.iter_number
          )
          for i in range(self.n_procs)
      ]

      if self.n_procs == 1:
        task = tasks[0]
        print("new seed: ", seeds[0])
        random.seed(seeds[0])
        for i in range(Config.iter_number):
          task.set_old(self.root)
          task.one_iteration()

          #g = Digraph()
          #task.draw(task.root, g, 0)
          #g.render(f'data/{i}.gv')
          
          if i == 10:
            Config.can_debug = True

          now = time.time()
          nodeno, depth = task.count_tree(self.root)
          task.record.update(dict(
            proc=0,
            iter=i,
            cost= -task.root.max_score[0],
            time=now - self.start_time,
            nodeno=nodeno, 
            depth=depth, 
            timestamp=now
          ))
          Config.log_iter(task.record)
          task.record = {}
          print(i)


          heartbeats[0].append((i, task.root.max_score))
          if self.can_stop(heartbeats):
            break

        self.merge_sub_results([task.root])
        max_score = self.root.max_score
        self.apply_optimal_path()
        print('mcts rand optimal ' + str(max_score))
        return self.state, max_score

      procs = []
      for task in zip(tasks, seeds):
        qme2proc = Queue() # me to proc
        qproc2me = Queue() # proc to me
        p = Process(target=execute_single_step, args=(task, qme2proc, qproc2me))
        procs.append((p, qme2proc, qproc2me))
      for p, _, _ in procs:
        p.start()

      #
      # XXX: this is not robust to errors nor extreme 
      # progress disparities between processes.
      #
      # on error, we should
      # 1. track that process died and mark it as done
      # 2. not expect its data when deciding merge
      # 3. not include it in the can_stop checks
      #
      # if progress disparity, then one process may be DONE
      # while others still are waiting on merge responses
      # from controller, which will never be heard because
      # roots will have empty slots for the DONE process.
      #
      while True:
        time.sleep(0.01)

        for i, (p, _, qproc2me) in enumerate(procs):
          while not qproc2me.empty():
            msg = qproc2me.get()
            if msg[0] == "DONE":
              dones[i] = True
            elif msg[0] == "STATE":
              roots[i] = msg[1]
            else:  # a heartbeat
               heartbeats[i].append(msg[1:-1])
               Config.log_iter(msg[3])

        if all(dones): break

        # all processes have finished K iterations
        if all(roots):
          now = time.time()
          self.merge_sub_results(roots)
          Config.log_tmerge(time.time() - now)
          for (p, qme2proc, _) in procs:
            qme2proc.put(("STATE", self.root))
          roots = [None] * self.n_procs

        if self.can_stop(heartbeats):
          for (p, qme2proc, _) in procs:
            qme2proc.put(("STOP", None))
          break
        # end while loop

      print("about to join.  is everyone done?")
      print(dones)

      # Cleanup and flush out any remaining heartbeats
      for i, (p, qme2proc, qproc2me) in enumerate(procs):
        if not dones[i]:
          qme2proc.put(("STOP", None))

        while not dones[i]:
          msg = qproc2me.get()
          print(msg)
          if msg[0] == "HEARTBEAT":
            Config.log_iter(msg[3])
          elif msg[0] == "STATE":
            roots[i] = msg[1]
          elif msg[0] == "DONE":
            dones[i] = True

        print("join on", i)
        p.join()
      now = time.time()

      if all(roots):
        now = time.time()
        self.merge_sub_results(roots)
        Config.log_tmerge(time.time() - now)

      max_score = self.root.max_score
      self.apply_optimal_path()
      return self.state, max_score

    def apply_optimal_path(self):
      while True:
        actions = self.get_actions(self.state)
        if not self.root.children or not actions:
            break
        idx = self.get_decision()
        self.state, _ = self.apply(self.state, actions[idx][0])
        self.root = self.root.children[idx]
        self.root.parent = None
        self.root.crank = -1
        #print the transformation path to the optimal
        # print("==="*10)
        # for r in self.state[0]:
        #   print(r.get_text())
        # print("==="*10)

    def merge_sub_results(self, roots):
        def merge(nodes):
            children = []
            n_child = max(len(n.children) for n in nodes)
            merged = MCTSNode(None, -1, Config.uct_c)
            for n in nodes:
                merged.times += n.times
                if not merged.max_score:
                    merged.max_score = n.max_score
                elif n.max_score:
                    merged.max_score = max(n.max_score, merged.max_score)
                merged.sum_score += n.sum_score
                merged.sum_sqr_score += n.sum_sqr_score
            for i in range(n_child):
                sub_nodes = []
                for n in nodes:
                    if n.children:
                        sub_nodes.append(n.children[i])
                children.append(merge(sub_nodes))
                children[-1].parent = merged
                children[-1].crank = i
            merged.children = children
            merged.update_uct()
            return merged

        if len(roots) == 1:
            self.root = roots[0]
        else:
            self.root = merge(roots)

    def get_decision(self):
        decision = None
        for c in self.root.children:
            if c.times == 0:
                continue
            if decision is None or c.max_score > decision.max_score:
                decision = c
        actions = self.get_actions(self.state)
        # print("***" * 20)
        # print(self.root.children[decision.crank].max_score, actions[decision.crank])

        return decision.crank
