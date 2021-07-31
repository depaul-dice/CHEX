import os
import sys
import subprocess
import socket
import pickle
import time
import signal
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
    os.system(f'sudo criu dump -t {pid} --shell-job -D {directory}/')
    if waiter is not None:
        waiter.wait()
    while psutil.pid_exists(pid):
        time.sleep(1)
    time.sleep(2)


def criu_restore(pid, hash_directory):
    while psutil.pid_exists(pid):
        time.sleep(1)
    directory = base64.b64encode(hash_directory).decode()
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


def run_tree(tree_binary, cache_size):
    start = time.time()
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

    def rec_run(node, cache=cache_size, create=None):
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

    tree.cache_size = cache_size
    recurse_algorithm(tree)
    rec_run(tree.get_node(tree.root))
    os.system(f'sudo kill -KILL {runner_pid}')
    print(f'Total Time = {time.time() - start}')


if __name__ == '__main__':
    run_tree('../data/kaggle.bin', 4 * 1024**3)
