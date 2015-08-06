import tracerServerConfig as tConf
import os
from mupif import *
import logging
logger = logging.getLogger()

# required firewall settings (on ubuntu):
# for computer running daemon (this script)
# sudo iptables -A INPUT -p tcp -d 0/0 -s 0/0 --dport 44361 -j ACCEPT
# for computer running a nameserver
# sudo iptables -A INPUT -p tcp -d 0/0 -s 0/0 --dport 9090 -j ACCEPT


#locate nameserver
ns = PyroUtil.connectNameServer(nshost=tConf.nshost, nsport=tConf.nsport, hkey=tConf.hkey)

#Run a daemon for jobMamager on this machine
daemon = PyroUtil.runDaemon(host=tConf.daemonHost, port=tConf.jobManPort, nathost=tConf.nathost, natport=tConf.jobManNatport)
#Run job manager on a server
jobMan = JobManager.SimpleJobManager2(daemon, ns, tConf.applicationClass, tConf.jobManName, tConf.jobManPortsForJobs, tConf.jobManWorkDir, os.getcwd(), 'tracerServerConfig', tConf.jobMan2CmdPath, tConf.jobManMaxJobs, tConf.jobManSocket)

#set up daemon with JobManager
uri = daemon.register(jobMan)
#register JobManager to nameServer
ns.register(tConf.jobManName, uri)
logger.debug ("Daemon for JobManager runs at " + str(uri))
print 80*'-'
print ("Started "+tConf.jobManName)
#waits for requests
daemon.requestLoop()
