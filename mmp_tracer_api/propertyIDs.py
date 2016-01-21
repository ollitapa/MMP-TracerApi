#
# Copyright 2016 VTT Technical Research Center of Finland
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

"""
Module defining PropertyID as enumeration, e.g. concentration, velocity.
class Enum allows accessing members by .name and .value
"""

from enum import IntEnum


class PropertyID(IntEnum):
    """
    Enumeration class  defining Property IDs.
    These are used to uniquely determine
    the canonical keywords identifiing individual properties.
    """
    PID_RefractiveIndex = 1
    PID_NumberOfRays = 2
    PID_LEDSpectrum = 3
    PID_ChipSpectrum = 4
    PID_LEDColor_x = 5
    PID_LEDColor_y = 6
    PID_LEDCCT = 7
    PID_LEDRadiantPower = 8
    PID_ParticleNumberDensity = 9
    PID_ParticleRefractiveIndex = 10
    PID_EmissionSpectrum = 11
    PID_ExcitationSpectrum = 12
    PID_AsorptionSpectrum = 13

    PID_ScatteringCrossSections = 14
    PID_InverseCumulativeDist = 15


if __name__ == '__main__':
    print(PropertyID.PID_InverseCumulativeDist)
