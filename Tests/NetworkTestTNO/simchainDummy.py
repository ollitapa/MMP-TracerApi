
#
# Import all needed libraries, definitions, etc.
#
import Pyro4
Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle', 'serpent', 'json', 'marshal']
Pyro4.config.SERIALIZER = 'pickle'
# VTT Code
import objID
import logging
logger = logging.getLogger()
# VTT Code

import sys
# sys.path.append('./VTT')

import ex_em_import

from mupif import *

#sys.excepthook = Pyro4.util.excepthook

# Simulation chain
#
logger.info('Connecting with NameServer...')
ns = Pyro4.locateNS(port=9091)
logger.info('Connected')
logger.info('Connecting with appTNO')
appTNO = Pyro4.Proxy(ns.lookup('ComsolDummy@mmpserver'))
logger.info('Connecting with mieApp')
mieApp = Pyro4.Proxy(ns.lookup('MMPMie@mmpserver'))
logger.info('Connecting with tracerApp')
tracerApp = Pyro4.Proxy(ns.lookup('MMPRaytracer@mmpserver'))
logger.info('All applications connected')

tracerApp.setDefaultInputFile('DefaultLED.json')

# VTT can as for the fields (with respective meshes) as in:
logger.info('Retrieving initial data from appTNO')
fHeatVol = appTNO.getField(FieldID.FID_Thermal_absorption_volume, 0)
logger.info('Fields retrieved')

# VTTCode
# Connect fields
logger.info('Connecting Fields...')
tracerApp.setField(fHeatVol)
logger.info('Fields connected')


# Particle density
logger.info('Setting Properties...')
vDens = 0.00003400
pDens = Property.Property(value=vDens,
                          propID=PropertyID.PID_ParticleNumberDensity,
                          valueType=ValueType.Scalar,
                          time=0.0,
                          units=None,
                          objectID=objID.OBJ_CONE)
tracerApp.setProperty(pDens)

# Number of rays to trace
pRays = Property.Property(value=10000,
                          propID=PropertyID.PID_NumberOfRays,
                          valueType=ValueType.Scalar,
                          time=0.0,
                          units=None,
                          objectID=objID.OBJ_CONE)
tracerApp.setProperty(pRays)
# Emission spectrum
em = Property.Property(value=ex_em_import.getEm(),
                       propID=PropertyID.PID_EmissionSpectrum,
                       valueType=ValueType.Scalar,
                       time=0.0,
                       units=None,
                       objectID=objID.OBJ_PARTICLE_TYPE_1)
tracerApp.setProperty(em)

# Excitation spectrum
ex = Property.Property(value=ex_em_import.getEx(),
                       propID=PropertyID.PID_ExcitationSpectrum,
                       valueType=ValueType.Scalar,
                       time=0.0,
                       units=None,
                       objectID=objID.OBJ_PARTICLE_TYPE_1)
tracerApp.setProperty(ex)

# Absorption spectrum
aabs = Property.Property(value=ex_em_import.getAbs(),
                         propID=PropertyID.PID_AsorptionSpectrum,
                         valueType=ValueType.Scalar,
                         time=0.0,
                         units=None,
                         objectID=objID.OBJ_PARTICLE_TYPE_1)
tracerApp.setProperty(aabs)


# Solve
logger.info('Entering mieApp solver')
mieApp.solveStep(0)
logger.info('mieApp solved')

# Connect properties
logger.info('Connecting Mie properties...')
pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                           objID.OBJ_PARTICLE_TYPE_1)

pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                            objID.OBJ_PARTICLE_TYPE_1)

logger.info('Props received...')
tracerApp.setProperty(pScat, objID.OBJ_PARTICLE_TYPE_1)
tracerApp.setProperty(pPhase, objID.OBJ_PARTICLE_TYPE_1)
logger.info('Props connected')

# logger.debug("mieApp.isSolved=", mieApp.isSolved())  # True
logger.info('Entering tracerApp solver')
tracerApp.solveStep(0, runInBackground=False)
logger.info('tracerApp solved')

# Manually get Fields
fHvolnew = tracerApp.getField(FieldID.FID_Thermal_absorption_volume, 0)
fHvolnew.field2VTKData().tofile('fHeatVol02.vtk')

# Properties
p = tracerApp.getProperty(PropertyID.PID_LEDCCT, 0,
                          objectID=objID.OBJ_LED)
print('CCT: %d' % p.getValue())
p = tracerApp.getProperty(PropertyID.PID_LEDRadiantPower, 0,
                          objectID=objID.OBJ_LED)
print('RadiantPower: %f' % p.getValue())

p = tracerApp.getProperty(PropertyID.PID_LEDColor_x, 0,
                          objectID=objID.OBJ_LED)
print('Color x: %f' % p.getValue())
p = tracerApp.getProperty(PropertyID.PID_LEDColor_y, 0,
                          objectID=objID.OBJ_LED)
print('Color y: %f' % p.getValue())
p = tracerApp.getProperty(PropertyID.PID_LEDSpectrum, 0,
                          objectID=objID.OBJ_LED)
print(p.getValue()['wavelengths'][0:10])
print(p.getValue()['intensities'][0:10])
