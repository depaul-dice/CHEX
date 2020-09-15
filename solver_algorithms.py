import subprocess

from pyomo.environ import *
from pyomo.opt import ProblemFormat, ReaderFactory, ResultsFormat

from algorithms import dfs_cost

MODEL_FILE_NAME = 'instance.nl'
COUENNE = ['couenne', 'instance']  # Modify Couenne path here if not present in PATH
SOLUTION_FILE_NAME = 'instance.sol'


def solve(model, verbose):
    """Solve a given model using Couenne"""
    _, symbol_map_id = model.write(MODEL_FILE_NAME, format=ProblemFormat.nl)

    try:
        subprocess.run(COUENNE, capture_output=not verbose)
    except FileNotFoundError:
        print('Couenne not found in PATH.')
        print('Please input path or leave empty to run manually and generate instance.sol')
        couenne_path = input()
        if couenne_path:
            subprocess.run([couenne_path, *COUENNE[1:]], capture_output=not verbose)

    with ReaderFactory(ResultsFormat.sol) as reader:
        results = reader(SOLUTION_FILE_NAME)
    results._smap_id = symbol_map_id

    model.solutions.load_from(results)


def optimal_dfs(ex_tree, verbose=False):
    """Create a Pyomo model for the optimal DFS problem and solve it"""
    nodes_list = ex_tree.all_nodes()
    nodes = {node.identifier: (i+1, node) for i, node in enumerate(nodes_list)}
    paths = ex_tree.paths_to_leaves()

    model = AbstractModel()

    # Pyomo Sets are 1-indexed: valid index values for Sets are [1 .. len(Set)]
    # so all indexes have to be subtracted from 1 for ex_tree
    model.i = RangeSet(1, len(nodes))
    model.j = RangeSet(1, len(paths))

    model.x = Var(model.i, domain=Boolean, initialize=lambda *_: 0)
    model.y = Var(model.i, within=PositiveIntegers, initialize=lambda *_: 1)

    model.paths = Constraint(model.j,
                             rule=lambda m, j: inequality(0,
                                                          sum(nodes[k][1].data.c_size * m.x[nodes[k][0]]
                                                              for k in paths[j-1]),
                                                          ex_tree.cache_size))

    @model.Constraint(model.i)
    def y_constraint(m, i):
        if nodes_list[i-1].is_leaf():
            return m.y[i] == 1
        else:
            return m.y[i] == sum(1 + (m.y[nodes[child.identifier][0]] - 1) * (1 - m.x[nodes[child.identifier][0]])
                                 for child in ex_tree.children(nodes_list[i-1].identifier))

    model.construct()
    if verbose:
        model.pprint()

    model.total_cost = Objective(expr=sum((node.data.r_cost * (model.y[i] - 1) * (1 - model.x[i]))
                                          for i, node in nodes.values()),
                                 sense=minimize)

    solve(model, verbose)

    if verbose:
        model.x.display()

    for i, node in nodes.values():
        node.data.x_in_cache = bool(round(model.x[i].value))
    if verbose:
        ex_tree.show(data_property='x_in_cache')


def optimal(ex_tree, verbose=False):
    """Create a Pyomo model for the optimal problem and solve it"""
    max_time = dfs_cost(ex_tree, force_cost=1)
    if verbose:
        print(f'Max Time: {max_time}')

    nodes_list = ex_tree.all_nodes()
    nodes = {node.identifier: (i+1, node) for i, node in enumerate(nodes_list)}
    paths = ex_tree.paths_to_leaves()

    model = AbstractModel()

    # Pyomo Sets are 1-indexed: valid index values for Sets are [1 .. len(Set)]
    # so all indexes have to be subtracted from 1 for ex_tree
    model.t = RangeSet(0, max_time)
    model.i = RangeSet(1, len(nodes))
    model.j = RangeSet(1, len(paths))

    model.x = Var(model.i, model.t, domain=Boolean, initialize=lambda *_: 0)
    model.p = Var(model.i, model.t, domain=Boolean, initialize=lambda *_: 0)

    @simple_constraintlist_rule
    def x_time_0_rule(m, i):
        if i == len(nodes) + 1:
            return None
        return m.x[i, 0] == 0

    model.x_time_0_constraint = ConstraintList(rule=x_time_0_rule)

    @simple_constraintlist_rule
    def p_time_0_rule(m, i):
        if i == len(nodes) + 1:
            return None
        return m.p[i, 0] == 0

    model.p_time_0_constraint = ConstraintList(rule=p_time_0_rule)

    @simple_constraintlist_rule
    def cache_size_rule(m, time):
        if time == max_time + 1:
            return None
        return inequality(0, sum(m.x[i, time] * node.data.c_size for i, node in nodes.values()), ex_tree.cache_size)

    model.cache_size_constraint = ConstraintList(rule=cache_size_rule)

    @simple_constraintlist_rule
    def produce_one_thing_at_a_time_rule(m, time):
        if time == max_time + 1:
            return None
        return inequality(0, sum(m.p[i, time] for i in range(1, 1 + len(nodes))), 1)

    model.produce_one_thing_constraint = ConstraintList(rule=produce_one_thing_at_a_time_rule)

    @simple_constraintlist_rule
    def produce_everything_at_least_one_rule(m, i):
        if i == len(nodes) + 1:
            return None
        return sum(m.p[i, time] for time in range(1 + max_time)) >= 1

    model.produce_everything_constraint = ConstraintList(rule=produce_everything_at_least_one_rule)

    model.construct()

    model.cache_consistency_constraint = ConstraintList()
    for i in range(1, 1 + len(nodes)):
        for t in range(1, 1 + max_time):
            model.cache_consistency_constraint.add(model.x[i, t] * (1 - model.x[i, t-1]) * (1 - model.p[i, t]) == 0)

    model.parent_present_constraint = ConstraintList()
    for i in range(1, 1 + len(nodes)):
        if i == nodes[ex_tree.root][0]:
            continue
        p = nodes[ex_tree.parent(nodes_list[i-1].identifier).identifier][0]
        for t in range(1, 1 + max_time):
            model.parent_present_constraint.add(model.p[i, t] * (1 - model.x[p, t - 1]) * (1 - model.p[p, t - 1]) == 0)

    if verbose:
        model.pprint()

    model.total_cost = Objective(expr=sum(node.data.r_cost*model.p[i, t]
                                          for t in range(1, 1 + max_time)
                                          for i, node in nodes.values()),
                                 sense=minimize)

    solve(model, verbose)

    if verbose:
        model.x.display()
        model.p.display()

    for i, node in nodes.values():
        node.data.x_in_cache = [bool(round(model.x[i, t].value)) for t in range(1 + max_time)]
        node.data.p_computed = [bool(round(model.p[i, t].value)) for t in range(1 + max_time)]
    if verbose:
        ex_tree.show(data_property='x_in_cache')
        ex_tree.show(data_property='p_computed')
