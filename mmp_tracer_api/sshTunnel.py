#
# Copyright 2016 VTT Technical Research Center of Finland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import subprocess
import threading
import os


class SshTunnel(threading.Thread):
    '''
    Class to create an ssh tunnel to remote host and forward given ports.
    '''

    def __init__(self, localport, remoteport, remoteuser, remotehost,
                 reverse=False):
        threading.Thread.__init__(self)
        self.localport = localport      # Local port to listen to
        self.remoteport = remoteport    # Remote port on remotehost
        self.remoteuser = remoteuser    # Remote user on remotehost
        self.remotehost = remotehost    # What host do we send traffic to
        self.direction = 'L'
        if reverse:
            self.direction = 'R'

        self.daemon = True              # So that thread will exit when
        # main non-daemon thread finishes

    def run(self):
        client = 'ssh'
        if os.name == 'nt':
            client = 'putty'

        cmd = '%s -N -%s %d:localhost:%d %s@%s' % (client,
                                                   self.direction,
                                                   self.localport,
                                                   self.remoteport,
                                                   self.remoteuser,
                                                   self.remotehost)
        self.p = subprocess.Popen(cmd.split(),
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        # print(self.p.stdout.readlines())
        print('Tunnel open to %s.' % self.remotehost)

    def terminate(self):
        self.p.terminate()
        print('Tunnel to %s closed.' % self.remotehost)
