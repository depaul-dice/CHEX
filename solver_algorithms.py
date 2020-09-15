import subprocess

from pyomo.environ import *
from pyomo.opt import ProblemFormat, ReaderFactory, ResultsFormat

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

    model.x = Var(model.i, within=Binary, initialize=lambda *_: 0)
    model.y = Var(model.i, within=PositiveIntegers, initialize=lambda *_: 1)

    model.paths = Constraint(model.j,
                             rule=lambda m, j: inequality(0,
                                                          sum(nodes[k][1].data.c_size * m.x[nodes[k][0]]
                                                              for k in paths[j-1]),
                                                          ex_tree.cache_size))

    def y_constraint(m, i):
        if nodes_list[i-1].is_leaf():
            return m.y[i] == 1
        else:
            return m.y[i] == sum(1 + (m.y[nodes[child.identifier][0]] - 1) * (1 - m.x[nodes[child.identifier][0]])
                                 for child in ex_tree.children(nodes_list[i-1].identifier))

    model.y_constraint = Constraint(model.i, rule=y_constraint)

    model.construct()

    model.total_cost = Objective(expr=sum((node.data.r_cost * (model.y[i] - 1) * (1 - model.x[i]))
                                          for i, node in nodes.values()),
                                 sense=minimize)

    solve(model, verbose)

    for i, node in nodes.values():
        node.data.x_in_cache = bool(round(model.x[i].value))
    if verbose:
        print(ex_tree.show(data_property='x_in_cache'))
