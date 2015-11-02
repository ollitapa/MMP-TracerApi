import sys
import Pyro4
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}
Pyro4.config.HOST = 'localhost'


nshost = 'mech.FSV.CVUT.CZ'   # NameServer - do not change
nsport = 9090  # NameServer's port - do not change
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications
nathost = 'localhost'  # NatHost of local computer - do not change
serverNathost = 'localhost'  # NatHost of local computer - do not change

server = 'mmpserver.erve.vtt.fi'
daemonHost = 'mmpserver.erve.vtt.fi'  # IP of server
hostUserName = 'elemim'  # 'mmp'#User name for ssh connection

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

mieSolverJobManRec = (44360, 5557, 'mmpserver.erve.vtt.fi',
                      hostUserName, 'Mupif.JobManager@MMPMie')

tracerSolverJobManRec = (44362, 5556, 'mmpserver.erve.vtt.fi',
                         hostUserName, 'Mupif.JobManager@Raytracer')


comsolSolverJobManRec = (44363, 5558, 'mmpserver.erve.vtt.fi',
                         hostUserName, 'Mupif.JobManager@MMPComsolDummy')

# client ports used to establish ssh connections (nat ports)
jobNatPorts = range(4000, 4019)
