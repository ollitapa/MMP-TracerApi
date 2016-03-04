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

from mmp_mie_api import MMPMie
from mmp_tracer_api import MMPRaytracer, objID
from comsol_api import MMPComsolDummy
import numpy as np

from mupif import PropertyID, FieldID, Property, ValueType
import logging
import logging.config
import os

if not os.path.isdir('runFolder'):
    os.mkdir('runFolder')
os.chdir('runFolder')


if __name__ == '__main__':

    # create a new logger, MMPRaytracer class creates a logger
    # that logs at the INFO-level. Use this place to set for debug level.
    logging.config.fileConfig('../../loggingNew.conf')

    logger = logging.getLogger('mmpraytracer')
    print("#######################################")
    print("######### Active Logging info #########")
    logger.debug('messages will be logged')
    logger.info('messages will be logged')
    logger.warn('messages will be logged')
    logger.error('messages will be logged')
    logger.critical('messages will be logged')
    print("#######################################")

    # Initialise apps
    mieApp = MMPMie('localhost')
    tracerApp = MMPRaytracer('localhost')
    comsolApp = MMPComsolDummy('localhost')

    logger.info('Connecting Mie properties...')
    pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                               objID.OBJ_PARTICLE_TYPE_1)

    pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                                objID.OBJ_PARTICLE_TYPE_1)

    logger.info('Props received...')
    tracerApp.setProperty(pScat, objID.OBJ_PARTICLE_TYPE_1)
    tracerApp.setProperty(pPhase, objID.OBJ_PARTICLE_TYPE_1)
    logger.info('Props connected')

    # Connect fields
    fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
    fHeat = comsolApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

    tracerApp.setField(fTemp)
    tracerApp.setField(fHeat)

    # Connect properties
    # Particle density
    vDens = 0.00000003400
    pDens = Property.Property(value=vDens,
                              propID=PropertyID.PID_ParticleNumberDensity,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
    tracerApp.setProperty(pDens)

    # Number of rays to trace
    pRays = Property.Property(value=100,
                              propID=PropertyID.PID_NumberOfRays,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
    tracerApp.setProperty(pRays)

    # Emission spectrum
    import numpy as np

    #a = {'wavelengths': None, 'intensities': None}
    a = {}
    #A=np.loadtxt(resource_filename(__name__, "data/InvCumul_EM_GREEN.dat"))
    A = np.loadtxt('../../../mmp_tracer_api/data/EM_GREEN.dat')
    a['wavelengths'] = A[:, 0]
    a['intensities'] = A[:, 1]
    em = Property.Property(value=a,
                           propID=PropertyID.PID_EmissionSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_1)
    tracerApp.setProperty(em)

    # Excitation spectrum
    b = {}
    B = np.loadtxt('../../../mmp_tracer_api/data/EX_GREEN.dat')
    b['wavelengths'] = B[:, 0]
    b['intensities'] = B[:, 1]
    ex = Property.Property(value=b,
                           propID=PropertyID.PID_ExcitationSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_1)
    tracerApp.setProperty(ex)

    # Absorption spectrum
    c = {}
    C = np.loadtxt('../../../mmp_tracer_api/data/Abs_GREEN.dat')
    c['wavelengths'] = C[:, 0]
    c['intensities'] = C[:, 1]
    aabs = Property.Property(value=c,
                             propID=PropertyID.PID_AsorptionSpectrum,
                             valueType=ValueType.Scalar,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_PARTICLE_TYPE_1)
    tracerApp.setProperty(aabs)



    # Solve
    times = np.arange(0, 3)
    for t in times:
        mieApp.solveStep(t)
        tracerApp.solveStep(t, runInBackground=False)
        comsolApp.solveStep(t)

    fHeat = tracerApp.getField(FieldID.FID_Thermal_absorption_volume, 1.5)
    pDens = tracerApp.getProperty(propID=PropertyID.PID_ParticleNumberDensity,
                                  objectID=objID.OBJ_CONE, time=1.5)

    # print('%.10f' % pDens.value)

    # Plot data to file
    logger.info("Saving vtk")
    v = fHeat.field2VTKData()
    v.tofile('testHeat.vtk')
