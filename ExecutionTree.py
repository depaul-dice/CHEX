from random import randint, choice
from functools import singledispatch
from itertools import islice

from treelib import Tree


class NodeData:

    def __init__(self, r_cost, c_size):
        self.r_cost = r_cost  # corresponds to r in equation
        self.c_size = c_size  # corresponds to c in equation
        self.x_in_cache = False  # corresponds to x in equation
        self.y = 0  # corresponds to y in equation
        self.numChildren = 0

    def reset(self):
        self.x_in_cache = False
        self.y = 0
        self.numChildren = 0


class ExecutionTree(Tree):
    def reset(self):
        for node in self.all_nodes():
            node.data.reset()


@singledispatch
def create_tree(creation_type, *args, **kwargs):
    """Create A Tree Based on Functions decorated with @register_tree_creator"""
    return create_tree.tree_creator_map[creation_type](*args, **kwargs)


@create_tree.register
def _(creation_type: int, *args, **kwargs):
    """Alternative that finds the function using index rather than the key"""
    assert 1 <= creation_type <= len(create_tree.tree_creator_map)
    return next(islice(create_tree.tree_creator_map.values(),
                       creation_type - 1,
                       len(create_tree.tree_creator_map)))(*args, **kwargs)


create_tree.tree_creator_map = {}


def register_tree_creator(creation_type):
    """Use this decorator to register a tree creator with create_tree"""
    assert not isinstance(creation_type, int)

    def register(tree_creator):
        create_tree.tree_creator_map[creation_type] = tree_creator
        create_tree.__doc__ += f'\n{len(create_tree.tree_creator_map)}. {creation_type}'
        return tree_creator

    if callable(creation_type):
        creator, creation_type = creation_type, creation_type.__name__
        return register(creator)
    else:
        return register


def fixed_node_factory(_):
    """Create a Node of fixed cost and size"""
    r_cost, c_size = 1, 1
    return NodeData(r_cost, c_size)


def rand_node_factory(height):
    """Create a Node of random cost and size based on height"""
    height = max(1, height)
    r_cost_lim = 100 * height
    c_size_lim = 100 // height
    r_cost = randint(max(0, r_cost_lim - 10), r_cost_lim + 10)
    c_size = randint(max(0, c_size_lim - 10), c_size_lim + 10)
    return NodeData(r_cost, c_size)


@register_tree_creator('FIXED')
def fixed_tree_creator(node_factory=fixed_node_factory):
    """Create A Fixed Tree"""
    tree = ExecutionTree()
    tree.create_node("A", "a", data=node_factory(0))  # root node
    tree.create_node("B", "b", parent="a", data=node_factory(1))
    tree.create_node("C", "c", parent="b", data=node_factory(2))
    tree.create_node("D", "d", parent="b", data=node_factory(2))
    tree.create_node("E", "e", parent="d", data=node_factory(3))
    tree.create_node("F", "f", parent="d", data=node_factory(3))
    tree.create_node("G", "g", parent="f", data=node_factory(4))
    tree.create_node("H", "h", parent="f", data=node_factory(4))
    tree.create_node("I", "i", parent="f", data=node_factory(4))
    tree.create_node("J", "j", parent="h", data=node_factory(5))
    tree.create_node("K", "k", parent="j", data=node_factory(6))
    tree.create_node("L", "l", parent="k", data=node_factory(7))
    tree.create_node("M", "m", parent="j", data=node_factory(6))
    tree.create_node("N", "n", parent="i", data=node_factory(5))
    tree.create_node("O", "o", parent="n", data=node_factory(6))
    return tree


@register_tree_creator('BRANCH')
def branch_tree_creator(k, height, node_factory=rand_node_factory):
    """Create a random k-ary with the given k and height"""
    tree = ExecutionTree()
    tree.create_node("N0", "n0", data=node_factory(0))
    for i in range(1, (k**(height + 1) - 1) // (k - 1)):
        if choice([True, False]) and tree.contains(f'n{(i - 1) // k}'):
            tree.create_node(f'N{i}', f'n{i}', parent=f'n{(i - 1) // k}',
                             data=node_factory(tree.depth(f'n{(i - 1) // k}') + 1))
    return tree


@register_tree_creator('KARY')
def kary_tree_creator(k, height, node_factory=fixed_node_factory):
    """Create a perfect k-ary tree with the given k and height"""
    tree = ExecutionTree()
    tree.create_node("N0", "n0", data=node_factory(0))
    for i in range(1, (k**(height + 1) - 1) // (k - 1)):
        tree.create_node(f'N{i}', f'n{i}', parent=f'n{(i - 1) // k}',
                         data=node_factory(tree.depth(f'n{(i - 1) // k}') + 1))
    return tree
