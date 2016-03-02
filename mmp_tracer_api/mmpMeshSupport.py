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

from mupif import BBox, Field, FieldID, ValueType, CellGeometryType, APIError
import subprocess
import os
import numpy as np
import logging
import logging.config
logger = logging.getLogger('mmpraytracer')
import time


def getMeshBounds(mesh):
    '''
    Returns the bounding box of the mesh.

    Parameters
    ----------
    mesh : Mesh
        Mesh object to check.

    Returns
    -------
    bounds : list
        List of tuples. [(xmin, xmax), (ymin, ymax), (zmin, zmax)]
    '''

    verts = np.array(mesh.vertexList)

    def points(x):
        return x.getCoordinates()
    getP = np.vectorize(points)

    verts = getP(verts)

    xmax = np.max(verts[0])
    ymax = np.max(verts[1])
    zmax = np.max(verts[2])
    xmin = np.min(verts[0])
    ymin = np.min(verts[1])
    zmin = np.min(verts[2])

    return([(xmin, xmax), (ymin, ymax), (zmin, zmax)])


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
    bounds = getMeshBounds(mesh)
    eps = np.min(np.diff(bounds)) * 0.1
    ans = []
    cells = mesh.giveCellLocalizer().giveItemsInBBox(
        BBox.BBox([c - eps for c in point], [c + eps for c in point]))
    # print('Found %s cells' % len(cells))
    for icell in cells:
        if icell.containsPoint(point):
            ans.append(icell)
    return ans


def computeCellVolumeOrArea(cell):

    vol = 0

    if cell.getGeometryType() == CellGeometryType.CGT_TETRA:

        # Get vertices and create points as np.array
        verts = cell.getVertices()

        p0 = np.array(verts[0].getCoordinates())
        p1 = np.array(verts[1].getCoordinates())
        p2 = np.array(verts[2].getCoordinates())
        p3 = np.array(verts[3].getCoordinates())

        # Creat three polyhedron edge vectors a, b, and c
        a = p1 - p0
        b = p2 - p0
        c = p3 - p0

        # Calculate volume
        vol = 1 / 6.0 * np.abs(np.dot(a, np.cross(b, c)))

    elif cell.getGeometryType() == CellGeometryType.CGT_TRIANGLE_1:
        # Get vertices and create points as np.array
        verts = cell.getVertices()

        p0 = np.array(verts[0].getCoordinates())
        p1 = np.array(verts[1].getCoordinates())
        p2 = np.array(verts[2].getCoordinates())

        # Creat edge vectors a, b
        a = p1 - p0
        b = p2 - p0

        # Calculate volume
        vol = np.linalg.norm(np.cross(a, b)) / 2.0

    else:
        raise APIError.APIError("Volume/Area calculation for %s\
                                 not supported" % str(cell))
    return(vol)


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
        Field where the points have been inserted. Point values are divided
        by Cell volume/area

    '''
    logger.debug("Converting point data (n=%d) to mesh (cells=%d)..." % (
        len(points), field.getMesh().getNumberOfCells()))

    if not inplace:
        f = Field.Field(field.getMesh(),
                        field.getFieldID(),
                        field.getValueType(),
                        field.getUnits(),
                        field.getTime(),
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
        for cell in elems:
            j = cell.number
            divider = computeCellVolumeOrArea(cell)

        # Sum field values
        if len(elems) > 0:
            vDivVol = v / divider
            f.setValue(j, vDivVol + f.giveValue(j))
        else:
            pNfound += 1

    logger.debug("Points not found to be in mesh: %d" % pNfound)
    return(f)


def convertPointDataToMeshFAST(pointdataVTKfile, field, inplace=True):
    '''
    Converts point-data to mesh based Cell-data. This uses a c-program
    to perform fast search. The program must be installed separately.
    See:

    An element of the mesh
    containing each point is searched. The value of the point is added to
    the value of that cell in the field. No interpolation of occurs.

    Parameters
    ----------
    pointdataVTKfile : string
            Filename to vtk-file containing point data
    field : Field.Field
            An empty field that should be filled with values.
            Mupif Field in which the points should be inserted.
    inplace : bool
              If true the original field object is changed. Otherwise
              a copy is returned.

    Returns
    -------
    Field.Field
        Field where the points have been inserted. Point values are divided
        by Cell volume/area

    '''
    logger.info("Converting point data to mesh (cells=%d)..." % (
        field.getMesh().getNumberOfCells()))

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

    v = field.field2VTKData()
    f_mesh = 'mesh_data_tmp.vtk'
    v.tofile(f_mesh)

    logger.info("Conversion process starting...")
    status = subprocess.check_call(
        ["abs2grid", f_mesh, pointdataVTKfile, '_abs'])
    print(status)
    if status == 0:
        logger.info("Conversion process done!")
        a = np.loadtxt("AbsorptionGrid__abs.txt")

        for i, v in zip(range(len(a)), a):
            f.setValue(i, v)
        logger.info("Absorbed power: %f" % np.sum(a))

    else:
        logger.info("Conversion failed")

    return(f)


def FASTisAvailable():
    try:
        subprocess.call(["abs2grid"])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
        else:
            return False

    return True
