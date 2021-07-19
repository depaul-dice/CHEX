import sys
from util import dfs_cost, paths_to_leaves, checkpoints_restores
from itertools import count
from collections import defaultdict as ddict


def _check_constraints(ex_tree, node, paths):
    """Check if any cache constraints are violated along the paths where the node is present"""
    for path in paths:
        if node.identifier in path:
            path_nodes = map(lambda path_node: ex_tree.get_node(path_node).data, path)
            if sum(path_node.c_size for path_node in path_nodes if path_node.x_in_cache) > ex_tree.cache_size:
                return False
    return True


def dfs_algorithm(ex_tree, cost_compare, verbose=False):
    """General purpose algorithm for DFS using a custom cost comparison function"""
    paths = ex_tree.paths_to_leaves()
    nodes = set(ex_tree.filter_nodes(lambda tree_node: not tree_node.is_leaf()))

    while True:
        min_node, min_cost = None, float('inf')
        for node in nodes:
            node.data.x_in_cache = True
            if _check_constraints(ex_tree, node, paths):
                if cost_compare(new_cost := dfs_cost(ex_tree), node, min_cost, min_node):
                    min_node, min_cost = node, new_cost
            node.data.x_in_cache = False
        if not min_node:
            break
        min_node.data.x_in_cache = True
        nodes.remove(min_node)
    if verbose:
        ex_tree.show(data_property='x_in_cache')


def dfs_algorithm_v1(ex_tree, verbose=False):
    """Run DFS algorithm by comparing just time saved in each iteration"""
    return dfs_algorithm(ex_tree, lambda new_cost, new_node, min_cost, min_node: new_cost < min_cost, verbose)


def dfs_algorithm_v2(ex_tree, verbose=False):
    """Run DFS algorithm by comparing time saved per cache usage in each iteration"""
    def cost_compare(new_cost, new_node, min_cost, min_node):
        if min_node is None:
            return True
        return (new_cost / new_node.data.c_size) < (min_cost / min_node.data.c_size)
    return dfs_algorithm(ex_tree, cost_compare, verbose)


def recurse_algorithm(ex_tree, verbose=False):

    def recurse(node, cache, parent_cost=0):
        if cache in node.data.recursive_cache:
            return sum(recurse(cache_node, cache - (node.data.c_size if cached else 0))
                       if cache_node != node
                       else node.data.r_cost
                       for cache_node, cached in node.data.recursive_cache[cache])

        node.data.recursive_cache[cache] = [(node, False)]
        total_cost = node.data.r_cost

        if node.is_leaf():
            return total_cost

        with_extra_cache, without_extra_cache = [], []

        if cache < node.data.c_size:
            for child in ex_tree.children(node.identifier):
                with_extra_cache.append((recurse(child, cache, node.data.r_cost + parent_cost), child))
        else:
            tie_breaker = count()
            for child in ex_tree.children(node.identifier):
                less_cache_cost = recurse(child, cache - node.data.c_size)
                more_cache_cost = recurse(child, cache, node.data.r_cost + parent_cost)
                if less_cache_cost - more_cache_cost <= node.data.r_cost + parent_cost:
                    without_extra_cache.append((less_cache_cost - more_cache_cost, next(tie_breaker),
                                                less_cache_cost, child))
                else:
                    with_extra_cache.append((more_cache_cost, child))

        if verbose:
            print(node, cache)
            print('without_extra_cache', *without_extra_cache, sep='\n')
            print('with_extra_cache', *with_extra_cache, sep='\n')

        if without_extra_cache:
            node.data.recursive_cache[cache][0] = (node, True)
            without_extra_cache.sort()
            # Process items where all use parent in cache
            for _, _, less_cache_cost, child in without_extra_cache:
                node.data.recursive_cache[cache].append((child, True))
                total_cost += less_cache_cost

        if with_extra_cache:
            # For first child, skip re-computation
            first = True
            # Process children by recomputing parent
            for more_cache_cost, child in with_extra_cache:
                if first:
                    first = False
                else:
                    node.data.recursive_cache[cache].append((node, False))
                    total_cost += node.data.r_cost + parent_cost
                node.data.recursive_cache[cache].append((child, False))
                total_cost += more_cache_cost
        else:
            # Use cache for last without cache if nothing else exists
            diff, _, _, child = without_extra_cache[-1]
            node.data.recursive_cache[cache][-1] = (child, False)
            total_cost -= diff

        return total_cost

    total_cost_ret = recurse(ex_tree.get_node(ex_tree.root), ex_tree.cache_size)
    if verbose:
        ex_tree.show(data_property='recursive_cache')
        print(f'{total_cost_ret=}')
    ex_tree.total_cost = total_cost_ret
    ex_tree.map_size = sys.getsizeof(ex_tree)
    ex_tree.c_r = checkpoints_restores(ex_tree)
    return total_cost_ret


def online_algorithm(ex_tree, verbose=False):
    ex_tree.get_node(ex_tree.root).data.recursive_cache = True
    ex_tree.total_cost = 0
    freq = ddict(int)
    depth = {}
    cache = {}
    for path in paths_to_leaves(ex_tree):
        next_d = 0
        for d, node in enumerate(path):
            freq[node] += 1
            depth[node] = d
            if node in cache: next_d = d + 1
        while next_d < len(path):
            ex_tree.total_cost += node.data.r_cost
            node = path[next_d]
            next_d += 1
            cache_nodes = list(cache)
            cache_nodes.append(node)
            cache[node] = node.data.c_size
            cache_nodes.sort(key=lambda n: (freq[n], -depth[n]))
            new_cache = {}
            while cache_nodes and sum(new_cache.values()) + cache[cache_nodes[-1]] <= ex_tree.cache_size:
                new_cache[cache_nodes[-1]] = cache[cache_nodes[-1]]
                cache_nodes.pop()
            cache = new_cache
