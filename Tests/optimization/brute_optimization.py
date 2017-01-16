from mmp_mie_api import MMPMie
from mmp_tracer_api import MMPRaytracer, objID
from comsol_api import MMPComsolDummy

from mupif import *
import logging
import logging.config
import ex_em_import
import numpy as np
from scipy.stats import lognorm
#from pyraytracer import scatteringTools as st
import scatteringTools as st 
import os

from pycolortools import CIEXYZ, Illuminants
import pickle

print("simple brute force optimization")

#parameters that remain constant:
params = ()

#value that we target in the simulation:
x = (4000.0, ) #CCT: 2700...5000 K

#Color coordinates x and y corresponding to target CCT:
CCT = x[0]
cie = CIEXYZ()
il = Illuminants()

wave = np.linspace(200, 900, 1000)
# Select reference illuminant: Select good white
if CCT <= 4500:
    testIntens = il.blackbodySpectrum560(wave, CCT)
elif CCT < 5500.0:
    testIntens = il.illuminantD_M(wave, CCT)
else:
    testIntens = il.illuminantD(wave, CCT)


# Check CCT that CCT is correct
CCT = cie.calculateCCT(cie.ciexyzFromSpectrum(wave, testIntens))

print('targetCCT: %f' % CCT)

# Calculate color coordinates
global xyz
xyz = cie.ciexyzFromSpectrum(wave, testIntens)
print('x: %.5f y: %.5f' % (xyz[0], xyz[1]))



#function that runs the simulation and returns the simulated result value xsim:
def xsim(z, *params):

    #create the apps:
    mieApp = MMPMie('localhost')
    tracerApp = MMPRaytracer('localhost')
    comsolApp = MMPComsolDummy('localhost')

    # Point data conversion to false. Speeds up testing
    tracerApp._convertPointData = True #False

    # Set default LED json
    tracerApp.setDefaultInputFile('./DefaultLED.json') 

    #Set refractive indexes to mieApp:
    pri = Property.Property(1.83,
                            PropertyID.PID_RefractiveIndex,
                            valueType=ValueType.Scalar,
                            time=0.0,
                            units=None,
                            objectID=objID.OBJ_PARTICLE_TYPE_1)
    mieApp.setProperty(pri)

    # same for particle_type_2
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

    # Connect fields
    fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
    fHeat = comsolApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

    tracerApp.setField(fTemp)
    tracerApp.setField(fHeat)


    #set the constant properties from *params:

    p_max = 20.0
    p_min = 2.0
    p_num = 50

    w_max = 1100.0
    w_min = 100.0
    w_num = 1001


    # Particle density for PARTICLE_TYPE_1 and 2
    dens_p = [5.0, 4.04]  # g/cm3
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
    weight_frac = z / 100.0
    print("z, weight_frac = ", z, weight_frac)
    
    # Number of rays to trace
    pRays = Property.Property(value=1000,
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
    p_eff1 = Property.Property(value=0.4, propID=PropertyID.PID_PhosphorEfficiency, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)
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


    # Solve Mie
    mieApp.solveStep(0)

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
    

    particles_in_um3 = []
    volume_fractions = []
    
    if n_particles.value == 2:
        
        vol_frac, par_dens = st.particlesInVolumeLogNormWeightTotal2(weight_frac[0], weight_frac[1], dens_p[0], dens_p[1], dens_host, mu[0], sigma[0], particle_diameters=d)
        particles_in_um3.extend([par_dens])
        volume_fractions.extend([vol_frac])
        vol_frac, par_dens = st.particlesInVolumeLogNormWeightTotal2(weight_frac[1], weight_frac[0], dens_p[1], dens_p[0], dens_host, mu[1], sigma[1], particle_diameters=d)
        particles_in_um3.extend([par_dens])
        volume_fractions.extend([vol_frac])

        print('volume fractions for 2 particles:', volume_fractions)

    else:
        print("warning: number of particles != 2")
        j=0
        for w_frac in weight_frac:
            vol_frac, par_dens = st.particlesInVolumeLogNormWeightTotal(w_frac, dens_p[j], dens_host, mu[j], sigma[j], particle_diameters=d)
            particles_in_um3.extend([par_dens])
            volume_fractions.extend([vol_frac])
            j = j+1


    # Particle density
    #NOTE: If more than 1 particle type, use ValueType.Vector !
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



    #get the simulation result values and return them:

    fHvolnew = tracerApp.getField(FieldID.FID_Thermal_absorption_volume, 0)
    #fHvolnew.field2VTKData().tofile('fHvolnewG{}R{}.vtk'.format(z[0],z[1]))
    pickle.dump(fHvolnew, open('ThAbsVolField_G{}R{}.pickle'.format(z[0],z[1]), 'wb'))
    
    p = tracerApp.getProperty(PropertyID.PID_LEDCCT, 0,
                              objectID=objID.OBJ_LED)
    print('CCT: %f' % p.getValue())
    p_radpower = tracerApp.getProperty(PropertyID.PID_LEDRadiantPower, 0,
                                  objectID=objID.OBJ_LED)
    print('RadiantPower: %f' % p_radpower.getValue())

    p_x = tracerApp.getProperty(PropertyID.PID_LEDColor_x, 0,
                                  objectID=objID.OBJ_LED)
    print('Color x: %f' % p_x.getValue())
    p_y = tracerApp.getProperty(PropertyID.PID_LEDColor_y, 0,
                                  objectID=objID.OBJ_LED)
    print('Color y: %f' % p_y.getValue())
    p_led = tracerApp.getProperty(PropertyID.PID_LEDSpectrum, 0,
                                  objectID=objID.OBJ_LED)
    print(p_led.getValue()['wavelengths'][0:10])
    print(p_led.getValue()['intensities'][0:10])
    pickle.dump(p_led, open('LEDspectrum_G{}R{}.pickle'.format(z[0],z[1]), 'wb'))

    #return X, Y, CCT, Radiant power, and LEDSpectrum:
    p_cct = tracerApp.getProperty(PropertyID.PID_LEDCCT, 0,
                              objectID=objID.OBJ_LED)
    return (p_x.getValue(), p_y.getValue(), p_cct.getValue(), p_radpower.getValue(), p_led)



global cx
global cy
global sim_cct
global sim_radpower
global sim_ledspectrum
sim_ledspectrum = []
sim_radpower = []
sim_cct = []
cx = []
cy = []
#function to be interpolated:
def f(z, *params):
    #cct, led = xsim(z, *params)
    c_x, c_y, c_cct, c_rpow, c_ledspect = xsim(z, *params)
    cx.append(c_x)
    cy.append(c_y)
    sim_cct.append(c_cct)
    sim_radpower.append(c_rpow)
    sim_ledspectrum.append(c_ledspect)
    return((abs(xyz[0] - c_x)**2 + abs(xyz[1] - c_y)**2)**(1/2.0))


#ranges for each changing parameter:
#range for z=weight_fraction, 0...100
xs = np.arange(1, 21, 5) #start, stop, step
ys = np.arange(1, 21, 5)
#NOTE: cubic interpolation requires at least 16 data points!



xxs = []
yys = []
fs = []


# HINT: run this once and copy the values below for faster testing
for i in range(0, len(xs), 1):
    for j in range(0, len(ys), 1):
        xxs.append(xs[i])
        yys.append(ys[j])
        z = np.array([xs[i], ys[j]])
        fs.append(f(z, params))


"""

#TEMPORARY TEST VALUES (got from above simulations):
xxs = [5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 20, 20, 20, 20, 20, 20, 25, 25, 25, 25, 25, 25, 30, 30, 30, 30, 30, 30]
yys = [5, 10, 15, 20, 25, 30, 5, 10, 15, 20, 25, 30, 5, 10, 15, 20, 25, 30, 5, 10, 15, 20, 25, 30, 5, 10, 15, 20, 25, 30, 5, 10, 15, 20, 25, 30]

fs = [0.069050737190116965, ...]

cx =  [0.31567361194155563, ...]

cy = [0.35286768684384129, ...]

sim_cct = [6199.3109214866454, ...]

sim_radpower= [0.073300958696176449, ...]
"""


print("xs:", xs)
print("ys:", ys)
print("xxs:", xxs)
print("yys:", yys)
print("fs:", fs)
print("cx:", cx)
print("cy:", cy)
print("cct:", sim_cct)
print("radiant power:", sim_radpower)

dfile = open("optimization_data.txt", 'w')

for i in range(0, len(xxs)):
   print(i)
   dfile.write("%f %f %f %f %f %f %f\n" % (xxs[i], yys[i], fs[i], cx[i], cy[i], sim_cct[i], sim_radpower[i]))

dfile.close()



#optimization:
from scipy import optimize

#interpolation:
from scipy import interpolate
g = interpolate.interp2d(xxs, yys, fs, kind='linear', bounds_error=False,
fill_value=[10000] )

# fill_value="extrapolate")
#kind = 'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
#bounds_error=False --> extrapolation if out of range values
#fill_value='extrapolate' only for kind={linear, nearest}, scipy version 0.17.0
#fill_value=(0, 0) means that 0 (the first) is used for extrapolated values on the left of the range, and 0 (the latter) for right side of range; scipy version 0.17.0
#fill_value=[10000]; some big number that will not be a minimum..

#find the min value and coordinates, start from the middle point: 
middle = np.array([xxs[len(xxs)/2], yys[len(yys)/2]])
print("middle = ", middle)
print("g(middle)=", g(middle[0], middle[1]))


def absg3(z):
    return abs(g(z[0], z[1]))


solution = optimize.basinhopping(absg3, middle, niter=50000)

print(solution)


