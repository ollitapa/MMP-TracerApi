import sys
sys.path.append('../../..')

import Pyro4
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}
hkey = 'mmp-secret-key'

nshost = 'localhost'  # NameServer - do not change
nsport = 9090  # NameServer's port - do not change
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications
nathost = 'localhost'  # NatHost of local computer - do not change

# daemonHost='147.32.130.137'#IP of server
hostUserName = 'otolli'  # 'mmp'#User name for ssh connection

# Edit these paths for your SSH-client and location of a private key
if(sys.platform.lower().startswith('win')):  # Windows ssh client
    sshClient = 'C:\\Program Files\\Putty\\putty.exe'
    options = '-i C:\\msys64\\home\\otolli\\.ssh\\putty_private.ppk'
    sshHost = ''
else:  # Unix ssh client
    sshClient = 'ssh'
    options = '-oStrictHostKeyChecking=no'
    sshHost = ''

# jobManager records to be used in scenario
# format: (jobManPort, jobManNatport, jobManHostname, jobManUserName,
# jobManDNSName)
# thermalSolverJobManRec = (44360, 5555, '127.0.1.1',#'147.32.130.137',
# hostUserName, 'Mupif.JobManager@ThermalSolverDemo')
# mechanicalSolverJobManRec = (44361, 5556, '127.0.1.1',
#'147.32.130.137',
# hostUserName, 'Mupif.JobManager@MechanicalSolverDemo')

mieSolverJobManRec = (44360, 5555, 'localhost',  # '147.32.130.137',
                      hostUserName, 'Mupif.JobManager@MMPMie')

tracerSolverJobManRec = (44362, 5557, 'localhost',  # '147.32.130.137',
                         hostUserName, 'Mupif.JobManager@Raytracer')

# client ports used to establish ssh connections (nat ports)
jobNatPorts = range(6000, 6019)
