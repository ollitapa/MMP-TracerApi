import clientConfig as cConf
import Pyro4
from mmp_tracer_api import objID
from comsol_api import MMPComsolDummy
from mupif import PyroUtil, Property, PropertyID, FieldID, ValueType
import logging
logger = logging.getLogger()

PropertyID.PID_RefractiveIndex = "PID_RefractiveIndex"
PropertyID.PID_NumberOfRays = "PID_NumberOfRays"
PropertyID.PID_LEDSpectrum = "PID_LEDSpectrum"
PropertyID.PID_ParticleNumberDensity = "PID_ParticleNumberDensity"
PropertyID.PID_ParticleRefractiveIndex = "PID_ParticleRefractiveIndex"
PropertyID.PID_EmissionSpectrum = "PID_EmissionSpectrum"
PropertyID.PID_ExcitationSpectrum = "PID_ExcitationSpectrum"
PropertyID.PID_AsorptionSpectrum = "PID_AsorptionSpectrum"

PropertyID.PID_ScatteringCrossSections = "PID_ScatteringCrossSections"
PropertyID.PID_InverseCumulativeDist = "PID_InverseCumulativeDist"

FieldID.FID_HeatSourceVol = "FID_HeatSourceVol"
FieldID.FID_HeatSourceSurf = "FID_HeatSourceSurf"


import time as timeTime
start = timeTime.time()
logger.info('Timer started')

# locate nameserver
ns = PyroUtil.connectNameServer(nshost=cConf.nshost,
                                nsport=cConf.nsport,
                                hkey=cConf.hkey)
logger.info('NS connected: %s' % str(ns))


# Tunnels to different machines machine
mieTunnel = PyroUtil.sshTunnel(remoteHost=cConf.mieServer,
                               userName=cConf.mieUser,
                               localPort=cConf.mieNatPort,
                               remotePort=cConf.miePort,
                               sshClient=cConf.sshClient,
                               options=cConf.options,
                               sshHost=cConf.sshHost)
tracerTunnel = PyroUtil.sshTunnel(remoteHost=cConf.tracerServer,
                                  userName=cConf.tracerUser,
                                  localPort=cConf.tracerNatPort,
                                  remotePort=cConf.tracerPort,
                                  sshClient=cConf.sshClient,
                                  options=cConf.options,
                                  sshHost=cConf.sshHost)
'''
comsolTunnel = PyroUtil.sshTunnel(remoteHost=cConf.mieServer,
                                  userName=cConf.mieUser,
                                  localPort=cConf.mieNatPort,
                                  remotePort=cConf.miePort,
                                  sshClient=cConf.sshClient,
                                  options=cConf.options,
                                  sshHost=cConf.sshHost)
'''


mieApp = PyroUtil.connectApp(ns, cConf.mieID)
tracerApp = PyroUtil.connectApp(ns, cConf.tracerID)
#comsolApp = PyroUtil.connectApp(ns, cConf.comsolID)

logger.info('Applications loaded:')
print(mieApp)
print(tracerApp)
# print(comsolApp)

'''

# Connect functions
logger.info('Connecting Mie properties...')
pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                           objID.OBJ_PARTICLE_TYPE_1)

pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                            objID.OBJ_PARTICLE_TYPE_1)

logger.info('Props received...')
tracerApp.setProperty(pScat, objID.OBJ_PARTICLE_TYPE_1)
tracerApp.setProperty(pPhase, objID.OBJ_PARTICLE_TYPE_1)
logger.info('Props connected')


# Connect fields
#logger.info('Connecting Fields...in direct app-to-app manner')
#fTempURI = comsolApp.getFieldURI(FieldID.FID_Temperature, 0)
#fHeatURI = comsolApp.getFieldURI(FieldID.FID_HeatSourceVol, 0)
#print(fTempURI, fHeatURI)
#fTemp = cConf.Pyro4.Proxy(fTempURI)
#fHeat = cConf.Pyro4.Proxy(fHeatURI)

logger.info('Connecting Fields...')
# old way to connect fields:
fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
fHeat = comsolApp.getField(FieldID.FID_HeatSourceVol, 0)

tracerApp.setField(fTemp)
tracerApp.setField(fHeat)
logger.info('Fields connected')

# Connect properties
# Particle density
logger.info('Setting Properties...')
vDens = 0.00000003400
pDens = Property.Property(value=vDens,
                          propID=PropertyID.PID_ParticleNumberDensity,
                          valueType=ValueType.Scalar,
                          time=0.0,
                          units=None,
                          objectID=objID.OBJ_CONE)
tracerApp.setProperty(pDens)

# Number of rays to trace
pRays = Property.Property(value=100,
                          propID=PropertyID.PID_NumberOfRays,
                          valueType=ValueType.Scalar,
                          time=0.0,
                          units=None,
                          objectID=objID.OBJ_CONE)
tracerApp.setProperty(pRays)
logger.info('Properties set!')

# Solve
mieApp.solveStep(0)
logger.debug("mieApp.isSolved=", mieApp.isSolved())  # True

tracerApp.solveStep(0, runInBackground=False)
comsolApp.solveStep(0)

# Plot data to file
#logger.info("Saving vtk")
#v = fTemp.field2VTKData()
# v.tofile('testTemperature.vtk')
#v = fHeat.field2VTKData()
# v.tofile('testHeat.vtk')
'''

# Kill tunnels.
mieTunnel.kill()
tracerTunnel.kill()
# comsolTunnel.kill()