import clientConfig as cConf
import Pyro4
from mmp_tracer_api import objID
from comsol_api import MMPComsolDummy
from mupif import PyroUtil, Property, PropertyID, FieldID, ValueType
import logging
logger = logging.getLogger()
'''
### FID and PID definitions untill implemented at mupif###
PropertyID.PID_RefractiveIndex = 22
PropertyID.PID_NumberOfRays = 23
PropertyID.PID_LEDSpectrum = 24
PropertyID.PID_ParticleNumberDensity = 25
PropertyID.PID_ParticleRefractiveIndex = 26
PropertyID.PID_EmissionSpectrum = 2121
PropertyID.PID_ExcitationSpectrum = 2222
PropertyID.PID_AsorptionSpectrum = 2323

PropertyID.PID_ScatteringCrossSections = 28
PropertyID.PID_InverseCumulativeDist = 29

FieldID.FID_HeatSourceVol = 33
##########################################################
'''
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

comsolAppRec = PyroUtil.allocateApplicationWithJobManager(ns, cConf.comsolSolverJobManRec, cConf.jobNatPorts.pop(0), cConf.sshClient, cConf.options, cConf.sshHost)


mieApp = mieSolverAppRec.getApplication()
tracerApp = tracerSolverAppRec.getApplication()
#comsolApp = MMPComsolDummy('localhost')
comsolApp = comsolAppRec.getApplication()

logger.info('Applications loaded:')
print(mieApp)
print(tracerApp)
print(comsolApp)

#create a reverse tunnel so tracer can access comsol directly
appsTunnel = PyroUtil.connectApplications(cConf.tracerSolverJobManRec, comsolApp, sshClient=cConf.sshClient, options=cConf.options)

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
logger.info('Connecting Fields...in direct app-to-app manner')
fTempURI = comsolApp.getFieldURI(FieldID.FID_Temperature, 0)
fHeatURI = comsolApp.getFieldURI(FieldID.FID_HeatSourceVol, 0)
print(fTempURI, fHeatURI)
fTemp = cConf.Pyro4.Proxy(fTempURI)
fHeat = cConf.Pyro4.Proxy(fHeatURI)
print('fTemp=',fTemp)

##old way to connect fields:
#fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
#fHeat = comsolApp.getField(FieldID.FID_HeatSourceVol, 0)

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
if comsolAppRec:
    comsolAppRec.terminateAll()
if appsTunnel:
    appsTunnel.terminate()


