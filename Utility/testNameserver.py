'''
Script for checkking what is currently registered in Pyro4 nameserver.
Also removes any apps named MMPMie, Raytracer or ComsolDummy
'''
import Pyro4

nshost = 'mech.FSV.CVUT.CZ'
nsport = 9090
hkey = 'mmp-secret-key'

ns = Pyro4.locateNS(host=nshost, port=nsport, hmac_key=hkey)

for app in ns.list():
    print(20 * '-')
    print(app)
    print(ns.lookup(app))
    if(app.find('Raytracer') != -1
       or app.find('MMPMie') != -1
       or app.find('ComsolDummy') != -1):
        ns.remove(app)
        print('removed')
