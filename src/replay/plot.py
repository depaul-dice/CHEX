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

# File purpose: Generate all plots present in the paper

import random
import time
from collections import defaultdict as ddict

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker as mtick

import ExecutionTree as exT
from util import *
from algorithms import *
from solver_algorithms import *


# plt.rc('font', size=14, weight='bold')
plt.rc('font', size=16)
plt.rc('errorbar', capsize=10)

PLOT_ERROR_BARS = False
PLOT_FILL_BETWEEN = False
PLOT_SHOW_TITLE = False
PLOT_YMIN_ZERO = False
PLOT_Y_PERC = True
PLOT_Y0_BOLD = True
VERBOSE_SHOW_PLOT = False
ALGORITHM_VERBOSE = False
VERBOSE_PRINT_INFO = True
EXP_COUNT = 10

ALGOS = {prp_v1: 'PRP-v1',
         prp_v2: 'PRP-v2',
         pc: 'PC',
         # optimal_dfs: 'Couenne Optimal DFS',
         # optimal: 'Couenne Optimal',
         lfu: 'LFU'}

LINSHAPES = ['*-', '.-', 'x-', '<-', 's-', 'D-', '>-']

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
    mems = [[i * 1.8 * 1024 ** 3  for i in range(1, 21)],
            [i * 0.38 * 1024 ** 3  for i in range(1, 21)],
            [i * 2 * 1024 ** 3  for i in range(1, 21)],
            [i * 0.1 * 1024 ** 3  for i in range(1, 21)],
            [i * 0.05 * 1024 ** 3  for i in range(1, 21)],
            [i * 11 * 1024 ** 3  for i in range(1, 21)]]
    label_ps = [(3, 3), (3, 2), (3, 3), (3, 3), (3, 3), (3, 3)]

    data = ddict(dict)

    for t, tmems, p in zip(trees, mems, label_ps):
        tmems = [int(tmem) for tmem in tmems]
        ex_tree = exT.create_tree('SCIUNIT', f'data/{t}')
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
        # plt.xlabel(LABEL_CACHE_SIZE(p[0]))
        plt.xlabel(f'Cache Size (X = {tmems[0] / 1024**p[0]:.2f} {LABEL_CACHE_SIZE_MAP[p[0]]})')
        plt.ylabel(f'Total Replay Cost (% of {cost(ex_tree):.0f} s)')
        # plt.ylabel(LABEL_COMPUTE_COST(p[1]))
        plt.legend()
        if PLOT_YMIN_ZERO:
            plt.ylim(ymin=0)
        if PLOT_Y_PERC:
            plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(cost(ex_tree) / 10**p[1]))
            # plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(tmems[-1] / 1024**p[0]))
            # xticks = plt.xticks()[0]
            xticks = [i * tmems[0] / 1024**p[0] for i in [0, 4, 8, 12, 16, 20]]
            plt.xticks(ticks=xticks, labels=[f'{x / (tmems[0] / 1024**p[0]):.0f}X' for x in xticks])
        if PLOT_SHOW_TITLE:
            plt.title(trees[t])
        if PLOT_Y0_BOLD:
            plt.draw()
            plt.gca().get_yticklabels()[1].set_color('red')
            plt.gca().get_yticklabels()[1].set_weight('bold')
            while False:
                try:
                    print(eval(input('>> ')))
                except Exception:
                    pass
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
        if PLOT_YMIN_ZERO:
            plt.ylim(ymin=0)
        if PLOT_SHOW_TITLE:
            plt.title(tname)
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
                print_info(ex_tree, f'TS: {t}')
            for cache_sz in t_mems:
                ex_tree.cache_size = cache_sz
                pc(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
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
            plt.errorbar(x, y, yerr=dy, fmt=l, label=f'TS: {t}')
        else:
            plt.plot(x, y, l, label=f'TS: {t}')
        if PLOT_FILL_BETWEEN:
            plt.fill_between(x, y - dy, y + dy, alpha=.2)
    plt.xlabel(LABEL_CACHE_SIZE(2))
    plt.ylabel('Total Checkpoints/Restores')
    plt.legend()
    if PLOT_YMIN_ZERO:
        plt.ylim(ymin=0)
    if PLOT_SHOW_TITLE:
        plt.title('Checkpoints/Restores By Algorithm')
    plt.savefig(f'c_r.jpg', dpi=1200, bbox_inches='tight')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.clf()


def plot_storage(verbose=False):
    tree_args = [(16, pc), (16, prp_v2), (32, pc), (32, prp_v2)]
    mems = [[i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)]]

    data = ddict(lambda: ddict(list))

    for (t, algo), t_mems, l in zip(tree_args, mems, LINSHAPES):
        for _ in range(EXP_COUNT):
            ex_tree = exT.create_tree('SIZE', t, 4, 6, an_node_factory)
            if verbose and VERBOSE_PRINT_INFO:
                print_info(ex_tree, f'TS: {t}')
            for cache_sz in t_mems:
                ex_tree.cache_size = cache_sz
                algo(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
                if verbose:
                    print(f'Cache:{cache_sz} {t}-{ALGOS[algo]} = {ex_tree.map_size}')
                data[t, algo][cache_sz / 1024**2].append(ex_tree.map_size / 1024)
                ex_tree.reset()
        x, y, dy = [], [], []
        for c in data[t, algo]:
            x.append(c)
            y.append(np.mean(data[t, algo][c]))
            dy.append(np.std(data[t, algo][c]))
        y, dy = np.array(y), np.array(dy)
        if PLOT_ERROR_BARS:
            plt.errorbar(x, y, yerr=dy, fmt=l, label=f'TS: {t} Algo: {ALGOS[algo]}')
        else:
            plt.plot(x, y, l, label=f'TS: {t} Algo: {ALGOS[algo]}')
        if PLOT_FILL_BETWEEN:
            plt.fill_between(x, y - dy, y + dy, alpha=.2)
    plt.xlabel(LABEL_CACHE_SIZE(2))
    plt.ylabel('Total Storage Used (in KB)')
    plt.legend()
    if PLOT_YMIN_ZERO:
        plt.ylim(ymin=0)
    if PLOT_SHOW_TITLE:
        plt.title('Storage Used By Algorithm')
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
                pc(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
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
    if PLOT_YMIN_ZERO:
        plt.ylim(ymin=0)
    if PLOT_SHOW_TITLE:
        plt.title('No. of Versions that can be run with given cost')
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
                    print_info(ex_tree, f'TS: {t}')
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

    plt.xlabel('Tree Size (TS)')
    plt.ylabel('Algorithm Running Time (in mS)')
    plt.legend()
    if PLOT_YMIN_ZERO:
        plt.ylim(ymin=0)
    if PLOT_SHOW_TITLE:
        plt.title('Running Time')
    plt.savefig('running_time.jpg', dpi=1200, bbox_inches='tight')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.clf()


def plot_timevstorage(verbose=False):
    tree_args = [16, 24, 32, 64]
    mems = [[i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)],
            [i * 200 * 1024 ** 2 for i in range(1, 15)]]

    data = ddict(lambda: ddict(list))

    for t, t_mems, l in zip(tree_args, mems, LINSHAPES):
        for _ in range(EXP_COUNT):
            ex_tree = exT.create_tree('SIZE', t, 4, 6, an_node_factory)
            if verbose and VERBOSE_PRINT_INFO:
                print_info(ex_tree, f'TS: {t}')
            for cache_sz in t_mems:
                ex_tree.cache_size = cache_sz
                begin = time.time()
                pc(ex_tree, verbose=False)
                end = time.time()
                if verbose:
                    print(f'Cache:{cache_sz} {t} Time = {end - begin}')
                data[t][cache_sz / 1024**2].append(1000 * (end - begin))
                ex_tree.reset()
        x, y, dy = [], [], []
        for c in data[t]:
            x.append(c)
            y.append(np.mean(data[t][c]))
            dy.append(np.std(data[t][c]))
        y, dy = np.array(y), np.array(dy)
        if PLOT_ERROR_BARS:
            plt.errorbar(x, y, yerr=dy, fmt=l, label=f'TS: {t}')
        else:
            plt.plot(x, y, l, label=f'TS: {t}')
        if PLOT_FILL_BETWEEN:
            plt.fill_between(x, y - dy, y + dy, alpha=.2)
    plt.xlabel(LABEL_CACHE_SIZE(2))
    plt.ylabel('Total Time Taken (in msec)')
    plt.legend()
    if PLOT_YMIN_ZERO:
        plt.ylim(ymin=0)
    if PLOT_SHOW_TITLE:
        plt.title('Time Taken By Algorithm')
    plt.savefig(f'tvs.jpg', dpi=1200, bbox_inches='tight')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.clf()


def plot_couenne(verbose=False):
    sizes = list(range(10))
    data = {}
    for sz in sizes:
        data[sz] = []
        for _ in range(EXP_COUNT):
            ex_tree = exT.create_tree('SIZE', sz, 3, 5, an_node_factory)
            if verbose and VERBOSE_PRINT_INFO:
                print_info(ex_tree, f'TS: {sz}')
            ex_tree.cache_size = 1024**3
            time_start = time.time()
            optimal(ex_tree, verbose=verbose and ALGORITHM_VERBOSE)
            data[sz].append(time.time() - time_start)

    x, y, dy = [], [], []
    for sz in data:
        x.append(sz)
        y.append(np.mean(data[sz]))
        dy.append(np.std(data[sz]))
    y, dy = np.array(y) * 1000, np.array(dy) * 1000
    if PLOT_ERROR_BARS:
        plt.errorbar(x, y, yerr=dy)
    else:
        plt.plot(x, y)
    if PLOT_FILL_BETWEEN:
        plt.fill_between(x, y - dy, y + dy, alpha=.2)

    plt.xlabel('Tree Size')
    plt.ylabel('Algorithm Running Time (in sec)')
    plt.savefig(f'couenne.jpg', dpi=1200, bbox_inches='tight')
    if verbose and VERBOSE_SHOW_PLOT:
        plt.show()
    plt.clf()


if __name__ == '__main__':
    plot_real(verbose=True)
    plot_synthetic(verbose=True)
    plot_storage(verbose=True)
    plot_cr(verbose=True)
    plot_versions(verbose=True)
    plot_algotime(verbose=True)
    plot_couenne(verbose=True)
    plot_timevstorage(verbose=True)
