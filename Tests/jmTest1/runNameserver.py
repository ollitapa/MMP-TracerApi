import Pyro4

Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}
hkey = 'mmp-secret-key'

# Start nameserver
Pyro4.naming.startNSloop(host='localhost',
                         port=9090,
                         enableBroadcast=True,
                         bchost=None,
                         bcport=None,
                         unixsocket=None,
                         nathost=None,
                         natport=None,
                         storage=None,
                         hmac=hkey)
