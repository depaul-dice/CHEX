from collections import defaultdict

import matplotlib.pyplot as plt

from util import create_registerer, cost
import ExecutionTree as exT


get_trees, register_x_param_generator = create_registerer()


@register_x_param_generator
def cache_size(size_range, k=3, height=3):
    """Iterator for using cache_size on the x-axis"""
    ex_tree = exT.create_tree('KARY', k, height, lambda h: exT.NodeData(h + 1, h + 1))
    for size in size_range:
        ex_tree.cache_size = size
        yield size, ex_tree
        ex_tree.reset()


@register_x_param_generator
def k_height(k_height_range, size=4):
    for k, height in k_height_range:
        ex_tree = exT.create_tree('KARY', k, height, lambda h: exT.NodeData(h + 1, h + 1))
        ex_tree.cache_size = size
        yield (k, height), ex_tree


def experiment(algorithms, x_param, *args, **kwargs):

    x_range = []
    y_ranges = defaultdict(list)
    for x, ex_tree in get_trees(x_param, *args, **kwargs):
        x_range.append(x)
        for algorithm in algorithms:
            algorithm(ex_tree)
            y_ranges[algorithm].append(cost(ex_tree))
            ex_tree.reset()

    for algorithm in algorithms:
        plt.plot(list(range(len(x_range))), y_ranges[algorithm])

    plt.show()


def test(algorithms):
    # create a tree
    # possible types: FIXED, BRANCH, KARY, SCIUNIT
    # ex_tree = exT.create_tree('FIXED')
    # ex_tree = exT.create_tree('BRANCH', 3, 4)
    ex_tree = exT.create_tree('KARY', 2, 3, lambda h: exT.NodeData(h + 1, h + 1))
    # ex_tree = exT.create_tree('SCIUNIT', input('Enter Tree Binary: '), input('Enter Images Path: '))

    ex_tree.cache_size = 4

    # ex_tree.show()
    # ex_tree.show(data_property='c_size')
    # ex_tree.show(data_property='r_cost')

    # run algorithms
    # possible types: greedy1, greedy2, optimal_dfs, optimal

    print(f'Without Cache = {cost(ex_tree)}')

    for algorithm in algorithms:
        algorithm(ex_tree)
        print(f'{algorithm.__name__} Cost = {cost(ex_tree)}')
        ex_tree.reset()
