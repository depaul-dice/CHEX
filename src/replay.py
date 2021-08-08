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

# File purpose: Main script to re-run an execution using a replay sequence and checkpointing with CRIU.
# Usage: For Bob to use the replay sequence to run the execution.

import os
import sys
import subprocess
import socket
import pickle
import time
import signal
import shutil
import base64
import pickle as pkl

import psutil

from runner_util import *


def delete_checkpoint(hash_directory):
    directory = base64.b64encode(hash_directory).decode().replace('/', '_')
    shutil.rmtree(directory, ignore_errors=True)


def criu_dump(pid, hash_directory, waiter=None):
    delete_checkpoint(hash_directory)
    directory = base64.b64encode(hash_directory).decode().replace('/', '_')
    os.mkdir(directory)
    os.system(f'sudo criu dump -t {pid} --shell-job -D {directory}/')
    if waiter is not None:
        waiter.wait()
    while psutil.pid_exists(pid):
        time.sleep(1)
    time.sleep(2)


def criu_restore(pid, hash_directory):
    while psutil.pid_exists(pid):
        time.sleep(1)
    directory = base64.b64encode(hash_directory).decode().replace('/', '_')
    # os.system(f'sudo criu restore --shell-job -D {directory}/ &')
    runner = subprocess.Popen(['sudo', 'criu', 'restore', '--shell-job', '-D', f'{directory}/'], start_new_session=True)
    while not psutil.pid_exists(pid):
        time.sleep(1)
    signal.pause()
    signal.pause()
    return runner


def run_code(server, pid, code):
    while not psutil.pid_exists(pid):
        time.sleep(1)
    time.sleep(1)
    while True:
        try:
            os.kill(pid, signal.SIGUSR1)
            break
        except PermissionError:
            pass
    conn, _ = server.accept()
    send_msg(conn, pickle.dumps(code))
    result = pickle.loads(recv_msg(conn))
    conn.close()
    return result.out


def make_code_map(node, code_map):
    code_map[node.hash] = node.code
    for child in node.children:
        make_code_map(node.children[child], code_map)


def replay(replay_order_binary):
    with open(replay_order_binary, 'rb') as robf:
        sciunit_execution_tree, tree = pkl.load(robf)
    start = time.time()

    code_map = {}
    make_code_map(sciunit_execution_tree, code_map)

    try:
        os.unlink(SOCKET_FILE)
    except FileNotFoundError:
        pass
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_FILE)
    server.listen(1)

    signal.signal(signal.SIGUSR1, lambda *_: None)

    runner = subprocess.Popen([sys.executable, 'runner.py'], start_new_session=True)

    cconn, _ = server.accept()
    runner_pid = pickle.loads(recv_msg(cconn))
    send_msg(cconn, pickle.dumps(os.getpid()))
    cconn.close()
    print(runner_pid)

    criu_dump(runner_pid, tree.root, runner)
    runner = criu_restore(runner_pid, tree.root)
    print('First Restore Done')

    def rec_run(node, cache=tree.cache_size, create=None):
        nonlocal runner
        if create is None:
            create = [node]

        for child, to_cache in node.data.recursive_cache[cache]:
            if child is node:
                restore, *run = create
                criu_dump(runner_pid, b'criu', runner)
                runner = criu_restore(runner_pid, restore.identifier)
                for r in run:
                    print(run_code(server, runner_pid, code_map[r.identifier]))
            else:
                if to_cache:
                    criu_dump(runner_pid, node.identifier, runner)
                    runner = criu_restore(runner_pid, node.identifier)
                    rec_run(child, cache - node.data.c_size, [node, child])
                else:
                    rec_run(child, cache, create + [child])

    rec_run(tree.get_node(tree.root))
    os.system(f'sudo kill -KILL {runner_pid}')
    print(f'Total Time = {time.time() - start}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: replay.py replay-order.bin')
    replay(sys.argv[1])
