import os
import sys
import subprocess
import socket
import pickle
import time
import shutil
import base64

import psutil

import sciunit_tree
import ExecutionTree as exT
from algorithms import recurse_algorithm
from runner_util import *


def delete_checkpoint(hash_directory):
    directory = base64.b64encode(hash_directory).decode()
    shutil.rmtree(directory, ignore_errors=True)


def criu_dump(pid, hash_directory, waiter=None):
    delete_checkpoint(hash_directory)
    directory = base64.b64encode(hash_directory).decode()
    os.mkdir(directory)
    os.system(f'sudo criu dump -t {pid} -D {directory}/')
    if waiter is not None:
        waiter.wait()
    while psutil.pid_exists(pid):
        time.sleep(1)
    time.sleep(2)


def criu_restore(pid, hash_directory):
    directory = base64.b64encode(hash_directory).decode()
    os.system(f'sudo criu restore -D {directory}/ &')
    while not psutil.pid_exists(pid):
        time.sleep(1)
    time.sleep(2)


def run_code(server, pid, code):
    while not psutil.pid_exists(pid):
        time.sleep(1)
    time.sleep(1)
    os.system(f'sudo kill -USR1 {pid}')
    conn, _ = server.accept()
    send_msg(conn, pickle.dumps(code))
    result = pickle.loads(recv_msg(conn))
    conn.close()
    return result.out


def make_code_map(node, code_map):
    code_map[node.hash] = node.code
    for child in node.children:
        make_code_map(node.children[child], code_map)


def run_tree(tree_binary, cache_size):
    sciunit_execution_tree, _ = sciunit_tree.tree_load(tree_binary)
    tree = exT.create_tree('SCIUNIT', tree_binary)
    code_map = {}
    make_code_map(sciunit_execution_tree, code_map)

    try:
        os.unlink(SOCKET_FILE)
    except FileNotFoundError:
        pass
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_FILE)
    server.listen(1)

    runner = subprocess.Popen([sys.executable, 'runner.py'], start_new_session=True,
                              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    cconn, _ = server.accept()
    runner_pid = pickle.loads(recv_msg(cconn))
    cconn.close()
    print(runner_pid)

    criu_dump(runner_pid, tree.root, runner)
    criu_restore(runner_pid, tree.root)

    def rec_run(node, cache=cache_size, create=None):
        if create is None:
            create = [node]

        for child, to_cache in node.data.recursive_cache[cache]:
            if child is node:
                restore, *run = create
                os.system(f'sudo kill -KILL {runner_pid}')
                while psutil.pid_exists(runner_pid):
                    time.sleep(1)
                criu_restore(runner_pid, restore.identifier)
                for r in run:
                    print(run_code(server, runner_pid, code_map[r.identifier]))
            else:
                if to_cache:
                    criu_dump(runner_pid, node.identifier)
                    criu_restore(runner_pid, node.identifier)
                    rec_run(child, cache - node.data.c_size, [node, child])
                else:
                    rec_run(child, cache, create + [child])

    tree.cache_size = cache_size
    recurse_algorithm(tree)
    rec_run(tree.get_node(tree.root))
    os.system(f'sudo kill -KILL {runner_pid}')


if __name__ == '__main__':
    run_tree('../data/kaggle.bin', 4 * 1024**3)
