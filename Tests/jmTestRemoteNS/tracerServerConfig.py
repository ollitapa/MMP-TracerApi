import os
from mmp_tracer_api import mmpraytracer
import socket
import Pyro4
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}
Pyro4.config.HOST = 'mmpserver.erve.vtt.fi'

serverConfigPath = os.getcwd()

nshost = 'mech.FSV.CVUT.CZ'  # NameServer - do not change
nsport = 9090  # NameServer's port - do not change
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications
nathost = 'localhost'  # NatHost of local computer - do not change
serverNathost = 'localhost'  # NatHost of local computer - do not change

server = 'mmpserver.erve.vtt.fi'
daemonHost = 'mmpserver.erve.vtt.fi'  # socket.getfqdn()  # IP of server
hostUserName = 'otolli'  # User name for ssh connection

jobManPort = 44362  # Port for job manager's daemon
jobManNatport = 5556  # Natport - nat port used in ssh tunnel for job manager
jobManSocket = 10002  # Port used to communicate with application servers

jobManName = 'Mupif.JobManager@Raytracer'
applicationClass = mmpraytracer.MMPRaytracer

# Range of ports to be assigned on the server to jobs
jobManPortsForJobs = (9101, 9146)
jobManMaxJobs = 40  # Maximum number of jobs

# Main directory for transmitting files
jobManWorkDir = os.path.abspath(os.path.join(os.getcwd(), 'jobManWorkDir'))

# path to JobMan2cmd.py
jobMan2CmdPath = "jobMan2cmd"
