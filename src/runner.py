import os
import socket
import pickle
import signal

import sciunit_tree
from runner_util import *

kernel = sciunit_tree.CodeKernel()


def handle_usr1(*_):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_FILE)
    code = pickle.loads(recv_msg(client))

    result = kernel.run_cell(code)
    send_msg(client, pickle.dumps(result))
    client.close()


def setup_signal():
    signal.signal(signal.SIGUSR1, handle_usr1)

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_FILE)
    send_msg(client, pickle.dumps(os.getpid()))
    client.close()

    while True:
        signal.pause()


if __name__ == '__main__':
    setup_signal()
