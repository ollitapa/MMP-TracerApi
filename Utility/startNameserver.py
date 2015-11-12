'''
Starts local nameserver.
run with python startNameserver.py
'''
import Pyro4

Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle', 'serpent', 'json']
Pyro4.config.SERIALIZER = 'pickle'
Pyro4.naming.startNSloop()
