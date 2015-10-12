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
import numpy as np
from scipy import integrate
from pyraytracer import scatteringTools as sc


def writeExAbsSpectrumFile(wavelengths, intensities, fname):
    '''
    Helper function to write Excitation and Emission spectrum in file
    for the mmpraytracer

    Parameters
    ----------
    wavelengths : list like
                  Wavelengths of the spectrum.
    intensities : list like
                  Intensities of the spectrum.
    fname : str
            Filepath to save the spectrum.
    '''
    A = np.array([wavelengths, intensities])
    np.savetxt(fname, A.T)


def writeEmissionSpectrumFile(wavelengths, intensities, fname, n_rv=10000):
    '''
    Helper function to write Excitation and Emission spectrum in file
    for the mmpraytracer

    Parameters
    ----------
    wavelengths : list like
                  Wavelengths of the spectrum.
    intensities : list like
                  Intensities of the spectrum.
    fname : str
            Filepath to save the spectrum.
    n_rv : int
           Number of random variables the spectrum is divided. Default 10000.

    '''
    intensities = np.atleast_1d(intensities)
    wavelengths = np.atleast_1d(wavelengths)

    # Invert emission spectrum
    intensEMone = intensities / np.trapz(intensities, x=wavelengths)
    rv = np.linspace(0, 1, n_rv)
    cumEM = integrate.cumtrapz(intensEMone, wavelengths, initial=0)
    invCumEM = sc.invertNiceFunction(wavelengths, cumEM, rv)

    np.savetxt(fname, invCumEM)

if __name__ == '__main__':
    writeExAbsSpectrumFile([1, 2, 3], [7, 8, 9], 'koe.txt')
    writeEmissionSpectrumFile([400, 500, 600], [1, 2, 3], 'koeEM.txt')
