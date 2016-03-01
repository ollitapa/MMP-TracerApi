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

import os
import socket
from subprocess import Popen, PIPE
import sys
import threading
from pkg_resources import resource_filename

import Pyro4
from mupif import APIError
from mupif import Property, Field, Mesh
from mupif import FunctionID, FieldID, PropertyID
# from mupif.fieldID import FieldID
# from mupif.propertyID import PropertyID
from mupif import TimeStep
from mupif import ValueType
from mupif.Application import Application
import numpy as np
import pandas as pd
import vtkSupport as vtkS
import mmpMeshSupport as meshS
import generalSupport as gS
import hdfSupport as hdfS
import json
import initialConfiguration as initConf
import interpolationSupport as interP
import objID
import logging
import logging.config
from pyraytracer import detectorTools as dt
from pyraytracer import fileTools as ft

# create logger
logging.config.fileConfig(resource_filename(__name__, 'data/logging.conf'),
                          disable_existing_loggers=False)
logger = logging.getLogger('mmpraytracer')
# logger.debug('messages will be logged')
# logger.info('messages will be logged')
# logger.warn('messages will be logged')
# logger.error('messages will be logged')
# logger.critical('messages will be logged')


sys.excepthook = Pyro4.util.excepthook
Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle', 'serpent', 'json']
Pyro4.config.SERIALIZER = 'pickle'


class MMPRaytracer(Application):

    """
    Mupif interface to mmpraytracer (phosphor raytracing)

    """

    _absorptionFilePath = "AbsorptionData.vtp"
    _absorptionFilePathSurface = "SurfaceAbsorptionData.vtp"
    _defaultInputfilePath = resource_filename(__name__, 'data/DefaultLED.json')
    _rayFilePath = "AllDetector_1_Pallo.bin"

    _curTStep = -1
    _convertPointData = True

    def __init__(self, file, workdir='.'):
        super(MMPRaytracer, self).__init__(file, workdir)  # call base
        os.chdir(workdir)

        # Containers
        # Properties
        # Key should be in form of tuple (propertyID, objectID, tstep)
        idx = pd.MultiIndex.from_tuples([(PropertyID.PID_LEDColor_x,
                                          1.0, 1.0)],
                                        names=['propertyID',
                                               'objectID',
                                               'tstep'])
        self.properties = pd.Series(index=idx, dtype=Property.Property)

        # Fields
        # Key should be in form of tuple (fieldID, tstep)
        idxf = pd.MultiIndex.from_tuples(
            [(FieldID.FID_Thermal_absorption_volume, 1.0)],
            names=['fieldID', 'tstep'])
        self.fields = pd.Series(index=idxf, dtype=Field.Field)

        # Functions, simple dictionary
        # Key should be in form of tuple (functionID, objectID)
        self.functions = {}

        # Initialise processes
        if os.name == "nt":
            self.tracerProcess = Popen(
                ["dir"], stdout=PIPE, stderr=PIPE, shell=True)
            self.postThread = Popen(
                ["dir"], stdout=PIPE, stderr=PIPE, shell=True)
        else:
            self.tracerProcess = Popen(["ls"], stdout=PIPE, stderr=PIPE)
            self.postThread = Popen(["ls"], stdout=PIPE, stderr=PIPE)

        # Load default values
        f = open(self._defaultInputfilePath, 'r')
        self._jsondata = json.load(f)
        f.close()

        # Initialise the app
        self._initialiseDefault()

        return

    def getField(self, fieldID, time):
        """
        Returns the requested field at given time.
        Field is identified by fieldID.

        :param FieldID fieldID: Identifier of the field
        :param float time: Target time

        :return: Returns requested field.
        :rtype: Field
        """

        key = (fieldID, time)
        field = 0
        if fieldID not in self.fields.index:
            raise APIError.APIError('Unknown field ID')
        if time not in self.fields.index:
            field = interP.interpolateFields(self.fields,
                                             time, fieldID,
                                             method='linear')
        else:
            field = self.fields[key]

        # Check if object is registered to Pyro
        # if hasattr(self, '_pyroDaemon') and not hasattr(field, '_PyroURI'):
        #    uri = self._pyroDaemon.register(field)
        #    field._PyroURI = uri

        return(field)

    def setField(self, field):
        """
        Registers the given (remote) field in application.

        :param Field field: Remote field to be registered by the application
        """

        # Set the new property to container
        key = (field.getFieldID(), field.getTime())
        self.fields.set_value(key, field)

    def getProperty(self, propID, time, objectID=0):
        """
        Returns property identified by its ID evaluated at given time.

        :param PropertyID propID: property ID
        :param float time: Time when property should to be evaluated
        :param int objectID: Identifies object/submesh on which property is
        evaluated (optional, default 0)

        :return: Returns representation of requested property
        :rtype: Property
        """
        key = (propID, objectID, time)
        if propID not in self.properties.index:

            raise APIError.APIError('Unknown property ID')

        if time not in self.properties.index:
            prop = interP.interpolateProperty(self.properties,
                                              time=time,
                                              propertyID=propID,
                                              objectID=objectID,
                                              method='linear')
        else:
            prop = self.properties[key]

        # Check pyro registering if applicaple
        if hasattr(self, '_pyroDaemon') and not hasattr(prop, '_PyroURI'):
            uri = self._pyroDaemon.register(prop)
            prop._PyroURI = uri

        return(prop)

    def setProperty(self, newProp, objectID=0):
        """
        Register given property in the application

        :param Property property: Setting property
        :param int objectID: Identifies object/submesh on which property is
               evaluated (optional, default 0)
        """

        # Set the new property to container
        key = (newProp.getPropertyID(),
               newProp.getObjectID(),
               newProp.time)  # TODO: update to getTime for pyro4
        self.properties.set_value(key, newProp)

    def getMesh(self, tstep):
        """
        Returns the computational mesh for given solution step.

        :param TimeStep tstep: Solution step
        :return: Returns the representation of mesh
        :rtype: Mesh
        """
        return(self.fields.xs(tstep, level='time')[0].getMesh())

    def solveStep(self, tstep, stageID=0, runInBackground=False):
        """
        Solves the problem for given time step.

        Proceeds the solution from actual state to given time.
        The actual state should not be updated at the end,
        as this method could be
        called multiple times for the same solution step
        until the global convergence
        is reached. When global convergence is reached,
        finishStep is called and then
        the actual state has to be updated.
        Solution can be split into individual stages
        identified by optional stageID parameter.
        In between the stages the additional data exchange can be performed.
        See also wait and isSolved services.

        :param TimeStep tstep: Solution step
        :param int stageID: optional argument identifying
               solution stage (default 0)
        :param bool runInBackground: optional argument, defualt False.
               If True, the solution will run in background (in separate thread
               or remotely).

        """
        # Check that old simulation is not running:
        if not self.isSolved():
            return

        # Check params and fields
        initConf.checkRequiredFields(self.fields, FieldID)
        initConf.checkRequiredParameters(self.properties, PropertyID)
        initConf.checkRequiredFunctions(self.functions, fID=FunctionID)

        # Set current tstep and copy previous results as starting values
        self._curTStep = tstep
        self._copyPreviousSolution()

        # Write out JSON file.
        self._writeInputJSON(tstep)

        # Get mie data from other app
        self._getMieData(tstep)

        # Start thread to start calculation
        self.tracerProcess = Popen(  # ["ping", "127.0.0.1",  "-n",
            # "3", "-w", "10"],
            # self.tracerProcess = Popen(["tracer",
            # "DefaultLED.json"],
            ["tracer-no-ray-save", "input.json"],
            stdout=PIPE,
            stderr=PIPE)

        # This thread will callback when tracer has ended.
        self.postThread = threading.Thread(target=self._runCallback,
                                           args=(self.tracerProcess,
                                                 self._tracerProcessEnded))
        # Post processing thread will wait for the tracer to finnish
        logger.info('Ray tracing starting...')
        self.postThread.start()

        # Wait for process if applicaple
        if not runInBackground:
            self.wait()

    def wait(self):
        """
        Wait until solve is completed when executed in background.
        """
        logger.debug("Tracing...")
        self.tracerProcess.wait()
        logger.debug("Post processing...")
        self.postThread.join()
        logger.debug("Post processing done!")

    def isSolved(self):
        """
        :return: Returns true or false depending whether solve has completed
                 when executed in background.
        :rtype: bool
        """
        if self.tracerProcess.poll() is not None:
            return True
        if self.postThread.poll() is not None:
            return True
        return False

    def getCriticalTimeStep(self):
        """
        :return: Returns the actual (related to current state) critical time
        step increment
        :rtype: float
        """
        # TODO: Check
        return np.Infinity  # Tracer does not have any time dependence...

    def getAPIVersion(self):
        """
        :return: Returns the supported API version
        :rtype: str, int
        """
        # TODO: API version support?? How
        return('1.0', 1)

    def getApplicationSignature(self):
        """
        :return: Returns the application identification
        :rtype: str
        """
        return("MMP-Raytracer@" + socket.gethostbyaddr(socket.gethostname())[0]
               + " version 0.1")

    def terminate(self):
        """
        Terminates the application.
        """
        if not self.isSolved():
            self.tracerProcess.terminate()
            self.postThread.terminate()
        if self.pyroDaemon:
            self.pyroDaemon.shutdown()

    def _copyPreviousSolution(self):
        if self._curTStep == 0:
            return

        # Function for finding closest timestep to current time
        def closest_floor(arr):
            tstep = arr.index.get_level_values('tstep')
            t = self._curTStep - tstep > 0
            # print(t)
            return(tstep[t].min())

        # Find closest time and copy fields to current time
        g = self.fields.groupby(level='fieldID').apply(closest_floor)
        for fID in g.index:
            key = (fID, g[fID])
            newKey = (fID, self._curTStep)
            f = self.fields[key]

            newField = Field.Field(f.getMesh(),
                                   f.getFieldID(),
                                   f.getValueType(),
                                   units=f.getUnits(),
                                   values=f.values,
                                   time=self._curTStep,
                                   fieldType=f.fieldType)
            self.fields.set_value(newKey, newField)

        # Find closest time and copy properties to current time
        g = self.properties.groupby(level=('propertyID',
                                           'objectID')).apply(closest_floor)
        for pID in g.index:
            key = (pID[0], pID[1], g[pID])
            newKey = (pID[0], pID[1], self._curTStep)
            p = self.properties[key]
            newProp = Property.Property(value=p.getValue(),
                                        propID=p.getPropertID(),
                                        valueType=p.valueType,
                                        time=self._curTStep,
                                        units=p.getUnits(),
                                        objectID=p.getObjectID())
            self.properties.set_value(newKey, newProp)

    def _writeInputJSON(self, tstep):
        """
        Writes input JSON for the raytracer.
        The fields and parameters should be accessible before
        calling this method.
        """

        # update json based on the Properties:
        # print("Property keys:")
        for key in self.properties.index:
            # print(key)
            prop = self.properties[key]

            if(key[0] == PropertyID.PID_RefractiveIndex and
               key[2] == tstep and key[1] == objID.OBJ_CONE):
                print("PID_RefractiveIndex, ", prop.getValue())
                parent = self._jsondata['materials']
                parent[3]["refractiveIndex"] = prop.getValue()

            elif(key[0] == PropertyID.PID_NumberOfRays and
                 key[2] == tstep):
                print("PID_NumberOfRays, ", prop.getValue())
                parent = self._jsondata['sources']
                for item in parent:
                    item["rays"] = prop.getValue()

            elif(key[0] == PropertyID.PID_ChipSpectrum and
                 key[2] == tstep):
                print("PID_ChipSpectrum, ", prop.getValue())
                parent = self._jsondata['sources']
                for item in parent:
                    item["wavelengths"] = prop.getValue()[
                        "wavelengths"].tolist()
                    item["intensities"] = prop.getValue()[
                        "intensities"].tolist()

            elif(key[0] == PropertyID.PID_ParticleNumberDensity and
                 key[2] == tstep):
                print("PID_ParticleNumberDensity, ", prop.getValue())
                parent = self._jsondata['materials']
                parent[3]["particleDensities"] = [prop.getValue()]
            elif(key[0] == PropertyID.PID_ScatteringCrossSections and
                 key[2] == tstep):
                pass
            elif(key[0] == PropertyID.PID_InverseCumulativeDist and
                 key[2] == tstep):
                pass
        # Datafiles:
        parent = self._jsondata['materials']

        # TODO: need PID for this property!!!
        n_particle_key = (PropertyID.PID_Demo_Value, objID.OBJ_CONE, tstep)
        n_particles = self.properties[n_particle_key]
        parent[3]['numberOfFluorescentParticles'] = n_particles.getValue()
        print("n_particles=", n_particles.getValue(),
              parent[3]['numberOfFluorescentParticles'])

        # Properties containing emission spectrums
        if PropertyID.PID_EmissionSpectrum in\
                self.properties.index.get_level_values('propertyID'):
            em = self.properties.xs((PropertyID.PID_EmissionSpectrum, tstep),
                                    level=('propertyID', 'tstep'))

            em_fname = []
            for i, row in em.iteritems():
                p = row.getValue()
                fname = 'InvCumul_EM_%d.dat' % i
                gS.writeEmissionSpectrumFile(p["wavelengths"],
                                             p["intensities"],
                                             fname)
                em_fname.extend([fname])

            parent[3]["cumulativeEmissionSpectrumFilenames"] = em_fname
            if len(em_fname) != n_particles.getValue():
                raise APIError.APIError("Number of em spectrum file names \
                                        (%d) does not match with number of \
                                        fluorescent particles (%d)" %
                                        (len(em_fname),
                                         n_particles.getValue())
                                        )
        else:
            raise APIError.APIError(
                "Did not find em spectrum file names in Properties!")

        # Excitation spectrum property
        if PropertyID.PID_ExcitationSpectrum in\
                self.properties.index.get_level_values('propertyID'):
            ex = self.properties.xs((PropertyID.PID_ExcitationSpectrum, tstep),
                                    level=('propertyID', 'tstep'))

            ex_fname = []
            for i, row in ex.iteritems():
                p = row.getValue()
                fname = 'InvCumul_EX_%d.dat' % i
                gS.writeExAbsSpectrumFile(p["wavelengths"],
                                          p["intensities"],
                                          fname)
                ex_fname.extend([fname])
            parent[3]["excitationSpectrumFilenames"] = ex_fname

            if len(ex_fname) != n_particles.getValue():
                raise APIError.APIError("Number of ex spectrum file names \
                                        (%d) does not match with number of \
                                        fluorescent particles (%d)" %
                                        (len(ex_fname),
                                         n_particles.getValue())
                                        )
        else:
            raise APIError.APIError(
                "Did not find ex spectrum file names in Properties!")

        # Absorption spectrum property
        if PropertyID.PID_AsorptionSpectrum in\
                self.properties.index.get_level_values('propertyID'):
            aabs = self.properties.xs((PropertyID.PID_AsorptionSpectrum,
                                       tstep),
                                      level=('propertyID', 'tstep'))

            aabs_fname = []
            for i, row in aabs.iteritems():
                p = row.getValue()
                fname = 'InvCumul_ABS_%d.dat' % i
                gS.writeExAbsSpectrumFile(p["wavelengths"],
                                          p["intensities"],
                                          fname)
                aabs_fname.extend([fname])
            parent[3]["absorptionSpectrumFilenames"] = aabs_fname
            if len(aabs_fname) != n_particles.getValue():
                raise APIError.APIError("Number of abs spectrum \
                                        file names (%d) does not match \
                                        with number of fluorescent \
                                        particles (%d)" %
                                        (len(aabs_fname),
                                         n_particles.getValue()))
        else:
            raise APIError.APIError(
                "Did not find abs spectrum file names in Properties!")

        # write the json file:
        f = open('input.json', 'w')
        f.write(json.dumps(self._jsondata))
        f.close()

    def _initialiseDefault(self):
        """
        Initialise default values for properties, fields and funcs.
        Does not initialize properties required to be provided
        by other apps.
        """

        # Empty old properties
        if not self.properties.empty:
            self.properties.drop(self.properties.index, inplace=True)
        # Empty old fields
        if not self.fields.empty:
            self.fields.drop(self.fields.index, inplace=True)

        # Empty functions
        self.functions = {}

        initConf.initialProps(self.properties, self._jsondata, PropertyID)
        initConf.initialField(self.fields, self._jsondata, FieldID)
        initConf.initialFunc(self.functions, self._jsondata, FunctionID)

    def _tracerProcessEnded(self, lines):
        # Check if process ended correctly
        # TODO! raise APIError (temporarily commented out for testing)
        if "########## Tracing done ################" in lines:
            logger.info("Tracing successful!")
        else:
            for line in lines:
                logger.debug(line)
            print(lines)
            logger.info("Tracing was not successful!")
            raise APIError.APIError("Tracing was not successful!")

        # Read absorption data
        (points, absorb) = vtkS.readAbsorptionData(self._absorptionFilePath)
        # print(points)
        # print(absorb)

        # Get field
        key = (FieldID.FID_Thermal_absorption_volume, self._curTStep)
        print(self.fields)
        f = self.fields[key]

        # Convert point data to field mesh
        if self._convertPointData:
            if meshS.FASTisAvailable():
                meshS.convertPointDataToMeshFAST(
                    pointdataVTKfile=self._absorptionFilePath,
                    field=f, inplace=True)
            else:
                meshS.convertPointDataToMesh(points, absorb, f, inplace=True)

        # Read line data (if needed): (TODO: not tested)
        # (pts, wv, offs) = vtkS.readLineData("ray_paths.vtp")

        # Read photometric data from overall detector
        df = ft.loadDetectorData('AllDetector_1_LED.bin')
        data = dt.convertToSphere(df)

        # Set data to properties
        # Spectrum
        key = (PropertyID.PID_LEDSpectrum, objID.OBJ_LED,
               self._curTStep)
        p = self.properties[key]
        p.value['wavelengths'] = data['wavelengths']
        p.value['intensities'] = data['intensities']

        # Color x
        key = (PropertyID.PID_LEDColor_x, objID.OBJ_LED,
               self._curTStep)
        p = self.properties[key]
        p.value = data['color_x']

        # Color y
        key = (PropertyID.PID_LEDColor_y, objID.OBJ_LED,
               self._curTStep)
        p = self.properties[key]
        p.value = data['color_y']

        # CCT
        key = (PropertyID.PID_LEDCCT, objID.OBJ_LED,
               self._curTStep)
        p = self.properties[key]
        p.value = data['CCT']

        # RadPower
        key = (PropertyID.PID_LEDRadiantPower, objID.OBJ_LED,
               self._curTStep)
        p = self.properties[key]
        p.value = data['radPower']

    def _runCallback(self, pHandle, callback):
        '''
        Method that excecutes callback method after process
        pHandle is ready.
        Callback should take one argument: lines of the stdout.
        '''
        # Read output. Otherwise the stdout will run out of buffer and hang
        lines = []
        with pHandle.stdout:
            for line in iter(pHandle.stdout.readline, ''):
                lines.extend([line.rstrip()])
        with pHandle.stderr:
            for line in iter(pHandle.stderr.readline, ''):
                lines.extend([line.rstrip()])
        # print(lines)
        pHandle.wait()
        callback(lines)
        return

    def _getMieData(self, tstep):

        logger.debug("Getting mie data...")

        # Wavelengths used
        # key = (PropertyID.PID_LEDSpectrum, objID.OBJ_CHIP_ACTIVE_AREA, 0)
        # wave = self.properties[key].getValue()['wavelengths']
        # TODO: These should be same with MieAPI!! pidetaan vakioina!
        w_max = 1100.0
        w_min = 100.0
        w_num = 10

        wave = np.linspace(w_min, w_max, w_num)

        # Find scattering cross-sections and corresponding invCDF:

        oids = []
        scs = {}
        icdf = {}
        if PropertyID.PID_ScatteringCrossSections in\
                self.properties.index.get_level_values('propertyID'):
            sc = self.properties.xs((PropertyID.PID_ScatteringCrossSections,
                                     tstep),
                                    level=('propertyID', 'tstep'))

            for i, row in sc.iteritems():
                sc_prop = row
                oids.append(sc_prop.getObjectID())
                scs[sc_prop.getObjectID()] = sc_prop.getValue()
                key = (PropertyID.PID_InverseCumulativeDist,
                       sc_prop.getObjectID(), tstep)
                icdf[sc_prop.getObjectID()] = self.properties[key].getValue()

        hdfS.writeMieDataHDF(wavelengths=wave,
                             particle_diameters=oids,
                             scatteringCrossSections=scs,
                             inverseCDF=icdf,
                             out_fname='mieData.hdf5')

        logger.debug("Mie data ready!")

    def setDefaultInputFile(self, newPath):
        '''
        Set the default input file for tracer.

        Parameters
        ----------
        newPath : string
               Path to the location of the properly formatted input json file.

        '''
        self._defaultInputfilePath = newPath

        # Load default values
        f = open(self._defaultInputfilePath, 'r')
        self._jsondata = json.load(f)
        f.close()

        # Initialise the appp
        self._initialiseDefault()
