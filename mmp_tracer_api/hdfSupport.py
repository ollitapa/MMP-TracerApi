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

import h5py as h5
import numpy as np
import logging
import logging.config
logger = logging.getLogger('mmpraytracer')


def writeMieDataHDF(wavelengths,
                    particle_diameters,
                    scatteringCrossSections,
                    inverseCDF,
                    out_fname):
    """
    Write scattering data to HDF5 format recognized by the ray tracer.

    Parameters
    ----------
    wavelengths : ndarray
                  Array of wavelengths
    particle_diameters : ndarray
                         Array of particle diameters
    scatteringCrossSections : dict of ndarrays
                              Dictionary of arrays of crosssections for each
                              particle diameter. Keys should be the items in
                              `particle_diameters`
    inverseCDF : dict of ndarrays
                 Dictionary of 2D ndarrays of inversCDFs for each particle
                 type. In the 2D array column=wavelength, row=inverseCDF
                 Keys should be the items in `particle_diameters`
    out_fname : string
                Output filename

    """
    logger.debug("Saving Mie-data...")

    # print(df.info())

    # Create file for saving data
    f = h5.File(out_fname, "w")

    # Save each particle diameter
    f.create_dataset("particleDiameter",
                     data=particle_diameters)
    f.create_dataset("wavelengths",
                     data=wavelengths)

    # Group values for each particle type.
    pDataG = f.create_group("particleData")
    p_id = 0
    for p in particle_diameters:
        grp = pDataG.create_group(str(p_id))

        # Save each inverseCDF.
        # Column = wavelength
        # Row = inverseCDF
        grp.create_dataset("inverseCDF",
                           data=inverseCDF[p])
        # Save crosssections for each wavelength
        grp.create_dataset("crossSections",
                           data=scatteringCrossSections[p])
        p_id += 1

    # Save identifier for each particle size
    f.create_dataset("particleID",
                     data=np.arange(p_id))

    f.close()
    logger.debug("Saved!")
