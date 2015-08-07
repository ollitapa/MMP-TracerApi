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
from mupif import Field, Property
import logging
import logging.config


# create logger
logger = logging.getLogger('mmpraytracer')


def interpolateFields(fields, time, fieldID, method='linear'):
    """
    Function to interpolate fields in between solved timesteps.


    Parameters
    ----------
    fields : pandas.Series of Field.Field
             Series of fields for consecutive timesteps.

    fieldID : FieldID
              Type of field to interpolate

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

    # Find closest timesteps
    idx_tstep = fields[fieldID].index
    value_to_find = time
    Min = idx_tstep <= value_to_find
    Max = idx_tstep >= value_to_find

    f_min = fields[(fieldID, idx_tstep[Min].max())]
    f_max = fields[(fieldID, idx_tstep[Max].min())]

    # Interpolate field values.
    if method == 'linear':
        newValues = f_min.values + (f_max.values - f_min.values) / 2.0
    else:
        logger.warning(
            'Interpolation method (%s) not supported! Using linear.' % method)
        newValues = f_min.values + (f_max.values - f_min.values) / 2.0

    # Create new field.
    interpolatedField = Field.Field(f_min.mesh,
                                    f_min.fieldID,
                                    f_min.valueType,
                                    units=f_min.units,
                                    values=newValues,
                                    time=time,
                                    fieldType=f_min.fieldType)
    # Return
    return(interpolatedField)


def interpolateProperty(properties, time, propertyID, objectID,
                        method='linear'):
    """
    Function to interpolate fields in between solved timesteps.


    Parameters
    ----------
    properties : pandas.Series of Property.Property
                 Series of properties for consecutive timesteps.
    time : float
           Time to interpolate data

    propetyID : PropertyID
                Type of the property to interpolate

    objectID : float
               Object id the porperty is attached to.

    method : string, optional
             Method to be used in the interpolation. Only linear is currently
             supported


    Returns
    -------
    interPorp : Property.Property
            Interpolated property


    """
    if not isinstance(properties, pd.Series):
        raise TypeError("Properties should be in pandas Series -object")

    # Find closest timesteps
    idx_tstep = properties.loc[propertyID, objectID, :].index
    value_to_find = time
    Min = idx_tstep <= value_to_find
    Max = idx_tstep >= value_to_find

    p_min = properties[(propertyID, objectID, idx_tstep[Min].max())]
    p_max = properties[(propertyID, objectID, idx_tstep[Max].min())]

    # Interpolate property value.
    if method == 'linear':
        newValue = p_min.value + (p_max.value - p_min.value) / 2.0
    else:
        logger.warning(
            'Interpolation method (%s) not supported! Using linear.' % method)
        newValue = p_min.value + (p_max.value - p_min.value) / 2.0

    # Create new property.
    newProp = Property.Property(value=newValue,
                                propID=propertyID,
                                valueType=p_min.valueType,
                                time=time,
                                units=p_min.units,
                                objectID=objectID)

    return(newProp)
