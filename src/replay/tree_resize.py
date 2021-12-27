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

# File purpose: Utility script to take subset of a tree for different kinds of testing

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
