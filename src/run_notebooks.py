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

# File purpose: Run the input notebooks and generate the tree using CRIU to measure checkpoint sizes.
# Usage: For Alice to run a set of notebooks and create a `tree.bin`.

import os
import sys
import time
import signal
import glob
from contextlib import contextmanager

import nbformat

from IPython.core import interactiveshell

import sciunit_tree


@contextmanager
def iter_paths(path):
    def path_generator():
        yield from glob.glob(path + '/*.ipynb')

    try:
        yield path_generator()
    finally:
        pass


CRIU_IMAGE_PATH = 'criu-image'


def criu_run(path, tree):
    cur_dir = os.getcwd()
    os.chdir(os.path.dirname(path))

    nb = nbformat.read(path, as_version=4)

    pid = os.fork()

    if pid == 0:
        kernel = interactiveshell.InteractiveShell()

        for i, cell in enumerate(nb.cells):
            if cell.cell_type != 'code': continue
            cell.source = cell.source.replace('%matplotlib inline', '')
            res = kernel.run_cell(cell.source, silent=True)
            os.kill(os.getpid(), signal.SIGSTOP)

        sys.exit(0)

    else:
        for i, cell in enumerate(nb.cells):
            _, tree = tree.traverse(cell.source)

            prev = time.time()
            os.waitpid(pid, os.WSTOPPED)
            tree.time = time.time() - prev

            os.mkdir(CRIU_IMAGE_PATH)
            os.system(f'sudo criu dump -t {pid} --images-dir {CRIU_IMAGE_PATH} --shell-job --leave-running')
            size = 0
            for (path, dirs, files) in os.walk(CRIU_IMAGE_PATH):
                for file in files:
                    size += os.path.getsize(os.path.join(path, file))
            tree.size = size
            os.system(f'sudo rm -rf {CRIU_IMAGE_PATH}')
            os.kill(pid, signal.SIGCONT)

    os.waitpid(pid, 0)
    os.chdir(cur_dir)


def main(argv):
    if len(argv) != 3:
        print(f'Usage: {argv[0]} <Notebooks Path> <Output Tree>')
        sys.exit(1)

    abs_path = os.path.abspath(os.path.expanduser(argv[1]))

    tree = sciunit_tree.Tree()
    tree.time = tree.size = 0

    with iter_paths(abs_path) as paths:
        for path in paths:
            criu_run(path, tree)

            sciunit_tree.tree_dump(tree, 0, argv[2])


if __name__ == '__main__':
    main(sys.argv)
