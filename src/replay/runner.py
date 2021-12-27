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

# File purpose: Helper script that gets run in a separate process to get checkpointed/restored by CRIU/

import os
import socket
import pickle
import signal
import time

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
    parent_pid = pickle.loads(recv_msg(client))
    client.close()

    while True:
        time.sleep(1)
        os.kill(parent_pid, signal.SIGUSR1)


if __name__ == '__main__':
    setup_signal()
