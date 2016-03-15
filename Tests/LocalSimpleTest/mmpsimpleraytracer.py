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

#import Pyro4
from mupif import APIError
from mupif import Property, Field, Mesh
from mupif import PropertyID, FieldID, FunctionID
from mupif import TimeStep
from mupif import ValueType
from mupif.Application import Application
import numpy as np
import pandas as pd


'''
sys.excepthook = Pyro4.util.excepthook
Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle', 'serpent', 'json']
Pyro4.config.SERIALIZER = 'pickle'
'''


class MMPSimpleRaytracer(Application):

    """
    Mupif interface to mmpraytracer (phosphor raytracing)

    """

    _curTStep = -1

    def __init__(self, file, workdir='.'):
        super(MMPSimpleRaytracer, self).__init__(file, workdir)  # call base
        os.chdir(workdir)
        
       
        # Fields
        # Key should be in form of tuple (fieldID, tstep)
        idxf = pd.MultiIndex.from_tuples([("fieldID", 1.0)],
                                         names=['fieldID', 'tstep'])
        self.fields = pd.Series(index=idxf, dtype=Field.Field)

        # Initialise processes
        if os.name == "nt":
            self.tracerProcess = Popen(
                ["dir"], stdout=PIPE, stderr=PIPE, shell=True)
            self.postThread = Popen(
                ["dir"], stdout=PIPE, stderr=PIPE, shell=True)
        else:
            self.tracerProcess = Popen(["ls"], stdout=PIPE, stderr=PIPE)
            self.postThread = Popen(["ls"], stdout=PIPE, stderr=PIPE)

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

        # Set the new field to container
        print(field)
        key = (field.getFieldID(), field.time)
        self.fields.set_value(key, field)


    def getMesh(self, tstep):
        """
        Returns the computational mesh for given solution step.

        :param TimeStep tstep: Solution step
        :return: Returns the representation of mesh
        :rtype: Mesh
        """
        return(self.fields.xs(tstep, level='time')[0])

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

        # Set current tstep
        self._curTStep = tstep

      
        # This thread will callback when tracer has ended.
        self.postThread = threading.Thread(target=self._runCallback,
                                           args=(self.tracerProcess,
                                                 self._tracerProcessEnded))
        # Post processing thread will wait for the tracer to finnish
        self.postThread.start()

        # Wait for process if applicaple
        if not runInBackground:
            self.wait()

    def wait(self):
        """
        Wait until solve is completed when executed in background.
        """
        print("Waiting...")
        self.tracerProcess.wait()
        print("Post processing...")
        self.postThread.join()
        print("Post processing done!")

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
        return("MMP-Simple-Raytracer@" + socket.gethostbyaddr(socket.gethostname())[0]
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

    def _tracerProcessEnded(self, lines):
        # Check if process ended correctly
        print("Tracing successful!")
        
        # Get field
        key = (FieldID.FID_Thermal_absorption_volume, self._curTStep)
        f = self.fields[key]

        #Generate some random values:
        #print("f.values length = ", len(f.values))
        #print("f.valueType=", f.valueType)
        #print(f.values)
        random_values = np.random.random(len(f.values))
        f.values[:, 0] = random_values[:]
        print("random values set to field")
        #print(f.values)
        #print("f.values length = ", len(f.values))

        
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
        pHandle.wait()
        callback(lines)
        return

