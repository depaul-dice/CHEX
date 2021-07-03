import random
import time
from collections import defaultdict as ddict

import numpy as np
from matplotlib import pyplot as plt

import ExecutionTree as exT
from util import *
from algorithms import *
from solver_algorithms import *


PLOT_ERROR_BARS = False
VERBOSE_SHOW_PLOT = False
ALGORITHM_VERBOSE = False
VERBOSE_PRINT_INFO = True
EXP_COUNT = 10

ALGOS = {dfs_algorithm_v1: 'DFS Algorithm v1',
         dfs_algorithm_v2: 'DFS Algorithm v2',
         recurse_algorithm: 'BestCost Algorithm',
         # optimal_dfs: 'Couenne Optimal DFS',
         # optimal: 'Couenne Optimal',
         online_algorithm: 'Online Algorithm'}

LINSHAPES = ['*-', '.-', 'x-', '<-', '>-', 's-', 'D-']

def plot_real(verbose=False):
    trees = {'epruning.bin': 'Epruning',
             'financial_news.bin': 'Financial News',
             'kaggle.bin': 'Kaggle',
             'natgas.bin': 'Natural Gas',
             'nasa.bin': 'NASA'}
    mems = [[i * 200 * 1024 ** 2 for i in range(1, 50)],
            [i * 20 * 1024 ** 2 for i in range(1, 50)],
            [i * 1024 ** 3 for i in range(1, 10)],
            [i * 25 * 1024 ** 2 for i in range(1, 20)],
            [i * 10 * 1024 ** 2 for i in range(1, 10)]]

    data = ddict(dict)

    for t, tmems in zip(trees, mems):
        ex_tree = exT.create_tree('SCIUNIT', t)
        if verbose and VERBOSE_PRINT_INFO:
            print_info(ex_tree, trees[t])
        for algorithm, l in zip(ALGOS, LINSHAPES):
            data[t][algorithm] = [(0, cost(ex_tree))]
            for cache_sz in tmems:
                ex_tree.cache_size = cache_sz
                algorithm(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
                if verbose:
                    print(f'{t}-{ALGOS[algorithm]} Cost (Cache:{cache_sz}) = {cost(ex_tree)}')
                data[t][algorithm].append((cache_sz / 1024**2, cost(ex_tree)))
                ex_tree.reset()
            plt.plot(*zip(*data[t][algorithm]), l, label=ALGOS[algorithm])
        plt.xlabel('Cache Size (in MB)')
        plt.ylabel('Storage Used by Algorithm (in Bytes)')
        plt.legend()
        plt.title(trees[t])
        if verbose and VERBOSE_SHOW_PLOT:
            plt.show()
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
    tree_args = [ci_node_factory,
                 di_node_factory,
                 an_node_factory]
    tree_names = ['CI', 'DI', 'AN']
    mems = [[i * 40 * 1024 ** 2 for i in range(1, 50)],
            [i * 50 * 1024 ** 2 for i in range(1, 50)],
            [i * 50 * 1024 ** 2 for i in range(1, 50)]]

    data = ddict(lambda: ddict(lambda: ddict(list)))

    for t, tmems, tname in zip(tree_args, mems, tree_names):
        for _ in range(EXP_COUNT):
            ex_tree = exT.create_tree('SIZE', 16, 4, 6, t)
            if verbose and VERBOSE_PRINT_INFO:
                print_info(ex_tree, tname)
            for algorithm in ALGOS:
                data[t][algorithm][0].append(cost(ex_tree))
                for cache_sz in tmems:
                    ex_tree.cache_size = cache_sz
                    algorithm(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
                    if verbose:
                        print(f'{tname}-{ALGOS[algorithm]} Cost (Cache:{cache_sz}) = {cost(ex_tree)}')
                    data[t][algorithm][cache_sz / 1024**2].append(cost(ex_tree))
                    ex_tree.reset()

        for algorithm, l in zip(data[t], LINSHAPES):
            x, y, dy = [], [], []
            for c in data[t][algorithm]:
                x.append(c)
                y.append(np.mean(data[t][algorithm][c]))
                dy.append(np.std(data[t][algorithm][c]))
            y, dy = np.array(y), np.array(dy)
            if PLOT_ERROR_BARS:
                plt.errorbar(x, y, yerr=dy, fmt=l, label=ALGOS[algorithm])
            else:
                plt.plot(x, y, l, label=ALGOS[algorithm])
            plt.fill_between(x, y - dy, y + dy, alpha=.2)

        plt.xlabel('Cache Size (in MB)')
        plt.ylabel('Total Cost')
        plt.legend()
        plt.title(tname)
        if verbose and VERBOSE_SHOW_PLOT:
            plt.show()
        plt.savefig(f'{tname}.jpg', dpi=1200)
        plt.clf()


def plot_cr(verbose=False):
    tree_args = [8, 16, 24, 32]
    mems = [[i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)]]

    data = ddict(lambda: ddict(list))

    for t, t_mems, l in zip(tree_args, mems, LINSHAPES):
        for _ in range(EXP_COUNT):
            ex_tree = exT.create_tree('SIZE', t, 4, 6, an_node_factory)
            if verbose and VERBOSE_PRINT_INFO:
                print_info(ex_tree, f'{t} Nodes')
            for cache_sz in t_mems:
                ex_tree.cache_size = cache_sz
                recurse_algorithm(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
                if verbose:
                    print(f'Cache:{cache_sz} {t} = {ex_tree.c_r}')
                data[t][cache_sz / 1024**2].append(ex_tree.c_r)
                ex_tree.reset()
        x, y, dy = [], [], []
        for c in data[t]:
            x.append(c)
            y.append(np.mean(data[t][c]))
            dy.append(np.std(data[t][c]))
        y, dy = np.array(y), np.array(dy)
        if PLOT_ERROR_BARS:
            plt.errorbar(x, y, yerr=dy, fmt=l, label=f'{t} Nodes')
        else:
            plt.plot(x, y, l, label=f'{t} Nodes')
        plt.fill_between(x, y - dy, y + dy, alpha=.2)
    plt.xlabel('Cache Size (in MB)')
    plt.ylabel('Total Checkpoints/Restores')
    plt.legend()
    plt.title('Checkpoints/Restores By Algorithm')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.savefig(f'c_r.jpg', dpi=1200)
    plt.clf()


def plot_storage(verbose=False):
    tree_args = [8, 16, 24, 32]
    mems = [[i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)]]

    data = ddict(lambda: ddict(list))

    for t, t_mems, l in zip(tree_args, mems, LINSHAPES):
        for _ in range(EXP_COUNT):
            ex_tree = exT.create_tree('SIZE', t, 4, 6, an_node_factory)
            if verbose and VERBOSE_PRINT_INFO:
                print_info(ex_tree, f'{t} Nodes')
            for cache_sz in t_mems:
                ex_tree.cache_size = cache_sz
                recurse_algorithm(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
                if verbose:
                    print(f'Cache:{cache_sz} {t} = {ex_tree.map_size}')
                data[t][cache_sz / 1024**2].append(ex_tree.map_size / 1024)
                ex_tree.reset()
        x, y, dy = [], [], []
        for c in data[t]:
            x.append(c)
            y.append(np.mean(data[t][c]))
            dy.append(np.std(data[t][c]))
        y, dy = np.array(y), np.array(dy)
        if PLOT_ERROR_BARS:
            plt.errorbar(x, y, yerr=dy, fmt=l, label=f'{t} Nodes')
        else:
            plt.plot(x, y, l, label=f'{t} Nodes')
        plt.fill_between(x, y - dy, y + dy, alpha=.2)
    plt.xlabel('Cache Size (in MB)')
    plt.ylabel('Total Storage Used (in KB)')
    plt.legend()
    plt.title('Storage Used By Algorithm')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.savefig(f'storage.jpg', dpi=1200)
    plt.clf()


def plot_algotime(verbose=False):
    tree_args = [8, 16, 24, 32]
    mem = 1024**4

    data = ddict(lambda: ddict(list))

    for algorithm, l in zip(ALGOS, LINSHAPES):
        for _ in range(EXP_COUNT):
            for t in tree_args:
                ex_tree = exT.create_tree('SIZE', t, 4, 6, an_node_factory)
                if verbose and VERBOSE_PRINT_INFO:
                    print_info(ex_tree, f'{t} Nodes')
                ex_tree.cache_size = mem
                begin = time.time()
                algorithm(ex_tree, verbose=False)
                end = time.time()
                if verbose:
                    print(f'{ALGOS[algorithm]}-{t} Time = {end - begin}')
                data[algorithm][t].append(end - begin)
        x, y, dy = [], [], []
        for t in data[algorithm]:
            x.append(t)
            y.append(np.mean(data[algorithm][t]))
            dy.append(np.std(data[algorithm][t]))
        y, dy = np.array(y), np.array(dy)
        if PLOT_ERROR_BARS:
            plt.errorbar(x, y, yerr=dy, fmt=l, label=ALGOS[algorithm])
        else:
            plt.plot(x, y, l, label=ALGOS[algorithm])
        plt.fill_between(x, y - dy, y + dy, alpha=.2)

    plt.xlabel('Tree Size')
    plt.ylabel('Algorithm Running Time')
    plt.legend()
    plt.title('Running Time')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.savefig('running_time.jpg', dpi=1200)
    plt.clf()
