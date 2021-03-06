# CHEX - Multiversion Replay with Ordered Checkpoints
# Copyright (c) 2020 DePaul University
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
#
# Author: Naga Nithin Manne <nithinmanne@gmail.com>

# File purpose: Implementations of the MINLP algorithms using the Couenne solver.
# Usage: For Bob to generate replay sequences using the mentioned algorithms.

import shutil

from pyomo.environ import *

from util import dfs_cost
from algorithms import prp_v1


def _couenne_solve(model, verbose=False):
    """Solve a given model using Couenne"""
    if not shutil.which('couenne'):
        if not hasattr(_couenne_solve, 'couenne_path'):
            print('Couenne not in PATH.')
            _couenne_solve.couenne_path = input('Please input path to executable: ')
    else:
        _couenne_solve.couenne_path = None

    opt = SolverFactory('couenne', executable=_couenne_solve.couenne_path)

    model.solutions.load_from(opt.solve(model, tee=verbose))


def optimal_dfs(ex_tree, verbose=False):
    """Create a Pyomo model for the optimal DFS problem and solve it"""
    nodes_list = ex_tree.all_nodes()
    nodes = {node.identifier: (i + 1, node) for i, node in enumerate(nodes_list)}
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
                                                              for k in paths[j - 1]),
                                                          ex_tree.cache_size))

    @model.Constraint(model.i)
    def y_constraint(m, i):
        if nodes_list[i - 1].is_leaf():
            return m.y[i] == 1
        else:
            return m.y[i] == sum(1 + (m.y[nodes[child.identifier][0]] - 1) * (1 - m.x[nodes[child.identifier][0]])
                                 for child in ex_tree.children(nodes_list[i - 1].identifier))

    model.construct()
    if verbose:
        model.pprint()

    model.total_cost = Objective(expr=sum((node.data.r_cost * (model.y[i] - 1) * (1 - model.x[i]))
                                          for i, node in nodes.values()),
                                 sense=minimize)

    _couenne_solve(model, verbose)

    if verbose:
        model.x.display()

    for i, node in nodes.values():
        node.data.x_in_cache = bool(round(model.x[i].value))
    if verbose:
        ex_tree.show(data_property='x_in_cache')


def optimal(ex_tree, verbose=False):
    """Create a Pyomo model for the optimal problem and solve it"""
    prp_v1(ex_tree, verbose)
    max_time = dfs_cost(ex_tree, force_cost=1)
    ex_tree.reset()
    if verbose:
        print(f'Max Time: {max_time}')

    nodes_list = ex_tree.all_nodes()
    nodes = {node.identifier: (i + 1, node) for i, node in enumerate(nodes_list)}

    model = AbstractModel()

    # Pyomo Sets are 1-indexed: valid index values for Sets are [1 .. len(Set)]
    # so all indexes have to be subtracted from 1 for ex_tree
    model.t = RangeSet(0, max_time)
    model.i = RangeSet(1, len(nodes))

    model.x = Var(model.i, model.t, domain=Boolean, initialize=lambda *_: 0)
    model.p = Var(model.i, model.t, domain=Boolean, initialize=lambda *_: 0)

    model.x_time_0_constraint = Constraint(model.i, rule=lambda m, i: m.x[i, 0] == 0)
    model.p_time_0_constraint = Constraint(model.i, rule=lambda m, i: m.p[i, 0] == 0)

    # Constraint to make sure cache is not over-filled at any time
    model.cache_size_constraint = Constraint(model.t,
                                             rule=lambda m, time: inequality(0,
                                                                             sum(m.x[i, time] * node.data.c_size
                                                                                 for i, node in nodes.values()),
                                                                             ex_tree.cache_size))
    # Constraint to produce only one thing at a time step
    model.produce_one_thing_constraint = Constraint(model.t,
                                                    rule=lambda m, time: inequality(0,
                                                                                    sum(m.p[i, time]
                                                                                        for i, _ in nodes.values()),
                                                                                    1))
    # Constraint to produce everything at least once
    model.produce_everything_constraint = Constraint(model.i,
                                                     rule=lambda m, i: sum(m.p[i, t]
                                                                           for t in range(1, 1 + max_time)) >= 1)

    # Constraint to make sure an element is in cache only if it was previously in cache or generated now
    model.cache_consistency_constraint = Constraint(model.i,
                                                    rule=lambda m, i: sum(m.x[i, t] *
                                                                          (1 - m.x[i, t - 1]) *
                                                                          (1 - m.p[i, t])
                                                                          for t in range(1, 1 + max_time)) == 0)

    # Constraint to make sure an element can be generated only if parent in cache or generated previously
    @model.Constraint(model.i)
    def parent_present_constraint(m, i):
        if i == nodes[ex_tree.root][0]:
            return Constraint.Feasible
        else:
            p = nodes[ex_tree.parent(nodes_list[i - 1].identifier).identifier][0]
            return sum(m.p[i, t] * (1 - m.x[p, t - 1]) * (1 - m.p[p, t - 1])
                       for t in range(1, 1 + max_time)) == 0

    model.construct()

    if verbose:
        model.pprint()

    model.total_cost = Objective(expr=sum(node.data.r_cost * model.p[i, t]
                                          for t in range(1, 1 + max_time)
                                          for i, node in nodes.values()),
                                 sense=minimize)

    _couenne_solve(model, verbose)

    if verbose:
        model.x.display()
        model.p.display()

    for i, node in nodes.values():
        node.data.x_in_cache = [bool(round(model.x[i, t].value)) for t in range(1 + max_time)]
        node.data.p_computed = [bool(round(model.p[i, t].value)) for t in range(1 + max_time)]
    if verbose:
        ex_tree.show(data_property='x_in_cache')
        ex_tree.show(data_property='p_computed')
