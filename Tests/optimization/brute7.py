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



print("simple brute force optimization")

#parameters that remain constant:
params = ()

#value that we target in the simulation:
x = (4000,) #CCT: 2700...5000


#function that runs the simulation and returns the simulated result value xsim:
def xsim(z, *params):

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

    hmri = Property.Property(1.55, PropertyID.PID_RefractiveIndex,
                             valueType=ValueType.Scalar,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_CONE)
    mieApp.setProperty(hmri)

    

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

    mieApp.setProperty(pScat2)
    mieApp.setProperty(pPhase2)

    # Connect functions
    pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                               objectID=objID.OBJ_PARTICLE_TYPE_1)
    pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                                objectID=objID.OBJ_PARTICLE_TYPE_1)
    
    pS2 = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                               objectID=objID.OBJ_PARTICLE_TYPE_2)

    pP2 = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                                objectID=objID.OBJ_PARTICLE_TYPE_2)

    tracerApp.setProperty(pScat)
    tracerApp.setProperty(pPhase)
    tracerApp.setProperty(pS2)
    tracerApp.setProperty(pP2)

    
    # Connect fields
    fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
    fHeat = comsolApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

    tracerApp.setField(fTemp)
    tracerApp.setField(fHeat)


    #set the constant properties from *params:

    p_max = 35.0
    p_min = 1.0
    p_num = 50

    w_max = 1100.0
    w_min = 100.0
    w_num = 1001

    # Weight fractions
    #weight_frac = np.array([24]) / 100.0 #CHANGING PARAMETER!See below

    # Particle density
    dens_p = 5.0  # g/cm3
    # Silicone density
    dens_host = 1.1  # g/cm3

    # log mean in microns
    mu1 = 2.4849
    # log standard deviation in microns
    sigma1 = 0.3878

    mu2 = 2.35137
    sigma2 = 0.627218

    mu = [mu1, mu2]
    sigma = [sigma1, sigma2]

    mup = Property.Property(value=mu1, propID=PropertyID.PID_ParticleMu, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

    sigmap = Property.Property(value=sigma1, propID=PropertyID.PID_ParticleSigma, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

    mup2 = Property.Property(value=mu2, propID=PropertyID.PID_ParticleMu, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

    sigmap2 = Property.Property(value=sigma2, propID=PropertyID.PID_ParticleSigma, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_2)

    mieApp.setProperty(mup)
    mieApp.setProperty(sigmap)
    mieApp.setProperty(mup2)
    mieApp.setProperty(sigmap2)

    # Particles diameters in micrometers
    d = np.linspace(p_min, p_max, p_num)
    #pdf = lognorm(sigma, scale=np.exp(mu))

    #set the changing properties from z:
    # Weight fractions
    #weight_frac = np.array([z]) / 100.0
    weight_frac = z / 100.0
    print("z, weight_frac = ", z, weight_frac)

    #run the simulation:
    
    # Number of rays to trace
    pRays = Property.Property(value=100000,
                              propID=PropertyID.PID_NumberOfRays,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
    tracerApp.setProperty(pRays)
    
   
    n_particles = Property.Property(value=2,
propID=PropertyID.PID_NumberOfFluorescentParticles,
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

    # Excitation spectrum 2
    ex2 = Property.Property(value=ex_em_import.getExRed(),
                           propID=PropertyID.PID_ExcitationSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_2)
    tracerApp.setProperty(ex2)

    # Absorption spectrum 2
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

    """
    # Connect functions
    pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                               objectID=objID.OBJ_PARTICLE_TYPE_1)
    pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                                objectID=objID.OBJ_PARTICLE_TYPE_1)
    
    pS2 = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0.0,
                               objectID=objID.OBJ_PARTICLE_TYPE_2)

    pP2 = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0.0,
                                objectID=objID.OBJ_PARTICLE_TYPE_2)

    tracerApp.setProperty(pScat)
    tracerApp.setProperty(pPhase)
    tracerApp.setProperty(pS2)
    tracerApp.setProperty(pP2)
    """

    particles_in_um3 = []
    j=0
    for w_frac in weight_frac:
        particles_in_um3.extend([st.particlesInVolumeLogNormWeightTotal(w_frac, dens_p, dens_host, mu[j], sigma[j], particle_diameters=d)])
        j = j+1


    # Particle density
    # Note: use ValueType.Vector if value already in []'s
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
    print('CCT: %f' % p.getValue())
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

    #return CCT:
    p = tracerApp.getProperty(PropertyID.PID_LEDCCT, 0,
                              objectID=objID.OBJ_LED)
    return (p.getValue())



#function to be minimized:
def f(z, *params):
    print('z: ', z)
    return (abs(x[0] - xsim(z, *params)))

"""
#ranges for each changing parameter:
#range for z=weight_fraction, 0...100
start = 15
stop = 26
step = 10
xs = [] #PARTICLE_TYPE_1 weight_fraction
ys = [] #PARTICLE_TYPE_2 weight_fraction

for z in range(start, stop, step):
    xs.append(z)
    ys.append(z)

print("xs:", xs)
print("ys:", ys)
"""

#ranges for each changing parameter:
rranges = (slice(15, 35, 10), slice(10, 29, 10)) #range for z=weight_fraction, 0...100

#optimization:
from scipy import optimize
resbrute = optimize.brute(f, rranges, args=params, full_output=True,
                          finish=None) #only brute force
                          #finish=optimize.fmin) #fmin after brute force

#optimization results:
print("global minimum at point:")
print(resbrute[0])  # global minimum
print("global minimum value:")
print(resbrute[1])  # function value at global minimum
print("evaluation grid points:")
print(resbrute[2])  # evaluation grid
print("values in evaluation grid points:")
print(resbrute[3])  # values in evaluation grid points


"""
#optimization:
from scipy import optimize

#interpolation:
from scipy import interpolate
g = interpolate.interp1d(xs, ys, kind='linear', bounds_error=False,
fill_value=[10000] )
# fill_value="extrapolate")
#kind = 'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
#bounds_error=False --> extrapolation if out of range values
#fill_value='extrapolate' only for kind={linear, nearest}, scipy version 0.17.0
#fill_value=(0, 0) means that 0 (the first) is used for extrapolated values on the left of the range, and 0 (the latter) for right side of range; scipy version 0.17.0
#fill_value=[10000]; some big number that will not be a minimum..

#solve the root:
middle = (stop + start)/2 
print("middle = ", middle)

root, infodict, ier, mesg = optimize.fsolve(g, middle, full_output=True)
print("root = ", root)
print("root value = ", g(root))
print("ier=", ier)

def absg(z):
    return abs(g(z))

if ier is not 1:
    print("could not find the root: ", mesg)
    print("finding min value in other ways")


    #if root not found, use basinhopping (finds the global min):
    oresult = optimize.basinhopping(absg, middle)
    print("min point and value: ", oresult.x, oresult.fun)

"""


