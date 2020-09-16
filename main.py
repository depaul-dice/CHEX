# The objective of this program is to store nodes of a tree in a cache
# such that the time to compute the graph is minimized.
# Input is a tree with nodes labels of compute cost (cost to compute the node)
# and storage cost (cost of storing a NodeData).

from algorithms import dfs_algorithm_v1, dfs_algorithm_v2
from solver_algorithms import optimal_dfs, optimal
from experiment import test, experiment


def main():

    # Experiment 1
    experiment([dfs_algorithm_v1, dfs_algorithm_v2, optimal_dfs], 'cache_size', range(1, 1 + 10),
               title='Experiment 1 Cache size Vs Re-computation Cost')

    # Experiment 2
    experiment([dfs_algorithm_v1, dfs_algorithm_v2, optimal_dfs], 'k_height', [(k, 3) for k in range(2, 6)],
               title='Experiment 2 Increasing k Vs Re-computation Cost')

    # Experiment 3
    experiment([dfs_algorithm_v1, dfs_algorithm_v2, optimal_dfs], 'k_height', [(2, h) for h in range(2, 6)],
               title='Experiment 3 Increasing height Vs Re-computation Cost')

    test([dfs_algorithm_v1, dfs_algorithm_v2, optimal_dfs, optimal])


if __name__ == '__main__':
    main()
