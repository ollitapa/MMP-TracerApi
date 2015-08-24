import os
import mupif
#import demoapp
from mmp_tracer_api import mmpraytracer

import Pyro4
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}
hkey = 'mmp-secret-key'

serverConfigPath = os.getcwd()

nshost = '147.32.130.137'  # NameServer - do not change
nsport = 9090  # NameServer's port - do not change
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications
nathost = '127.0.0.1'  # NatHost of local computer - do not change

daemonHost = 'localhost'  # '147.32.130.137'#IP of server
hostUserName = 'mmp'  # User name for ssh connection

jobManPort = 44362  # Port for job manager's daemon
jobManNatport = 5557  # Natport - nat port used in ssh tunnel for job manager
jobManSocket = 10002  # Port used to communicate with application servers

jobManName = 'Mupif.JobManager@Raytracer'
applicationClass = mmpraytracer.MMPRaytracer

# Range of ports to be assigned on the server to jobs
jobManPortsForJobs = (9101, 9106)
jobManMaxJobs = 4  # Maximum number of jobs

# Main directory for transmitting files
jobManWorkDir = os.path.abspath(os.path.join(os.getcwd(), 'jobManWorkDir'))

# path to JobMan2cmd.py
jobMan2CmdPath = os.path.join(os.path.dirname(mupif.__file__),
                              'tools', 'JobMan2cmd.py')
