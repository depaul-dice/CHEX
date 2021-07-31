import random
from copy import deepcopy as copy

import sciunit_tree


def resize(tree_binary, new_size, new_tree_binary):
    sciunit_execution_tree, _ = sciunit_tree.tree_load(tree_binary)

    def rec_nbs(node, nbl=None):
        if nbl is None:
            nbl = []
        else:
            nbl = copy(nbl)
            nbl.append((node.code, node.time, node.size))
        if len(node.children) == 0:
            return [nbl]
        else:
            return sum((rec_nbs(child, nbl) for child in node.children.values()), start=[])

    nbs = random.sample(rec_nbs(sciunit_execution_tree), new_size)

    new_tree = sciunit_tree.Tree()
    for nb in nbs:
        nd = new_tree
        for code, time, size in nb:
            added, nd = nd.traverse(code)
            if added:
                nd.time = time
                nd.size = size

    sciunit_tree.tree_dump(new_tree, 0, new_tree_binary)


if __name__ == '__main__':
    resize('../data/kaggle.bin', 10, '../data/kaggle_small.bin')
