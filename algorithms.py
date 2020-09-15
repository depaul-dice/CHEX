def check_constraints(ex_tree, node, paths):
    """Check if any cache constraints are violated along the paths where the node is present"""
    for path in paths:
        if node.identifier in path:
            path_nodes = map(lambda path_node: ex_tree.get_node(path_node).data, path)
            if sum(path_node.c_size for path_node in path_nodes if path_node.x_in_cache) > ex_tree.cache_size:
                return False
    return True


def dfs_cost(ex_tree, node=None, force_cost=None):
    """Compute cost of computing entire tree recursively"""
    if node is None:
        ex_tree.total_r_cost = 0
        node = ex_tree.get_node(ex_tree.root)
    for child in ex_tree.children(node.identifier):
        dfs_cost(ex_tree, child, force_cost)
    if node.is_leaf():
        node.data.y = 1
    else:
        # compute y value for all children
        node.data.y = 0  # reinitialize for repeated runs
        for child in ex_tree.children(node.identifier):
            node.data.y += 1 + (child.data.y - 1) * (1 - child.data.x_in_cache)

    if not force_cost:
        ex_tree.total_r_cost += node.data.r_cost * (1 + (node.data.y - 1) * (1 - node.data.x_in_cache))
    else:
        ex_tree.total_r_cost += force_cost * (1 + (node.data.y - 1) * (1 - node.data.x_in_cache))
    return ex_tree.total_r_cost


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


def non_dfs_cost(ex_tree):
    """Compute the cost for a non-DFS solution"""
    return sum(node.data.r_cost * sum(node.data.p_computed) for node in ex_tree.all_nodes_itr())
