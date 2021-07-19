import random
import time
from collections import defaultdict as ddict

import numpy as np
from matplotlib import pyplot as plt

import ExecutionTree as exT
from util import *
from algorithms import *
from solver_algorithms import *


# plt.rc('font', size=14, weight='bold')
plt.rc('font', size=16)
plt.rc('errorbar', capsize=10)

PLOT_ERROR_BARS = True
PLOT_FILL_BETWEEN = False
VERBOSE_SHOW_PLOT = False
ALGORITHM_VERBOSE = False
VERBOSE_PRINT_INFO = True
EXP_COUNT = 10

ALGOS = {dfs_algorithm_v1: 'PRP-v1',
         dfs_algorithm_v2: 'PRP-v2',
         recurse_algorithm: 'PC',
         # optimal_dfs: 'Couenne Optimal DFS',
         # optimal: 'Couenne Optimal',
         online_algorithm: 'LFU'}

LINSHAPES = ['*-', '.-', 'x-', '<-', '>-', 's-', 'D-']

LABEL_COMPUTE_COST = lambda p: f'Total Replay Cost (in $10^{p}$ sec)'
LABEL_CACHE_SIZE_MAP = {2: 'MB', 3: 'GB'}
LABEL_CACHE_SIZE = lambda p: f'Cache Size (in {LABEL_CACHE_SIZE_MAP[p]})'

def plot_real(verbose=False):
    trees = {'epruning.bin': 'Epruning',
             'financial_news.bin': 'Financial News',
             'kaggle.bin': 'Kaggle',
             'natgas.bin': 'Natural Gas',
             'nasa.bin': 'NASA',
             'timeseries.bin': 'TimeSeries'}
    mems = [[i * 200 * 1024 ** 2 for i in range(1, 50)],
            [i * 20 * 1024 ** 2 for i in range(1, 50)],
            [i * 1024 ** 3 for i in range(1, 10)],
            [i * 50 * 1024 ** 2 for i in range(1, 20)],
            [i * 10 * 1024 ** 2 for i in range(1, 10)],
            [i * 4 * 1024 ** 3 for i in range(1, 20)]]
    label_ps = [(3, 3), (2, 2), (3, 3), (2, 3), (2, 3), (3, 3)]

    data = ddict(dict)

    for t, tmems, p in zip(trees, mems, label_ps):
        ex_tree = exT.create_tree('SCIUNIT', t)
        if verbose and VERBOSE_PRINT_INFO:
            print_info(ex_tree, trees[t])
        for algorithm, l in zip(ALGOS, LINSHAPES):
            data[t][algorithm] = [(0, cost(ex_tree) / 10**p[1])]
            for cache_sz in tmems:
                ex_tree.cache_size = cache_sz
                algorithm(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
                if verbose:
                    print(f'{t}-{ALGOS[algorithm]} Cost (Cache:{cache_sz}) = {cost(ex_tree)}')
                data[t][algorithm].append((cache_sz / 1024**p[0], cost(ex_tree) / 10**p[1]))
                ex_tree.reset()
            plt.plot(*zip(*data[t][algorithm]), l, label=ALGOS[algorithm])
        plt.xlabel(LABEL_CACHE_SIZE(p[0]))
        plt.ylabel(LABEL_COMPUTE_COST(p[1]))
        plt.legend()
        # plt.title(trees[t])
        plt.savefig(f'{t}.jpg', dpi=1200, bbox_inches='tight')
        if verbose and VERBOSE_SHOW_PLOT:
            plt.show()
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
    mems = [[i * 250 * 1024**2 for i in range(1, 11)],
            [i * 250 * 1024**2 for i in range(1, 11)],
            [i * 250 * 1024**2 for i in range(1, 11)]]

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
                    data[t][algorithm][cache_sz / 1024**3].append(cost(ex_tree))
                    ex_tree.reset()

        for algorithm, l in zip(data[t], LINSHAPES):
            x, y, dy = [], [], []
            for c in data[t][algorithm]:
                x.append(c)
                y.append(np.mean(data[t][algorithm][c]))
                dy.append(np.std(data[t][algorithm][c]))
            y, dy = np.array(y) / 10**3, np.array(dy) / 10**3
            if PLOT_ERROR_BARS:
                plt.errorbar(x, y, yerr=dy, fmt=l, label=ALGOS[algorithm])
            else:
                plt.plot(x, y, l, label=ALGOS[algorithm])
            if PLOT_FILL_BETWEEN:
                plt.fill_between(x, y - dy, y + dy, alpha=.2)

        plt.xlabel(LABEL_CACHE_SIZE(3))
        plt.ylabel(LABEL_COMPUTE_COST(3))
        plt.legend()
        # plt.title(tname)
        plt.savefig(f'{tname}.jpg', dpi=1200, bbox_inches='tight')
        if verbose and VERBOSE_SHOW_PLOT:
            plt.show()
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
        if PLOT_FILL_BETWEEN:
            plt.fill_between(x, y - dy, y + dy, alpha=.2)
    plt.xlabel(LABEL_CACHE_SIZE(2))
    plt.ylabel('Total Checkpoints/Restores')
    plt.legend()
    # plt.title('Checkpoints/Restores By Algorithm')
    plt.savefig(f'c_r.jpg', dpi=1200, bbox_inches='tight')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
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
        if PLOT_FILL_BETWEEN:
            plt.fill_between(x, y - dy, y + dy, alpha=.2)
    plt.xlabel(LABEL_CACHE_SIZE(2))
    plt.ylabel('Total Storage Used (in KB)')
    plt.legend()
    # plt.title('Storage Used By Algorithm')
    plt.savefig(f'storage.jpg', dpi=1200, bbox_inches='tight')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.clf()


def plot_versions(verbose=False):
    mems = [0, 256 * 1024 ** 2, 512 * 1024 ** 2, 1024 ** 3]
    max_leaves = list(range(1, 33))

    data = ddict(lambda: ddict(list))

    for leaves in max_leaves:
        for e in range(EXP_COUNT):
            ex_tree = exT.create_tree('COUNT', leaves, 4, 6, an_node_factory)
            if verbose and VERBOSE_PRINT_INFO:
                print_info(ex_tree, f'{leaves} Leaves')
            for mem in mems:
                ex_tree.cache_size = mem
                recurse_algorithm(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
                if verbose:
                    print(f'Cache:{mem} {leaves} Leaves = {cost(ex_tree)}')
                data[mem][e].append((leaves, cost(ex_tree)))
                ex_tree.reset()

    tmax = min(max(max(c for _, c in data[m][e]) for e in data[m]) for m in data)
    x = np.linspace(0, tmax, 1000)
    for mem, l in zip(mems, LINSHAPES):
        ys = [[] for _ in x]
        for e in data[mem]:
            i, pl = 0, 0
            for le, c in data[mem][e]:
                while i < len(x) and x[i] < c:
                    ys[i].append(pl)
                    i += 1
                pl = le
            while i < len(x):
                ys[i].append(pl)
                i += 1
        ys = np.array(ys)
        y = np.mean(ys, axis=1)
        dy = np.std(ys, axis=1)
        # if PLOT_ERROR_BARS:
        #     plt.errorbar(x / 1000, y, yerr=dy, fmt=l, label=f'{mem // 1024 ** 2} MB')
        # else:
        #     plt.plot(x / 1000, y, l, label=f'{mem // 1024 ** 2} MB')
        # if PLOT_FILL_BETWEEN:
        #     plt.fill_between(x / 1000, y - dy, y + dy, alpha=.2)
        plt.plot(x / 1000, y, label=f'{mem // 1024 ** 2} MB')
        plt.fill_between(x / 1000, y - dy, y + dy, alpha=.2)

    plt.xlabel('Available Cost (in $10^3$ sec)')
    plt.ylabel('No. of Versions')
    plt.legend()
    # plt.title('No. of Versions that can be run with given cost')
    plt.savefig('versions.jpg', dpi=1200, bbox_inches='tight')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
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
        y, dy = np.array(y) * 1000, np.array(dy) * 1000
        if PLOT_ERROR_BARS:
            plt.errorbar(x, y, yerr=dy, fmt=l, label=ALGOS[algorithm])
        else:
            plt.plot(x, y, l, label=ALGOS[algorithm])
        if PLOT_FILL_BETWEEN:
            plt.fill_between(x, y - dy, y + dy, alpha=.2)

    plt.xlabel('Tree Size')
    plt.ylabel('Algorithm Running Time (in mS)')
    plt.legend()
    # plt.title('Running Time')
    plt.savefig('running_time.jpg', dpi=1200, bbox_inches='tight')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.clf()
