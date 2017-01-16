#
# Copyright 2015 VTT Technical Research Center of Finland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from scipy.integrate import cumtrapz
from scipy.interpolate import griddata
from scipy.stats import lognorm
from scipy.optimize import curve_fit
import numpy as np


def fitLogNormParticleDistribution(D10, D50, D90):
    '''
    Fitting function to get the mu and sigma -parameters of the Log-normal
    distribution from cumulative particle distribution values D10, D50 and D90.
    The DXX are values that the cumulative particle distribution function gets
    at those points. For example D10 means that 10% of particle are smaller
    than this size.

    d10 = 7.3
    d50 = 12.0
    d90 = 18.3

    (mu, sigma) = fitLogNormParticleDistribution(d10, d50, d90)
    print(mu, sigma)

    '''

    mu = np.log(D50)  # fixed by definition

    def errfunc(mu_, sig_):
        N = lognorm(sig_, scale=np.exp(mu_))
        # minimize ze difference between D10 and D90 to cumulative function
        # Weight the D10 more by 2*
        zero = 2 * np.abs(0.1 - N.cdf(D10)) + np.abs(0.9 - N.cdf(D90))
        return(zero)

    sigma, pcov = curve_fit(errfunc, [mu], [0])
    print(sigma)

    return(mu, sigma[0])


def particlesInVolumeLogNormWeight(weight_frac, density_p, density_host,
                                   mu, sigma, particle_diameters):
    '''
    Function that calculates particle densities in a volume element for
    given weight fraction.
    Presumes LogNormal particle distribution
    '''
    print('Weight fraction is %.1f %%' % (weight_frac * 100))
    w = weight_frac
    vol_frac = w * density_host / density_p / (1 + w * (
                                               density_host / density_p - 1))
    print('Volume fraction is %.1f %%' % (vol_frac * 100))
    return(particlesInVolumeLogNorm(vol_frac, mu, sigma, particle_diameters))


def particlesInVolumeLogNormWeightTotal(weight_frac, density_p, density_host,
                                        mu, sigma, particle_diameters):
    '''
    IF ONLY 1 PARTICLE TYPE IN SILICONE!
    Returns the total number of particles in volume element.
    Presumes LogNormal particle distribution
    '''
    print('Weight fraction is %.1f %%' % (weight_frac * 100))
    w = weight_frac
    vol_frac = w * density_host / density_p / (1 + w * (
                                               density_host / density_p - 1))
    print('Volume fraction is %.1f %%' % (vol_frac * 100))
    return(vol_frac, particlesInVolumeLogNormTotal(vol_frac, mu, sigma,
                                         particle_diameters))

def particlesInVolumeLogNormWeightTotal2(weight_frac1, weight_frac2, dens_p1, dens_p2, dens_host, mu, sigma, particle_diameters):
    '''
    IF 2 PARTICLE TYPES IN SILICONE!
    Returns the total number of particles in volume element.
    Presumes LogNormal particle distribution
    '''
    print('Weight fraction is %.1f %%' % (weight_frac1 * 100))
    w_p1 = weight_frac1
    w_p2 = weight_frac2
    w_s = 1.0 - w_p1 - w_p2

    vol_frac = (dens_host * dens_p2 * w_p1) / (w_s * dens_p1 * dens_p2 + w_p1 *dens_host * dens_p2 + w_p2 * dens_host * dens_p1)
    print('Volume fraction is %.1f %%' % (vol_frac * 100))
    return(vol_frac, particlesInVolumeLogNormTotal(vol_frac, mu, sigma,
                                         particle_diameters))


def particlesInVolumeLogNorm(vol_frac, mu, sigma, particle_diameters):
    '''
    Function that calculates particle densities in a volume element.
    The particles are diameters are log-normally distributed (sigma, mu)
    and they have a given volume fraction.
    '''

    D = particle_diameters

    # Calculate particle density(particles per um ^ 3)
    N = lognorm(sigma, scale=np.exp(mu))
    # Weight factors of each particle size
    pdf = N.pdf(D)

    # Volume of particle having radius R[m ^ 3]
    Vsph = 4.0 / 3.0 * np.pi * (D / 2.0) ** 3.0

    # Particle volumes multiplied with weight factors = > volume distribution
    WV = pdf * Vsph

    # Total volume of the volume distribution
    Vtot = np.trapz(WV, D)
    # Number of particles in um ^ 3
    n_part = vol_frac / Vtot

    print('Number of particles in cubic micrometer = %.18f' % n_part)

    # Check, should give the volume fraction in %
    print("Volume fraction was: %.1f %%" %
          (np.trapz(n_part * pdf * Vsph, D) * 100))
    bins = pdf * (D[1] - D[0])
    # print(bins.sum())
    return(n_part * bins)


def particlesInVolumeLogNormTotal(vol_frac, mu, sigma, particle_diameters):
    n = particlesInVolumeLogNorm(vol_frac, mu, sigma, particle_diameters)
    print("n=", n)
    print("n.sum()=", n.sum())
    return(n.sum())


def rayleighScatteringCrossSection(wavelengths,
                                   particle_refractive_index,
                                   particle_diameter):
    d = particle_diameter
    n = particle_refractive_index
    l = wavelengths

    cross = ((2.0 * (np.pi ** 5.0) * d ** 6.0) / (3 * l ** 4.0) *
             (((n ** 2.0) - 1.0) / ((n ** 2.0) + 2.0)) ** 2.0)

    return(cross)


def rayleighScatteringPhaseFunction(cosTheta):

    return(3.0 / 4.0 * (1 + cosTheta ** 2))


def henyeyGreensteinPhaseFunction(cosTheta, asymmetry_factor):
    g = asymmetry_factor
    p = 0.5 * (1.0 - g ** 2) / (1 + g ** 2 - 2 * g * cosTheta) ** (3.0 / 2.0)
    return(p)


def cumulativeDistribution(phaseFunction, cosTheta):
    return(-0.5 * cumtrapz(phaseFunction, cosTheta, initial=0))


def cumulativeDistributionTheta(phaseFunction, theta):
    return(cumtrapz(phaseFunction * np.sin(theta), theta, initial=0))


def invertNiceFunction(x, y, yi):
    new_y = griddata(y, x, yi)
    if np.isnan(new_y[0]):
        new_y[0] = x[0]

    if np.isnan(new_y[-1]):
        new_y[-1] = x[-1]
    return(new_y)

'''
th = np.arange(0, 180, 0.5)
th = np.radians(th)

rv = np.linspace(0, 1, 1000)

phase = rayleighScatteringPhaseFunction(np.cos(th))
phase = henyeyGreensteinPhaseFunction(np.cos(th), -0.6)
cumul = cumulativeDistribution(phase, np.cos(th))
invers = invertNiceFunction(np.cos(th), cumul, rv)


plt.plot(rv, np.degrees(np.arccos(invers)))
plt.show()
print(np.degrees(np.arccos(invers)))
'''
'''
if __name__ == '__main__':
    particlesInVolumeLogNormWeightTotal(weight_frac=0.24,
                                        density_p=5.0,
                                        density_host=1.1,
                                        mu=1, sigma=1,
                                        particle_diameters=np.array([1, 2]))
    particlesInVolumeLogNormWeight(weight_frac=0.24,
                                   density_p=5.0,
                                   density_host=1.1,
                                   mu=1, sigma=1,
                                   particle_diameters=np.array([1, 2]))
'''
