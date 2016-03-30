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

    p_max = 35.0
    p_min = 1.0
    p_num = 50

    w_max = 1100.0
    w_min = 100.0
    w_num = 1001


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
    weight_frac = z / 100.0
    print("z, weight_frac = ", z, weight_frac)

    #run the simulation:
    
    # Number of rays to trace
    pRays = Property.Property(value=1000000,
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
    j=0
    for w_frac in weight_frac:
        particles_in_um3.extend([st.particlesInVolumeLogNormWeightTotal(w_frac, dens_p, dens_host, mu[j], sigma[j], particle_diameters=d)])
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



#function to be interpolated:
def f(z, *params):
    return (x[0] - xsim(z, *params))


#ranges for each changing parameter:
#range for z=weight_fraction, 0...100
xs = np.arange(5, 26, 5) #start, stop, step
ys = np.arange(10, 31, 5)
#NOTE: cubic interpolation requires at least 16 data points!



xxs = []
yys = []
fs = []

"""
# HINT: run this once and copy the values below for faster testing
for i in range(0, len(xs), 1):
    for j in range(0, len(ys), 1):
        xxs.append(xs[i])
        yys.append(ys[j])
        z = np.array([xs[i], ys[j]])
        fs.append(f(z, params))

"""

#TEMPORARY TEST VALUES (got from above simulations):
xxs = [5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 20, 20, 20, 20, 20, 25, 25, 25, 25, 25]
yys = [10, 15, 20, 25, 30, 10, 15, 20, 25, 30, 10, 15, 20, 25, 30, 10, 15, 20, 25, 30, 10, 15, 20, 25, 30]

fs = [2139.3130012902275, 2148.9119575875056, 2145.6384244346173, 2135.3884501238626, 2139.9678900251238, 1261.0473650652693, 1169.61741228965, 1157.1989127471534, 1075.5214412899168, 930.18863193348989, -122.64386155575085, -214.79047218466985, -447.12264333593885, -614.5940055858282, -1047.4779911078531, -1597.5935138968325, -1729.1793549837475, -1883.0947305989339, -1724.0829276074965, -1265.1871413612007, -1100.0840272872574, 318.48324287984178, 4881.8581277551366, 7965.6222053979818, 28473.311061883891]




print("xs:", xs)
print("ys:", ys)
print("xxs:", xxs)
print("yys:", yys)
print("fs:", fs)


#optimization:
from scipy import optimize

#interpolation:
from scipy import interpolate
g = interpolate.interp2d(xxs, yys, fs, kind='cubic', bounds_error=False,
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
print("abs g middle=", abs(g(middle[0], middle[1])))

def absg(z):
    return abs(g(z[0],z[1]))

solution = optimize.minimize(absg, middle, method='Powell')
print(solution)

#Plot the simulated values:
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from scipy import meshgrid
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_trisurf(xxs, yys, fs, cmap=cm.jet, linewidth=0)
fig.colorbar(surf)

title = ax.set_title("CCT=4000, difference with 2 particle weight fractions")
title.set_y(1.01)

ax.xaxis.set_major_locator(MaxNLocator(5))
ax.yaxis.set_major_locator(MaxNLocator(6))
ax.zaxis.set_major_locator(MaxNLocator(5))

fig.tight_layout()
N = 1000000 #number of rays
fig.savefig('3D-CCT-{}.png'.format(N))

# Plot the interpolated values:
ixs = []
iys = []
izs = []
for i in range(5, 25, 1):
    for j in range(10, 30, 1):
        ixs.append(i)
        iys.append(j)
        #z = np.array([i, j])
        izs.append(g(i, j)[0])

print('ixs=', ixs)
print('iys=', iys)
print('izs=', izs)

fig2 = plt.figure()
ax2 = fig2.add_subplot(111, projection='3d')
surf2 = ax2.plot_trisurf(ixs, iys, izs, cmap=cm.jet, linewidth=0)
fig2.colorbar(surf2)
title2 = ax2.set_title("interpolated CCT difference from 4000")
title2.set_y(1.01)
ax2.xaxis.set_major_locator(MaxNLocator(5))
ax2.yaxis.set_major_locator(MaxNLocator(6))
ax2.zaxis.set_major_locator(MaxNLocator(5))

fig2.tight_layout()
fig2.savefig('3D-CCT-interpolated.png')


