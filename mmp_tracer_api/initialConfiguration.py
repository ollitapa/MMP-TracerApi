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

from mupif import FunctionID, PropertyID, FieldID, ValueType
from mupif import Property, APIError
import objID
import numpy as np


def checkRequiredFields(fields,  fID=FieldID):
    """
    Checks that all relevant fields for the simulation
    are present.
    """
    # TODO: Check!
    found = True

    if fID.FID_Thermal_absorption_volume not in fields.index:
        print("Thermal_absorption_volume not found!")
        #found = False

    if not found:
        print("not all relevant fields found!")
        raise APIError.APIError("not all relevant fields found!")


def checkRequiredParameters(props, pID=PropertyID):
    """
    Checks that all relevant parameters for the simulation
    are present.
    """
    # TODO: Check!
    """
        PropertyID.PID_RefractiveIndex = 22
        PropertyID.PID_NumberOfRays = 23
        PropertyID.PID_LEDSpectrum = 24
        PropertyID.PID_ParticleNumberDensity = 25
        PropertyID.PID_ParticleRefractiveIndex = 26
    """
    #print("Property keys:")
    # for key in props.index:
    #        print(key)

    found = True

    if pID.PID_RefractiveIndex not in props.index:
        print("RefractiveIndex not found!")
        found = False
    if pID.PID_NumberOfRays not in props.index:
        print("NumberOfRays not found!")
        found = False
    if pID.PID_LEDSpectrum not in props.index:
        print("LEDSpectrum not found!")
        found = False
    if pID.PID_ParticleNumberDensity not in props.index:
        print("ParticleNumberDensity not found!")
        #found = False
    #if pID.PID_ParticleRefractiveIndex not in props.index:
    #    print("ParticleRefractiveIndex not found!")
    #    #found = False
    if pID.PID_InverseCumulativeDist not in props.index:
        print("InverseCumulativeDist not found!")
        #found = False
    if pID.PID_ScatteringCrossSections not in props.index:
        print("ScatteringCrossSections not found!")
        #found = False

    if found is False:
        print("not all relevant parameters found!")
        raise APIError.APIError("not all relevant properties found!")


def checkRequiredFunctions(funcs, fID=FunctionID):
    pass


def initialFunc(funcs, json, fID=FunctionID):

    pass


def initialField(fields, json, fID=FieldID):

    pass


def initialProps(props, jsondata, pID=PropertyID):
    # Number of rays
    nr = Property.Property(value=jsondata['sources'][0]['rays'],
                           propID=pID.PID_NumberOfRays,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_CHIP_ACTIVE_AREA)

    key = (pID.PID_NumberOfRays, objID.OBJ_CHIP_ACTIVE_AREA, 0)
    props.set_value(key, nr)

    # Refractive index of silicone cone
    v = jsondata['materials'][3]['refractiveIndex']
    nr = Property.Property(value=v,
                           propID=pID.PID_RefractiveIndex,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_CONE)

    key = (pID.PID_RefractiveIndex, objID.OBJ_CONE, 0)
    props.set_value(key, nr)

    # LED spectrum
    nr = Property.Property(value={"wavelengths": np.array([450]),
                                  "intensities": np.array([0])},
                           propID=pID.PID_LEDSpectrum,
                           valueType="dict",
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_LED)

    key = (pID.PID_LEDSpectrum, objID.OBJ_LED, 0)
    props.set_value(key, nr)

    # Chip spectrum
    v1 = jsondata['sources'][0]['wavelengths']
    v2 = jsondata['sources'][0]['intensities']
    nr = Property.Property(value={"wavelengths": np.array(v1),
                                  "intensities": np.array(v2)},
                           propID=pID.PID_ChipSpectrum,
                           valueType="dict",
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_CHIP_ACTIVE_AREA)

    key = (pID.PID_ChipSpectrum, objID.OBJ_CHIP_ACTIVE_AREA, 0)
    props.set_value(key, nr)

    # Color X
    nr = Property.Property(value=0,
                           propID=pID.PID_LEDColor_x,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_LED)

    key = (pID.PID_LEDColor_x, objID.OBJ_LED, 0)
    props.set_value(key, nr)

    # Color Y
    nr = Property.Property(value=0,
                           propID=pID.PID_LEDColor_y,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_LED)

    key = (pID.PID_LEDColor_y, objID.OBJ_LED, 0)
    props.set_value(key, nr)

    # CCT
    nr = Property.Property(value=0,
                           propID=pID.PID_LEDCCT,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_LED)

    key = (pID.PID_LEDCCT, objID.OBJ_LED, 0)
    props.set_value(key, nr)

    # RadiantPower
    nr = Property.Property(value=0,
                           propID=pID.PID_LEDRadiantPower,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_LED)

    key = (pID.PID_LEDRadiantPower, objID.OBJ_LED, 0)
    props.set_value(key, nr)

    # Number of fluorescent particles:
    nr = Property.Property(value=jsondata['materials'][3]['numberOfFluorescentParticles'], valueType=ValueType.Scalar, propID=pID.PID_Demo_Value, time=0.0, units=None, objectID=objID.OBJ_CONE)
    key = (pID.PID_Demo_Value, objID.OBJ_CONE, 0)
    props.set_value(key, nr)

    # print(type(props[key].value))
    # print(props[key].value)
