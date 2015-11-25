import os
import socket
import sys

nsport = 9090
nshost = 'mech.FSV.CVUT.CZ'
nathost = 'localhost'  # NatHost of local computer - do not change
serverNathost = 'localhost'  # NatHost of local computer - do not change
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications

if(sys.platform.lower().startswith('win')):  # Windows ssh client
    sshClient = 'C:\\Program Files\\Putty\\putty.exe'
    options = '-i C:\\msys64\\home\\otolli\\.ssh\\putty_private.ppk'
    sshHost = ''
else:  # Unix ssh client
    sshClient = 'ssh'
    options = '-oStrictHostKeyChecking=no'
    sshHost = ''

# App info
tracerServer = 'mmpserver.erve.vtt.fi'
tracerPort = 9101
tracerID = 'MMPRaytracer@mmpserver'
tracerUser = 'otolli'  # ssh username
tracerNatPort = 5556

mieServer = 'mmpserver.erve.vtt.fi'
miePort = 9102
mieID = 'MMPMie@mmpserver'
mieUser = 'otolli'  # ssh username
mieNatPort = 5555

comsolServer = 'some.server.com'
comsolPort = 9103
comsolID = 'MMPComsol@some.server'
comsolUser = 'otolli'  # ssh username
comsolNatPort = 5557
