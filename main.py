# The objective of this program is to store nodes of a tree in a cache
# such that the time to compute the graph is minimized.
# Input is a tree with nodes labels of compute cost (cost to compute the node)
# and storage cost (cost of storing a NodeData).

import ExecutionTree as exT
from algorithms import dfs_cost, dfs_algorithm_v1, dfs_algorithm_v2
from solver_algorithms import optimal_dfs


def main():
    # create a tree
    # possible types: FIXED, BRANCH, KARY
    # ex_tree = exT.create_tree('FIXED')
    # ex_tree = exT.create_tree('BRANCH', 3, 4)
    ex_tree = exT.create_tree('KARY', 3, 3, lambda h: exT.NodeData(h+1, h+1))

    ex_tree.cache_size = 4

    # run algorithms
    # possible types: greedy1, greedy2, optimal

    dfs_algorithm_v1(ex_tree)
    print(f'dfs_algorithm_v1 Cost = {dfs_cost(ex_tree)}')
    ex_tree.reset()

    dfs_algorithm_v2(ex_tree)
    print(f'dfs_algorithm_v2 Cost = {dfs_cost(ex_tree)}')
    ex_tree.reset()

    optimal_dfs(ex_tree)
    print(f'optimal_dfs Cost = {dfs_cost(ex_tree)}')
    ex_tree.reset()


if __name__ == '__main__':
    main()
