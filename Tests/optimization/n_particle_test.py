from mmp_mie_api import MMPMie
from mmp_tracer_api import MMPRaytracer, objID
from comsol_api import MMPComsolDummy

from mupif import PropertyID, FieldID, FunctionID, Property, ValueType
import logging
import logging.config
import ex_em_import
import numpy as np
from scipy.stats import lognorm
from pyraytracer import scatteringTools as st
import os



print("test script for n particle types")


#create the apps:
mieApp = MMPMie('localhost')
tracerApp = MMPRaytracer('localhost')
comsolApp = MMPComsolDummy('localhost')

# Point data conversion to false. Speeds up testing
tracerApp._convertPointData = False

# Set default LED json
tracerApp.setDefaultInputFile('./DefaultLED3.json')

#Set refractive indexes to mieApp:
pri = Property.Property(1.83,
                        PropertyID.PID_RefractiveIndex,
                        valueType=ValueType.Scalar,
                        time=0.0,
                        units=None,
                        objectID=objID.OBJ_PARTICLE_TYPE_1)
mieApp.setProperty(pri)

#same for particle_type_2
pri2 = Property.Property(1.84,
                        PropertyID.PID_RefractiveIndex,
                        valueType=ValueType.Scalar,
                        time=0.0,
                        units=None,
                        objectID=objID.OBJ_PARTICLE_TYPE_2)
mieApp.setProperty(pri2)

"""
pri3 = Property.Property(1.85,
                        PropertyID.PID_RefractiveIndex,
                        valueType=ValueType.Scalar,
                        time=0.0,
                        units=None,
                         objectID=objID.OBJ_PARTICLE_TYPE_3)
mieApp.setProperty(pri3)
"""
hmri = Property.Property(1.55, PropertyID.PID_RefractiveIndex,
                             valueType=ValueType.Scalar,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_CONE)
mieApp.setProperty(hmri)


# Connect functions
pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                               objectID=objID.OBJ_PARTICLE_TYPE_1)
pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                                objectID=objID.OBJ_PARTICLE_TYPE_1)


#set also another particle type to MieApp:

pScat2 = Property.Property(0,
                              PropertyID.PID_ScatteringCrossSections,
                              valueType=ValueType.Vector,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_PARTICLE_TYPE_2)

pPhase2 = Property.Property(0,
                          propID=PropertyID.PID_InverseCumulativeDist,
                            valueType=ValueType.Vector,
                            time=0.0,
                            units=None,
                            objectID=objID.OBJ_PARTICLE_TYPE_2)


"""
pScat3 = Property.Property(0,
                              PropertyID.PID_ScatteringCrossSections,
                              valueType=ValueType.Vector,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_PARTICLE_TYPE_3)

pPhase3 = Property.Property(0,
                            propID=PropertyID.PID_InverseCumulativeDist,
                            valueType=ValueType.Vector,
                            time=0.0,
                            units=None,
                            objectID=objID.OBJ_PARTICLE_TYPE_3)
"""

mieApp.setProperty(pScat2)
mieApp.setProperty(pPhase2)


#mieApp.setProperty(pScat3)
#mieApp.setProperty(pPhase3)



pS2 = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0.0,
                               objectID=objID.OBJ_PARTICLE_TYPE_2)

pP2 = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0.0,
                                objectID=objID.OBJ_PARTICLE_TYPE_2)


"""
pS3 = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0.0,
                               objectID=objID.OBJ_PARTICLE_TYPE_3)

pP3 = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0.0,
                                objectID=objID.OBJ_PARTICLE_TYPE_3)

"""


tracerApp.setProperty(pScat)
tracerApp.setProperty(pPhase)
tracerApp.setProperty(pS2)
tracerApp.setProperty(pP2)
#tracerApp.setProperty(pS3)
#tracerApp.setProperty(pP3)

# Connect fields
fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
fHeat = comsolApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

tracerApp.setField(fTemp)
tracerApp.setField(fHeat)

# naille voisi olla oma property... sama mmpraytracer ja mmpmie (ei toistaiseksi)
p_max = 35.0
p_min = 3.0
p_num = 50

w_max = 1100.0
w_min = 100.0
w_num = 1000

# propertyiksi, mielle   
# Particle density
dens_p = 5.0  # g/cm3
# Silicone density
dens_host = 1.1  # g/cm3

# log mean in microns
mu = 2.4849
# log standard deviation in microns
sigma = 0.3878
# Particles diameters in micrometers
d = np.linspace(p_min, p_max, p_num)
pdf = lognorm(sigma, scale=np.exp(mu))

# Weight fractions
#weight_frac = np.array([20, 25, 28]) / 100.0
weight_frac = np.array([20, 25]) / 100.0
#weight_frac = np.array([20]) / 100.0

#run the simulation:
    
# Number of rays to trace
pRays = Property.Property(value=100000,
                              propID=PropertyID.PID_NumberOfRays,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
tracerApp.setProperty(pRays)
    

#TODO: replace PID with a new PID!!!!!    
n_particles = Property.Property(value=2,
                                    propID=PropertyID.PID_Demo_Value,
                                    valueType=ValueType.Scalar,
                                    time=0.0,
                                    units=None,
                                    objectID=objID.OBJ_CONE)
tracerApp.setProperty(n_particles)

#TODO: Should we have these spectrums for each particle_type 1, 2, ...n ? YES

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
    

# Emission spectrum 2
em2 = Property.Property(value=ex_em_import.getEm(),
                           propID=PropertyID.PID_EmissionSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_2)
tracerApp.setProperty(em2)

# Excitation spectrum
ex2 = Property.Property(value=ex_em_import.getEx(),
                           propID=PropertyID.PID_ExcitationSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_2)
tracerApp.setProperty(ex2)

# Absorption spectrum
aabs2 = Property.Property(value=ex_em_import.getAbs(),
                             propID=PropertyID.PID_AsorptionSpectrum,
                             valueType=ValueType.Scalar,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_PARTICLE_TYPE_2)
tracerApp.setProperty(aabs2)

#logger.info('Properties set!')

# Solve Mie
mieApp.solveStep(0)


# TODO: particles_in_um3 += st.par.....? Tarvitaan uusi yhtalo...
particles_in_um3 = 0.0
for w_frac in weight_frac:
    particles_in_um3 +=\
            st.particlesInVolumeLogNormWeightTotal(w_frac, dens_p,
                                                   dens_host, mu, sigma,
                                                   particle_diameters=d)

# Particle density
vDens = particles_in_um3
pDens = Property.Property(value=vDens,
                          propID=PropertyID.PID_ParticleNumberDensity,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
tracerApp.setProperty(pDens)

# Solve
tracerApp.solveStep(0, runInBackground=False)



#get the simulation result value and return it:
    
p = tracerApp.getProperty(PropertyID.PID_LEDCCT, 0,
                              objectID=objID.OBJ_LED)
print('CCT: %f' % p.value)
p = tracerApp.getProperty(PropertyID.PID_LEDRadiantPower, 0,
                                  objectID=objID.OBJ_LED)
print('RadiantPower: %f' % p.value)

p = tracerApp.getProperty(PropertyID.PID_LEDColor_x, 0,
                                  objectID=objID.OBJ_LED)
print('Color x: %f' % p.value)
p = tracerApp.getProperty(PropertyID.PID_LEDColor_y, 0,
                                  objectID=objID.OBJ_LED)
print('Color y: %f' % p.value)
p = tracerApp.getProperty(PropertyID.PID_LEDSpectrum, 0,
                                  objectID=objID.OBJ_LED)
print(p.value['wavelengths'][0:10])
print(p.value['intensities'][0:10])


