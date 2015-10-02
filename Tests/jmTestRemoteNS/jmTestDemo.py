import clientConfig as cConf
import Pyro4
from mmp_tracer_api import objID
from comsol_api import MMPComsolDummy
from mupif import PyroUtil, Property, PropertyID, FieldID, ValueType
import logging
logger = logging.getLogger()

### FID and PID definitions untill implemented at mupif###
PropertyID.PID_RefractiveIndex = 22
PropertyID.PID_NumberOfRays = 23
PropertyID.PID_LEDSpectrum = 24
PropertyID.PID_ParticleNumberDensity = 25
PropertyID.PID_ParticleRefractiveIndex = 26

PropertyID.PID_ScatteringCrossSections = 28
PropertyID.PID_InverseCumulativeDist = 29

FieldID.FID_HeatSourceVol = 33
##########################################################


import time as timeTime
start = timeTime.time()
logger.info('Timer started')

# locate nameserver
ns = PyroUtil.connectNameServer(
    nshost=cConf.nshost, nsport=cConf.nsport, hkey=cConf.hkey)

# localize JobManager running on (remote) server and create a tunnel to it
# allocate the first application app1

tracerSolverAppRec = PyroUtil.allocateApplicationWithJobManager(
    ns, cConf.tracerSolverJobManRec, cConf.jobNatPorts.pop(0),
    cConf.sshClient, cConf.options, cConf.sshHost)
mieSolverAppRec = PyroUtil.allocateApplicationWithJobManager(
    ns, cConf.mieSolverJobManRec, cConf.jobNatPorts.pop(0),
    cConf.sshClient, cConf.options, cConf.sshHost)


mieApp = mieSolverAppRec.getApplication()
tracerApp = tracerSolverAppRec.getApplication()
#comsolApp = MMPComsolDummy('localhost')

logger.info('Applications loaded:')
print(mieApp)
print(tracerApp)
# print(comsolApp)


# Connect functions

logger.info('Connecting Mie properties...')
pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                           objID.OBJ_PARTICLE_TYPE_1)
print(pScat)
print(pScat.getValue())


pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                            objID.OBJ_PARTICLE_TYPE_1)

logger.info('Props received...')
tracerApp.setProperty(Pyro4.Proxy(pScat._PyroURL), objID.OBJ_PARTICLE_TYPE_1)
#tracerApp.setProperty(pPhase, objID.OBJ_PARTICLE_TYPE_1)
logger.info('Props connected')

'''
# Connect fields
logger.info('Connecting Fields...')
fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
fHeat = comsolApp.getField(FieldID.FID_HeatSourceVol, 0)
print(fTemp)

tracerApp.setField(fTemp)
tracerApp.setField(fHeat)
logger.info('Fields connected')
'''
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
# comsolApp.solveStep(0)

# Plot data to file
logger.info("Saving vtk")
#v = fTemp.field2VTKData()
# v.tofile('testTemperature.vtk')
#v = fHeat.field2VTKData()
# v.tofile('testHeat.vtk')


logger.debug("terminating apps...")

if mieSolverAppRec:
    mieSolverAppRec.terminateAll()
if tracerSolverAppRec:
    tracerSolverAppRec.terminateAll()
