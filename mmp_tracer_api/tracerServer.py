#
# Copyright 2015 VTT Technical Research Center of Finland
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
import importlib
import argparse
import sys
import os
import threading
import signal
import Pyro4
from time import sleep
from mupif import PyroUtil, JobManager as jb
from mmp_tracer_api import MMPRaytracer
import logging
from .sshTunnel import SshTunnel
logger = logging.getLogger()

parser = argparse.ArgumentParser(description='Start MMP-Tracer server. ')
parser.add_argument("configFile",
                    help='Configuration filename (py format)',
                    type=str, default='config.json')


def main():
    # Parse arguments
    args = parser.parse_args()
    sys.path.append(os.getcwd())

    # Load config
    conf = args.configFile
    if conf[-3:] == '.py':
        conf = conf[:-3]

    tConf = importlib.import_module(conf)

    # locate nameserver
    ns = PyroUtil.connectNameServer(nshost=tConf.nshost,
                                    nsport=tConf.nsport,
                                    hkey=tConf.hkey)

    # Run a daemon for jobMamager on this machine
    daemon = PyroUtil.runDaemon(host=tConf.daemonHost,
                                port=tConf.jobManPort,
                                nathost=tConf.nathost,
                                natport=tConf.jobManNatport)
    # Run job manager on a serverdaemon, ns, appAPIClass, appName, portRange,
    # jobManWorkDir, serverConfigPath, serverConfigFile, jobMan2CmdPath,
    # maxJobs=1, jobMancmdCommPort=10000
    jobMan = jb.SimpleJobManager2(daemon, ns,
                                  appAPIClass=tConf.applicationClass,
                                  appName=tConf.jobManName,
                                  portRange=tConf.jobManPortsForJobs,
                                  jobManWorkDir=tConf.jobManWorkDir,
                                  serverConfigPath=tConf.serverConfigPath,
                                  serverConfigFile=conf,
                                  jobMan2CmdPath=tConf.jobMan2CmdPath,
                                  maxJobs=tConf.jobManMaxJobs,
                                  jobMancmdCommPort=tConf.jobManSocket)

    # set up daemon with JobManager
    uri = daemon.register(jobMan)
    # register JobManager to nameServer
    ns.register(tConf.jobManName, uri)
    logger.debug("Daemon for JobManager runs at " + str(uri))
    print(80 * '-')
    print("Started " + tConf.jobManName)
    # waits for requests
    daemon.requestLoop()


def runSingleServerInstance():
    '''
    Run a single instance of the Tracer server.
    The configuration file given in args must include the following:
    server,
    serverPort,
    serverNathost,
    serverNatport,
    nshost,
    nsport,
    appName,
    hkey
    '''
    # Parse arguments
    args = parser.parse_args()
    sys.path.append(os.getcwd())

    # Load config
    conf = args.configFile
    if conf[-3:] == '.py':
        conf = conf[:-3]
    print(conf)

    cfg = importlib.import_module(conf)

    app = MMPRaytracer('localhost')

    PyroUtil.runAppServer(cfg.server,
                          cfg.serverPort,
                          cfg.serverNathost,
                          cfg.serverNatport,
                          cfg.nshost,
                          cfg.nsport,
                          cfg.appName,
                          cfg.hkey,
                          app=app)


def runSingleServerInstanceNoNat():
    # Parse arguments
    args = parser.parse_args()
    sys.path.append(os.getcwd())

    # Load config
    conf = args.configFile
    if conf[-3:] == '.py':
        conf = conf[:-3]
    print(conf)

    cfg = importlib.import_module(conf)

    app = MMPRaytracer('localhost')

    # Creates deamon, register the app in it
    daemon = Pyro4.Daemon(host=cfg.server,
                          port=cfg.serverPort)
    uri = daemon.register(app)

    # Get nameserver
    ns = Pyro4.locateNS(host=cfg.nshost, port=cfg.nsport, hmac_key=cfg.hkey)
    # Register app
    ns.register(cfg.appName, uri)

    print(uri)
    # Deamon loops at the end
    daemon.requestLoop()


def runSingleServerInstanceSSHtunnel():
    # Parse arguments
    args = parser.parse_args()
    sys.path.append(os.getcwd())

    # Load config
    conf = args.configFile
    if conf[-3:] == '.py':
        conf = conf[:-3]
    print(conf)

    cfg = importlib.import_module(conf)

    # Load the App
    app = MMPRaytracer('localhost')

    # Prepare ssh tunnels
    pyroTunnel = SshTunnel(localport=cfg.serverPort,
                           remoteport=cfg.serverPort,
                           remoteuser=cfg.hostUserName,
                           remotehost=cfg.server,
                           reverse=True)
    nsTunnel = SshTunnel(localport=cfg.nsport,
                         remoteport=cfg.nsport,
                         remoteuser=cfg.hostUserName,
                         remotehost=cfg.nshost,
                         reverse=False)

    try:

        # Open tunnels
        pyroTunnel.run()
        nsTunnel.run()
        sleep(1)

        # Creates deamon, register the app in it
        daemon = Pyro4.Daemon(host='localhost',
                              port=cfg.serverPort)
        uri = daemon.register(app)
        print(uri)

        # Get nameserver
        ns = Pyro4.locateNS(host='localhost',
                            port=cfg.nsport,
                            hmac_key=cfg.hkey)
        # Register app
        ns.register(cfg.appName, uri)
        print(uri)

        # Shutdown handler. Remember to close ssh tunnels
        def signal_handler(signal, frame):
            print('Shutting down!')
            pyroTunnel.terminate()
            nsTunnel.terminate()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Deamon loops at the end
        daemon.requestLoop()

    except:
        pyroTunnel.terminate()
        nsTunnel.terminate()
        print('terminated')
        raise


if __name__ == '__main__':
    main()
