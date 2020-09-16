from util import dfs_cost


def check_constraints(ex_tree, node, paths):
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
            if check_constraints(ex_tree, node, paths):
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
