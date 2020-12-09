from functools import singledispatch
from itertools import islice


def create_registerer():
    @singledispatch
    def call(key, *args, **kwargs):
        """Use this function to call a registered function based on key"""
        return call.map[key](*args, **kwargs)

    @call.register
    def _(key: int, *args, **kwargs):
        """Use index rather than the key"""
        assert 1 <= key <= len(call.map)
        return next(islice(call.map.values(),
                           key - 1,
                           len(call.map)))(*args, **kwargs)

    call.map = {}

    def register_callee(key):
        """Use this decorator to register a callee"""
        assert not isinstance(key, int)

        def register(callee):
            call.map[key] = callee
            call.__doc__ += f'\n{len(call.map)}. {key}'
            return callee

        if callable(key):
            creator, key = key, key.__name__
            return register(creator)
        else:
            return register

    return call, register_callee


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


def non_dfs_cost(ex_tree):
    """Compute the cost for a non-DFS solution"""
    return sum(node.data.r_cost * sum(node.data.p_computed) for node in ex_tree.all_nodes_itr())


def cost(ex_tree):
    """Auto compute for both DFS and non-DFS solution"""
    if ex_tree.get_node(ex_tree.root).data.p_computed:
        return non_dfs_cost(ex_tree)
    elif ex_tree.get_node(ex_tree.root).data.recursive_cache:
        return ex_tree.total_cost
    else:
        return dfs_cost(ex_tree)
