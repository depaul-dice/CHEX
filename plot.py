import random

import ExecutionTree as exT
from util import cost
from algorithms import dfs_algorithm_v1, dfs_algorithm_v2, recurse_algorithm
from solver_algorithms import optimal_dfs, optimal


LABEL = {dfs_algorithm_v1: 'DFS Algorithm v1',
         dfs_algorithm_v2: 'DFS Algorithm v2',
         recurse_algorithm: 'BestCost Algorithm',
         optimal_dfs: 'Couenne Optimal DFS',
         optimal: 'Couenne Optimal'}

def plot_real(verbose=False):
    trees = ['epruning.bin', 'financial_news.bin', 'kaggle.bin', 'natgas.bin', 'nasa.bin']
    mems = [[i * 200 * 1024 ** 2 for i in range(1, 50)],
            [i * 20 * 1024 ** 2 for i in range(1, 50)],
            [i * 1024 ** 3 for i in range(1, 10)],
            [i * 25 * 1024 ** 2 for i in range(1, 20)],
            [i * 10 * 1024 ** 2 for i in range(1, 10)]]

    algos = [dfs_algorithm_v1, dfs_algorithm_v2, recurse_algorithm]
    linshapes = ['*-', '.-', 'x-']
    
    from collections import defaultdict as ddict
    data = ddict(dict)
    
    from matplotlib import pyplot as plt
    
    for t, tmems in zip(trees, mems):
        ex_tree = exT.create_tree('SCIUNIT', t)
        for algorithm, l in zip(algos, linshapes):
            data[t][algorithm] = [(0, cost(ex_tree))]
            for cache_sz in tmems:
                ex_tree.cache_size = cache_sz
                algorithm(ex_tree, verbose)
                print(f'{t}-{LABEL[algorithm]} Cost (Cache:{cache_sz}) = {cost(ex_tree)}')
                data[t][algorithm].append((cache_sz / 1024**2, cost(ex_tree)))
                ex_tree.reset()
            plt.plot(*zip(*data[t][algorithm]), l, label=LABEL[algorithm])
        plt.xlabel('Cache Size (in MB)')
        plt.ylabel('Total Cost')
        plt.legend()
        plt.title(t)
        # plt.show()
        plt.savefig(f'{t}.jpg', dpi=1200)
        plt.clf()


def ci_node_factory(height):
    height = max(1, height)
    r_cost_lim = 100 * height
    c_size_lim = 1024**2 * 500
    r_cost = random.randint(max(1, r_cost_lim - 10), r_cost_lim + 10)
    c_size = random.randint(max(1, c_size_lim - 10), c_size_lim + 10)
    return exT.NodeData(r_cost, c_size)

def di_node_factory(height):
    height = max(1, height)
    r_cost_lim = 100
    c_size_lim = 1024**2 * 100 * height
    r_cost = random.randint(max(1, r_cost_lim - 10), r_cost_lim + 10)
    c_size = random.randint(max(1, c_size_lim - 10), c_size_lim + 10)
    return exT.NodeData(r_cost, c_size)

def an_node_factory(height):
    height = max(1, height)
    r_cost_lim = 100 * height
    c_size_lim = 1024**2 * 100 * height
    r_cost = random.randint(max(1, r_cost_lim - 10), r_cost_lim + 10)
    c_size = random.randint(max(1, c_size_lim - 10), c_size_lim + 10)
    return exT.NodeData(r_cost, c_size)

def plot_synthetic(verbose=False):
    tree_args = [(3, 6, ci_node_factory),
                 (3, 6, di_node_factory),
                 (3, 6, an_node_factory)]
    mems = [[i * 20 * 1024 ** 2 for i in range(1, 100)],
            [i * 50 * 1024 ** 2 for i in range(1, 50)],
            [i * 50 * 1024 ** 2 for i in range(1, 50)]]

    algos = [dfs_algorithm_v1, dfs_algorithm_v2, recurse_algorithm]
    linshapes = ['*-', '.-', 'x-']
    
    from collections import defaultdict as ddict
    data = ddict(dict)
    
    from matplotlib import pyplot as plt
    
    for t, tmems in zip(tree_args, mems):
        ex_tree = exT.create_tree('BRANCH', *t)
        for algorithm, l in zip(algos, linshapes):
            data[t][algorithm] = [(0, cost(ex_tree))]
            for cache_sz in tmems:
                ex_tree.cache_size = cache_sz
                algorithm(ex_tree, verbose)
                print(f'{t[2].__name__[:2]}-{LABEL[algorithm]} Cost (Cache:{cache_sz}) = {cost(ex_tree)}')
                data[t][algorithm].append((cache_sz / 1024**2, cost(ex_tree)))
                ex_tree.reset()
            plt.plot(*zip(*data[t][algorithm]), l, label=LABEL[algorithm])
        plt.xlabel('Cache Size (in MB)')
        plt.ylabel('Total Cost')
        plt.legend()
        plt.title(t[2].__name__[:2])
        # plt.show()
        plt.savefig(f'{t[2].__name__[:2]}.jpg', dpi=1200)
        plt.clf()

def plot_algotime(verbose=False):
    import time
    from collections import defaultdict as ddict
    data = ddict(list)

    tree_args = [(3, 2), (3, 3), (3, 4), (3, 5)]
    mem = 1024**4
    algos = [dfs_algorithm_v1, dfs_algorithm_v2, recurse_algorithm]
    linshapes = ['*-', '.-', 'x-']

    for algorithm in algos:
        for t in tree_args:
            ex_tree = exT.create_tree('KARY', *t)
            ex_tree.cache_size = mem
            begin = time.time()
            algorithm(ex_tree, verbose)
            end = time.time()
            print(f'{LABEL[algorithm]}-{t} Time = {end - begin}')
            data[algorithm].append((f'{t}', end - begin))
        plt.plot(*zip(*data[algorithm]), label=LABEL[algorithm])

    plt.xlabel('Tree Size')
    plt.ylabel('Algorithm Running Time')
    plt.legend()
    plt.title('Running Time')
    # plt.show()
    plt.savefig('running_time.jpg', dpi=1200)
    plt.clf()
