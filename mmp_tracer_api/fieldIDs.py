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
Module defining FieldID as enumeration, e.g. concentration, velocity.
class Enum allows accessing members by .name and .value
"""

from enum import IntEnum


class FieldID(IntEnum):
    """
    Enumeration class  defining Field IDs.
    These are used to uniquely determine
    the canonical keywords identifiing individual properties.
    """
    FID_HeatSourceVol = 1
    FID_HeatSourceSurf = 2
    FID_Temperature = 3
