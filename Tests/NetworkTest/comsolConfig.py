import os
from mmp_tracer_api import mmpraytracer
import Pyro4
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}
Pyro4.config.HOST = 'mmpserver.erve.vtt.fi'

serverConfigPath = os.getcwd()
server = 'mmpserver.erve.vtt.fi'
serverPort = 9101
serverNathost = 'localhost'
serverNatport = 5556
nshost = 'mech.FSV.CVUT.CZ'  # NameServer - do not change
nsport = 9090  # NameServer's port - do not change
appName = "MMPRaytracer@mmpserver"
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications

hostUserName = 'elemim'  # User name for ssh connection
