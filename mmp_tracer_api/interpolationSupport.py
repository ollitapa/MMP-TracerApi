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

import pandas as pd


def interpolateFields(fields, time, method='linear'):
    """
    Function to interpolate fields in between solved timesteps.


    Parameters
    ----------
    fields : pandas.Series of Field.Field
             Series of fields for consecutive timesteps.
    time : float
           Time to interpolate data
    method : string, optional
             Method to be used in the interpolation. Only linear is currently
             supported


    Returns
    -------
    field : Field.Field
            Interpolated field


    """
    if not isinstance(fields, pd.Series):
        raise TypeError("Fields should be in pandas Series -object")

    # TODO: write!

    return(fields.loc[0])


def interpolateProperty(properties, time, method='linear'):
    """
    Function to interpolate fields in between solved timesteps.


    Parameters
    ----------
    properties : pandas.Series of Property.Property
                 Series of properties for consecutive timesteps.
    time : float
           Time to interpolate data
    method : string, optional
             Method to be used in the interpolation. Only linear is currently
             supported


    Returns
    -------
    interPorp : Property.Property
            Interpolated property


    """
    if not isinstance(properties, pd.Series):
        raise TypeError("Fields should be in pandas Series -object")

    # TODO: write!

    return(properties.loc[0])
