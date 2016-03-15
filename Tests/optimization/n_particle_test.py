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


#Green phosphor:
Mu = 2.4849
Sigma = 0.3878
#Red phosphor:
Mu2 =2.35137
Sigma2 = 0.627218

p_max = 35.0
p_min = 1.0
p_num = 50
w_max = 1100.0
w_min = 100.0
w_num = 1001


mup = Property.Property(value=Mu, propID=PropertyID.PID_ParticleMu, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

sigmap = Property.Property(value=Sigma, propID=PropertyID.PID_ParticleSigma, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

"""
maxp = Property.Property(value=p_max, propID=PropertyID.PID_Particle_max, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

minp = Property.Property(value=p_min, propID=PropertyID.PID_Particle_min, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

nump = Property.Property(value=p_num, propID=PropertyID.PID_Particle_n, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

maxw = Property.Property(value=w_max, propID=PropertyID.PID_Wavelen_max, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

minw = Property.Property(value=w_min, propID=PropertyID.PID_Wavelen_min, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

numw = Property.Property(value=w_num, propID=PropertyID.PID_Wavelen_n, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)
"""

mup2 = Property.Property(value=Mu2, propID=PropertyID.PID_ParticleMu, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

sigmap2 = Property.Property(value=Sigma2, propID=PropertyID.PID_ParticleSigma, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

"""
maxp2 = Property.Property(value=p_max2, propID=PropertyID.PID_Particle_max, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

minp2 = Property.Property(value=p_min2, propID=PropertyID.PID_Particle_min, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

nump2 = Property.Property(value=p_num2, propID=PropertyID.PID_Particle_n, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

maxw2 = Property.Property(value=w_max2, propID=PropertyID.PID_Wavelen_max, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

minw2 = Property.Property(value=w_min2, propID=PropertyID.PID_Wavelen_min, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

numw2 = Property.Property(value=w_num2, propID=PropertyID.PID_Wavelen_n, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)
"""

mieApp.setProperty(mup)
mieApp.setProperty(sigmap)
#mieApp.setProperty(maxp)
#mieApp.setProperty(minp)
#mieApp.setProperty(nump)
#mieApp.setProperty(maxw)
#mieApp.setProperty(minw)
#mieApp.setProperty(numw)

mieApp.setProperty(mup2)
mieApp.setProperty(sigmap2)
#mieApp.setProperty(maxp2)
#mieApp.setProperty(minp2)
#mieApp.setProperty(nump2)
#mieApp.setProperty(maxw2)
#mieApp.setProperty(minw2)
#mieApp.setProperty(numw2)



#run the simulation:
    
# Number of rays to trace
pRays = Property.Property(value=100000,
                              propID=PropertyID.PID_NumberOfRays,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
tracerApp.setProperty(pRays)
    
    
n_particles = Property.Property(value=2, propID=PropertyID.PID_NumberOfFluorescentParticles,
                                    valueType=ValueType.Scalar,
                                    time=0.0,
                                    units=None,
                                    objectID=objID.OBJ_CONE)
tracerApp.setProperty(n_particles)

#Phosphor efficiencies:
p_eff1 = Property.Property(value=0.8, propID=PropertyID.PID_PhosphorEfficiency, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)
tracerApp.setProperty(p_eff1)

p_eff2 = Property.Property(value=0.7, propID=PropertyID.PID_PhosphorEfficiency, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)
tracerApp.setProperty(p_eff2)



# em, ex, abs spectrum for each particle_type 1, 2, ...n

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
em2 = Property.Property(value=ex_em_import.getEmRed(),
                           propID=PropertyID.PID_EmissionSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_2)
tracerApp.setProperty(em2)

# Excitation spectrum
ex2 = Property.Property(value=ex_em_import.getExRed(),
                           propID=PropertyID.PID_ExcitationSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_2)
tracerApp.setProperty(ex2)

# Absorption spectrum
aabs2 = Property.Property(value=ex_em_import.getAbsRed(),
                             propID=PropertyID.PID_AsorptionSpectrum,
                             valueType=ValueType.Scalar,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_PARTICLE_TYPE_2)
tracerApp.setProperty(aabs2)

#logger.info('Properties set!')

# Solve Mie
mieApp.solveStep(0)


# propertyiksi, mielle   
# Particle density
dens_p = 5.0  # g/cm3
# Silicone density
dens_host = 1.1  # g/cm3


# Particles diameters in micrometers 
d = np.linspace(p_min, p_max, p_num)
#pdf = lognorm(sigma, scale=np.exp(mu))

# Weight fractions
#weight_frac = np.array([20, 25, 28]) / 100.0
weight_frac = np.array([20, 25]) / 100.0
#weight_frac = np.array([20]) / 100.0


particles_in_um3 = []
mu = [Mu, Mu2]
sigma = [Sigma, Sigma2]
j=0
for w_frac in weight_frac:
    particles_in_um3.extend([st.particlesInVolumeLogNormWeightTotal(w_frac, dens_p, dens_host, mu[j], sigma[j], particle_diameters=d)])
    j = j+1


# Particle density
#NOTE: USE ValueType.Vector if more than one particle type !!!
#Otherwise, use ValueType.Scalar !
vDens = particles_in_um3
pDens = Property.Property(value=vDens,
                          propID=PropertyID.PID_ParticleNumberDensity,
                              valueType=ValueType.Vector,
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


