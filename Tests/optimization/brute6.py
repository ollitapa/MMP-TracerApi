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

    
    tracerApp.setProperty(pScat)
    tracerApp.setProperty(pPhase)
    
    # Connect fields
    fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
    fHeat = comsolApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

    tracerApp.setField(fTemp)
    tracerApp.setField(fHeat)


    #set the constant properties from *params:

    p_max = 35.0
    p_min = 3.0
    p_num = 50

    w_max = 1100.0
    w_min = 100.0
    w_num = 1000


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

    #set the changing properties from z:
    # Weight fractions
    weight_frac = np.array([z]) / 100.0
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
    

    
    n_particles = Property.Property(value=1,
                                    propID=PropertyID.PID_NumberOfFluorescentParticles,
                                    valueType=ValueType.Scalar,
                                    time=0.0,
                                    units=None,
                                    objectID=objID.OBJ_CONE)
    tracerApp.setProperty(n_particles)

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
    

    #logger.info('Properties set!')

    # Solve Mie
    mieApp.solveStep(0)

    #TODO: Need a new function to calculate particles_in_um3 if more than 1 particle type... see n_particle_test.py
    particles_in_um3 = 0.0
    for w_frac in weight_frac:
        particles_in_um3 =\
            st.particlesInVolumeLogNormWeightTotal(w_frac, dens_p,
                                                   dens_host, mu, sigma,
                                                   particle_diameters=d)

    # Particle density
    #NOTE: If more than 1 particle type, use ValueType.Vector !
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

    #return CCT:
    p = tracerApp.getProperty(PropertyID.PID_LEDCCT, 0,
                              objectID=objID.OBJ_LED)
    return (p.value)



#function to be interpolated:
def f(z, *params):
    return (x[0] - xsim(z, *params))


#ranges for each changing parameter:
#range for z=weight_fraction, 0...100
start = 20
stop = 31
step = 10
xs = []
ys = []

for z in range(start, stop, step):
    xs.append(z)
    ys.append(f(z))

print("xs:", xs)
print("ys:", ys)


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




