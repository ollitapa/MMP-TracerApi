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

from mupif import PropertyID, FieldID, FunctionID, Property, ValueType
import logging
import logging.config
import ex_em_import
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

    # Set default LED json
    tracerApp.setDefaultInputFile('../../DefaultLED.json')

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

    # Connect properties
    # Particle density
    vDens = 0.00003400
    pDens = Property.Property(value=vDens,
                              propID=PropertyID.PID_ParticleNumberDensity,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
    tracerApp.setProperty(pDens)

    # Number of rays to trace
    pRays = Property.Property(value=100000,
                              propID=PropertyID.PID_NumberOfRays,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
    tracerApp.setProperty(pRays)
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

    hmri = Property.Property(1.55, PropertyID.PID_RefractiveIndex,
                             valueType=ValueType.Scalar,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_CONE)
    mieApp.setProperty(hmri)

    logger.info('Properties set!')

    # Solve
    mieApp.solveStep(0)
    tracerApp.solveStep(0, runInBackground=False)
    comsolApp.solveStep(0)

    # Plot data to file
    logger.info("Saving vtk")
    v = fTemp.field2VTKData()
    v.tofile('testTemperature.vtk')
    v = fHeat.field2VTKData()
    v.tofile('testHeat.vtk')
