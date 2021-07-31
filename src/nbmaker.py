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
    nbformat.write(notebook, os.path.join(sys.argv[2], f'{sys.argv[1]}_{i}.ipynb'))
