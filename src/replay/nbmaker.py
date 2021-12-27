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

# File purpose: Generate Notebooks from source code available in `tree.bin` files.
# Usage: For Alice to re-generate notebooks that were used in creating the `tree.bin` file.

import os
import sys
import shutil
import pickle as pkl
from copy import deepcopy as copy

import nbformat

assert len(sys.argv) == 3, 'Invalid Arguments'


def recursive_fill(node, nb=None):
    if nb is None:
        nb = nbformat.v4.new_notebook()
    else:
        nb = copy(nb)
        nb.cells.append(nbformat.v4.new_code_cell(node.code))
    if len(node.children) == 0:
        return [nb]
    else:
        return sum((recursive_fill(child, nb) for child in node.children.values()), start=[])


shutil.rmtree(sys.argv[2], ignore_errors=True)
os.mkdir(sys.argv[2])

for i, notebook in enumerate(recursive_fill(pkl.load(open(sys.argv[1], 'rb'))[0])):
    nbformat.write(notebook, os.path.join(sys.argv[2], f'{os.path.split(sys.argv[1])[1]}_{i}.ipynb'))
