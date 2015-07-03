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

from mupif import BBox, Field, FieldID, ValueType
import logging
import logging.config
logger = logging.getLogger('mmpraytracer')


def giveElementsContainingPoint(mesh, point):
    '''
    Find elements of the mesh containing given point

    Parameters
    ----------
    point : tuple
            Point for searching
    mesh : Mesh.Mesh
           Mesh where the point should be searched.

    Returns
    -------
    list of Cell.Cell
            List of found cells. Usually if many cells are found
            the point lies on an edge of the cells.

    '''
    eps = 0.0001
    ans = []
    cells = mesh.giveCellLocalizer().giveItemsInBBox(
        BBox.BBox([c - eps for c in point], [c + eps for c in point]))
    #print('Found %s cells' % len(cells))
    for icell in cells:
        if icell.containsPoint(point):
            ans.append(icell)
    return ans


def convertPointDataToMesh(points, values, field, inplace=True):
    '''
    Converts point-data to mesh based Cell-data. An element of the mesh
    containing each point is searched. The value of the point is added to
    the value of that cell in the field. No interpolation of occurs.

    Parameters
    ----------
    points : list
             List of points to convert.
    values : array_like
             Values corresponding to each point
    field : Field.Field
            An empty field that should be filled with values.
            Mupif Field in which the points should be inserted.
    inplace : bool
              If true the original field object is changed. Otherwise
              a copy is returned.

    Returns
    -------
    Field.Field
        Field where the points have been inserted.

    '''
    logger.debug("Converting point data (n=%d) to mesh (cells=%d)..." % (
        len(points), field.getMesh().getNumberOfCells()))

    if not inplace:
        f = Field.Field(field.getMesh(),
                        field.getFieldID(),
                        field.getValueType(),
                        field.getUnits(),
                        field.time,
                        field.values,
                        field.fieldType)
    else:
        f = field

    # Get mesh
    mesh = f.getMesh()

    # Points not found
    pNfound = 0
    # Iterate through points
    for p, v in zip(points, values):

        # Get elements containing points.
        elems = giveElementsContainingPoint(mesh, p)

        # now the elems list contains all elements containing the given point
        # print("%s %s %s" % ("Elements containing point", p, "are:"))
        j = 0
        for i in elems:
            j = i.number

        # Sum field values
        if len(elems) > 0:
            f.setValue(j, v + f.values[j])
        else:
            pNfound += 1

    logger.debug("Points not found to be in mesh: %d" % pNfound)
    return(f)
