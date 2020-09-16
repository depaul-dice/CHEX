# The objective of this program is to store nodes of a tree in a cache
# such that the time to compute the graph is minimized.
# Input is a tree with nodes labels of compute cost (cost to compute the node)
# and storage cost (cost of storing a NodeData).

from algorithms import dfs_algorithm_v1, dfs_algorithm_v2
from solver_algorithms import optimal_dfs, optimal
from experiment import test, experiment


def main():

    experiment([dfs_algorithm_v1, dfs_algorithm_v2, optimal_dfs], 'cache_size', range(1, 1 + 10))

    experiment([dfs_algorithm_v1, dfs_algorithm_v2, optimal_dfs], 'k_height', [(2, 1), (2, 2), (2, 3), (3, 2)])

    test([dfs_algorithm_v1, dfs_algorithm_v2, optimal_dfs, optimal])


if __name__ == '__main__':
    main()
