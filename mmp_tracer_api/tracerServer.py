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
from mupif import PyroUtil, JobManager as jb
from mmp_tracer_api import MMPRaytracer
import logging
logger = logging.getLogger()


# required firewall settings (on ubuntu):
# for computer running daemon (this script)
# sudo iptables -A INPUT -p tcp -d 0/0 -s 0/0 --dport 44361 -j ACCEPT
# for computer running a nameserver
# sudo iptables -A INPUT -p tcp -d 0/0 -s 0/0 --dport 9090 -j ACCEPT

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

if __name__ == '__main__':
    main()
