#
# Copyright 2015 Olli Tapaninen, VTT Technical Research Center of Finland
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
import sys
sys.path.append(os.path.abspath('../mmp_tracer_api/'))
import meshGenerator as mg
import numpy as np
from mmpMeshSupport import convertPointDataToMesh
from mupif import BBox, Field, FieldID, ValueType
from datetime import datetime

import logging
logger = logging.getLogger('mmpraytracer')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)

logger.addHandler(ch)

if __name__ == '__main__':

    # Just test scripting here
    #############################################

    mesh = mg.generateConeMesh(plot=False)
    # mesh = mg.generateCubeMesh()

    f = Field.Field(mesh, FieldID.FID_Temperature,
                    ValueType.Scalar, units='K', time=0,
                    fieldType=Field.FieldType.FT_cellBased)

    print('Mesh has %d elements' % mesh.getNumberOfCells())

    # print(mesh.cellList[0].getVertices())
    # print(len(mesh.cellList))
    # import pyvtk
    # vtk = pyvtk.VtkData(mesh.getVTKRepresentation())
    # vtk.tofile('mesh')
    x0 = 0
    y0 = 0
    z0 = 0
    h = 1
    r_bottom = 1.3
    r_top = 1.5
    n = 1E6

    xs = np.random.uniform(low=x0 - r_top, high=x0 + r_top, size=n)
    ys = np.random.uniform(low=y0 - r_top, high=y0 + r_top, size=n)
    zs = np.random.uniform(low=z0, high=z0 + h, size=n)

    values = np.random.uniform(size=n)
    print('zip')
    points = zip(xs, ys, zs)
    print('zip done')
    startTime = datetime.now()
    f2 = convertPointDataToMesh(points, values, f, inplace=True)
    print('Time it took to find %.0e points:' % n)
    print(str(datetime.now() - startTime).split('.', 2)[0])
    # print(f2.values)
    # print(f2.values)

    #############################################
