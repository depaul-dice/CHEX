import random
from importlib import import_module

from treelib import Tree

from util import create_registerer


class NodeData:

    def __init__(self, r_cost, c_size):
        self.r_cost = r_cost  # corresponds to r in equation
        self.c_size = c_size  # corresponds to c in equation
        self.x_in_cache = False  # corresponds to x in equation
        self.p_computed = []  # corresponds to p in equation
        self.recursive_cache = {}

    def reset(self):
        self.x_in_cache = False
        self.p_computed = []
        self.recursive_cache = {}


class ExecutionTree(Tree):

    def reset(self):
        for node in self.all_nodes_itr():
            node.data.reset()


create_tree, register_tree_creator = create_registerer()


def fixed_node_factory(_):
    """Create a Node of fixed cost and size"""
    r_cost, c_size = 1, 1
    return NodeData(r_cost, c_size)


def rand_node_factory(height):
    """Create a Node of random cost and size based on height"""
    height = max(1, height)
    r_cost_lim = 10 * height
    c_size_lim = 10 // height
    r_cost = random.randint(max(1, r_cost_lim - 10), r_cost_lim + 10)
    c_size = random.randint(max(1, c_size_lim - 10), c_size_lim + 10)
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
    for i in range(1, (k ** (height + 1) - 1) // (k - 1)):
        if random.choice([True, False]) and tree.contains(f'n{(i - 1) // k}'):
            tree.create_node(f'N{i}', f'n{i}', parent=f'n{(i - 1) // k}',
                             data=node_factory(tree.depth(f'n{(i - 1) // k}') + 1))
    return tree


@register_tree_creator('KARY')
def kary_tree_creator(k, height, node_factory=fixed_node_factory):
    """Create a perfect k-ary tree with the given k and height"""
    tree = ExecutionTree()
    tree.create_node("N0", "n0", data=node_factory(0))
    for i in range(1, (k ** (height + 1) - 1) // (k - 1)):
        tree.create_node(f'N{i}', f'n{i}', parent=f'n{(i - 1) // k}',
                         data=node_factory(tree.depth(f'n{(i - 1) // k}') + 1))
    return tree


@register_tree_creator('SCIUNIT')
def sciunit_tree_creator(tree_binary, sciunit_tree_module_path='sciunit_tree'):
    """Create a tree using the real world sciunit tree"""
    sciunit_tree = import_module(sciunit_tree_module_path)
    sciunit_execution_tree, _ = sciunit_tree.tree_load(tree_binary)

    tree = ExecutionTree()

    def recursive_fill(node, parent=None):
        tree.create_node(node.hash, node.hash, parent=parent.hash if parent else None,
                         data=NodeData(node.time, node.size))
        for child in node.children:
            recursive_fill(node.children[child], node)

    sciunit_execution_tree.time = sciunit_execution_tree.size = 1
    recursive_fill(sciunit_execution_tree)
    return tree
