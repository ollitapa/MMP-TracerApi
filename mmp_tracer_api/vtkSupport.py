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

import numpy as np
import os
from mupif import APIError
from pkg_resources import resource_filename
import logging
import logging.config


# create logger
logging.config.fileConfig(resource_filename(__name__, 'data/logging.conf'),
                          disable_existing_loggers=False)
logger = logging.getLogger('mmpraytracer')


def readAbsorptionData(filepath):
    '''
    Reads absorption data from vtk-file.

    Parameters
    ----------
    filepath : string
               Path to the location of the vtk-file.


    Returns
    -------
    points : list
             List of locations of the points.
    absorption : ndarray
                 Array of absorption values for each point.


    '''

    ########## READ ABSORPTION.VTP ###################
    # read values from AbsorptionData.vtk file:
    try:
        if os.path.getsize(filepath) > 500000000:
            logger.warn("file size >500MB")
            raise IOError
        absfile = open(filepath, 'rb')
        filecontents = absfile.read()
        if not filecontents:
            logger.warn("file is empty!")
            raise IOError
        lines = filecontents.splitlines()
    except IOError as e:
        logger.warn("error reading file, returning empty absorption data")
        points = ()  # tuple () or list []?
        absorption = np.array([])
        return(points, absorption)

    index = 0
    for line in lines:
        if line.strip().startswith('<Piece'):
            pieces = line.split()
            for item in pieces:
                if item.strip().startswith("NumberOfPoints="):
                    nPoints = int(item.split("\"")[1])
                    # print('nPoints = ', nPoints)
                elif item.strip().startswith("NumberOfLines"):
                    nLines = int(item.split("\"")[1])
                    # print('nLines = ', nLines)
                elif item.strip().startswith("NumberOfVerts"):
                    nVerts = int(item.split("\"")[1])
                    # print('nVerts = ', nVerts)
                elif item.strip().startswith("NumberOfStrips"):
                    nStrips = int(item.split("\"")[1])
                    # print('nStrips = ', nStrips)
                elif item.strip().startswith("NumberOfPolys"):
                    nPolys = int(item.split("\"")[1])
                    # print('nPolys = ', nPolys)
        elif line.strip().startswith('<Points'):
            # read the offset for data from the next line:
            # print('<Points> line index = ', index, lines[index])
            pieces = lines[index + 1].split()
            for item in pieces:
                if item.strip().startswith("offset="):
                    dataoffset = int(item.split("\"")[1])
                    # print('dataoffset = ', dataoffset)
                elif item.strip().startswith("NumberOfComponents"):
                    nComponents = int(item.split("\"")[1])
                    # print('nComponents = ', nComponents)
                elif item.strip().startswith("type"):
                    datatype = item.split("\"")[1]
                    # print('datatype = ', datatype)
                elif item.strip().startswith("format"):
                    dataformat = item.split("\"")[1]
                    # print('dataformat = ', dataformat)
        elif line.strip().startswith('<PointData'):
            # TODO: read Scalars="Absorption"?
            # read the offset and name for PointData from the next line:
            # print('<PointData> line index = ', index, lines[index])
            pieces = lines[index + 1].split()
            for item in pieces:
                if item.strip().startswith("offset="):
                    pointdataoffset = int(item.split("\"")[1])
                    # print('pointdataoffset = ', pointdataoffset)
                elif item.strip().startswith("NumberOfComponents"):
                    nPointComponents = int(item.split("\"")[1])
                    # print('nPointComponents = ', nPointComponents)
                elif item.strip().startswith("type"):
                    pointdatatype = item.split("\"")[1]
                    # print('pointdatatype = ', pointdatatype)
                elif item.strip().startswith("format"):
                    pointdataformat = item.split("\"")[1]
                    # print('pointdataformat = ', pointdataformat)
                elif item.strip().startswith("Name"):
                    pointdataname = item.split("\"")[1]
                    # print('pointdataname = ', pointdataname)

        elif line.strip().startswith('<AppendedData'):
            # read the appended data
            # print('<AppendedData> line index = ', index, lines[index])
            pieces = line.split()
            for item in pieces:
                if item.strip().startswith("encoding"):
                    encoding = item.split("\"")[1]
                    # print('encoding = ', encoding)
            if lines[index + 1].strip().startswith("_"):
                binarydatastartindex = index + 1
                # , lines[binarydatastartindex])
                # print('binarydatastartindex=', binarydatastartindex)
            # AppendedData is the last text line... finish for loop
            # and start reading binary data bytes
            break

        index += 1

    # offsets are bytes from the beginning of the binary data
    # read the data values by using the offsets
    absfile.seek(0)
    for x in range(0, binarydatastartindex):
        line = absfile.readline()
    # print('line=', line)  # <AppendedData encoding="raw">
    # print(vtpfile.tell())

    byte = absfile.read(1)  # read until '_'
    while byte != '_':
        byte = absfile.read(1)
    # print('byte=', byte, absfile.tell())

    binaryoffset = absfile.tell()
    # print('binaryoffset=', binaryoffset, 'dataoffset=', dataoffset)
    absfile.seek(binaryoffset + dataoffset, 0)  # dataoffset==0

    pointsize = np.fromfile(absfile, dtype=np.dtype('<u8'), count=1, sep="")
    # print('pointsize = ', pointsize, absfile.tell())
    #pointsize = struct.unpack('>Q', vtpfile.read(8))[0]
    if(pointsize / 3 / 8 != nPoints):
        raise APIError.APIError('Number of Points does not match')

    absvalueX = []
    absvalueY = []
    absvalueZ = []
    for x in range(0, nPoints):
        absvalueX.append(
            np.fromfile(absfile, dtype=np.dtype('<f8'), count=1)[0])
        absvalueY.append(
            np.fromfile(absfile, dtype=np.dtype('<f8'), count=1)[0])
        absvalueZ.append(
            np.fromfile(absfile, dtype=np.dtype('<f8'), count=1)[0])

    #print(x, absfile.tell(), absvalueX, absvalueY, absvalueZ)

    # print('bytes of file read after Points: ', absfile.tell())

    # read Absorption:
    abssize = np.fromfile(absfile, dtype=np.dtype('<u8'), count=1, sep="")
    # print('abssize=', abssize / 8)
    # if abssize/8 != nLines:
    #    raise APIError.APIError('Number of abs does not match')
    absvalues = []
    for x in range(0, abssize / 8):
        #absvalues.append(struct.unpack('<d', absfile.read(8))[0])
        absvalues.append(
            np.fromfile(absfile, dtype=np.dtype('<f8'), count=1)[0])
    # print(x, absfile.tell(), absvalues)

    # print('bytes of file read after Absorption: ', absfile.tell())

    remaining = absfile.read(
        os.fstat(absfile.fileno()).st_size - absfile.tell())
    # print('remaining=', remaining)

    pointlist = []
    for x in range(0, nPoints):
        pointlist.append(([absvalueX[x], absvalueY[x], absvalueZ[x]]))

    absorption = np.array(absvalues)

    return(pointlist, absorption)


def readLineData(filepath):
    '''
    Reads line data from vtk-file.

    Parameters
    ----------
    filepath : string
               Path to the location of the vtk-file.


    Returns
    -------
    points : list
             List of locations of the points.
    wavelengths : ndarray
                  Array of wavelengths of each line.
    offsets : ndarray
              Array of offsets, where a new line begins at points list.
    '''

    ######## read values from ray_paths.vtk file: ##########
    try:
        if os.path.getsize(filepath) > 500000000:
            print("file size >500MB, size=", os.path.getsize(filepath))
            raise IOError
        vtpfile = open(filepath, 'rb')
        filecontents = vtpfile.read()
        if not filecontents:
            print("file is empty!")
            raise IOError
        lines = filecontents.splitlines()
    except IOError as e:
        print("error reading file, returning empty ray_paths data")
        points = ()  # tuple () or list []?
        waves = np.array(None)
        offsets = np.array(None)
        return(points, waves, offsets)

    index = 0
    for line in lines:
        if line.strip().startswith('<Piece'):
            pieces = line.split()
            for item in pieces:
                if item.strip().startswith("NumberOfPoints="):
                    nPoints = int(item.split("\"")[1])
                    print('nPoints = ', nPoints)
                elif item.strip().startswith("NumberOfLines"):
                    nLines = int(item.split("\"")[1])
                    print('nLines = ', nLines)
                elif item.strip().startswith("NumberOfVerts"):
                    nVerts = int(item.split("\"")[1])
                    print('nVerts = ', nVerts)
                elif item.strip().startswith("NumberOfStrips"):
                    nStrips = int(item.split("\"")[1])
                    print('nStrips = ', nStrips)
                elif item.strip().startswith("NumberOfPolys"):
                    nPolys = int(item.split("\"")[1])
                    print('nPolys = ', nPolys)
        elif line.strip().startswith('<Points'):
            # read the offset for data from the next line:
            print('<Points> line index = ', index, lines[index])
            pieces = lines[index + 1].split()
            for item in pieces:
                if item.strip().startswith("offset="):
                    dataoffset = int(item.split("\"")[1])
                    print('dataoffset = ', dataoffset)
                elif item.strip().startswith("NumberOfComponents"):
                    nComponents = int(item.split("\"")[1])
                    print('nComponents = ', nComponents)
                elif item.strip().startswith("type"):
                    datatype = item.split("\"")[1]
                    print('datatype = ', datatype)
                elif item.strip().startswith("format"):
                    dataformat = item.split("\"")[1]
                    print('dataformat = ', dataformat)

        elif line.strip().startswith('<CellData'):
            # TODO: read Scalars="Wavelength"?
            # read the offset and name for CellData from the next line:
            print('<CellData> line index = ', index, lines[index])
            pieces = lines[index + 1].split()
            for item in pieces:
                if item.strip().startswith("offset="):
                    celldataoffset = int(item.split("\"")[1])
                    print('celldataoffset = ', celldataoffset)
                elif item.strip().startswith("NumberOfComponents"):
                    nCellComponents = int(item.split("\"")[1])
                    print('nCellComponents = ', nCellComponents)
                elif item.strip().startswith("type"):
                    celldatatype = item.split("\"")[1]
                    print('celldatatype = ', celldatatype)
                elif item.strip().startswith("format"):
                    celldataformat = item.split("\"")[1]
                    print('celldataformat = ', celldataformat)
                elif item.strip().startswith("Name"):
                    celldataname = item.split("\"")[1]
                    print('celldataname = ', celldataname)

        elif line.strip().startswith('<Lines'):
            # TODO: how many DataArrays? Always 2?
            # read the offsets and names from the next lines:
            print('<Lines> line index = ', index, lines[index])
            pieces = lines[index + 1].split()
            for item in pieces:
                if item.strip().startswith("offset="):
                    lines1offset = int(item.split("\"")[1])
                    print('lines1offset = ', lines1offset)
                elif item.strip().startswith("type"):
                    lines1type = item.split("\"")[1]
                    print('lines1type = ', lines1type)
                elif item.strip().startswith("format"):
                    lines1format = item.split("\"")[1]
                    print('lines1format = ', lines1format)
                elif item.strip().startswith("Name"):
                    lines1name = item.split("\"")[1]
                    print('lines1name = ', lines1name)

            pieces = lines[index + 3].split()
            for item in pieces:
                if item.strip().startswith("offset="):
                    lines2offset = int(item.split("\"")[1])
                    print('lines2offset = ', lines2offset)
                elif item.strip().startswith("type"):
                    lines2type = item.split("\"")[1]
                    print('lines2type = ', lines2type)
                elif item.strip().startswith("format"):
                    lines2format = item.split("\"")[1]
                    print('lines2format = ', lines2format)
                elif item.strip().startswith("Name"):
                    lines2name = item.split("\"")[1]
                    print('lines2name = ', lines2name)

        elif line.strip().startswith('<AppendedData'):
            # read the appended data
            print('<AppendedData> line index = ', index, lines[index])
            pieces = line.split()
            for item in pieces:
                if item.strip().startswith("encoding"):
                    encoding = item.split("\"")[1]
                    print('encoding = ', encoding)
            if lines[index + 1].strip().startswith("_"):
                binarydatastartindex = index + 1
                # , lines[binarydatastartindex])
                print('binarydatastartindex=', binarydatastartindex)
            # AppendedData is the last text line... finish for loop
            # and start reading binary data bytes
            break

        index += 1

    # offsets are bytes from the beginning of the binary data
    # read the data values by using the offsets

    vtpfile.seek(0)
    for x in range(0, binarydatastartindex):
        line = vtpfile.readline()
    # print('line=', line) #<AppendedData encoding="raw">
    # print(vtpfile.tell())

    byte = vtpfile.read(1)  # read until '_'
    while byte != '_':
        byte = vtpfile.read(1)
    print('byte=', byte, vtpfile.tell())

    binaryoffset = vtpfile.tell()
    print('binaryoffset=', binaryoffset, 'dataoffset=', dataoffset)
    vtpfile.seek(binaryoffset + dataoffset, 0)  # dataoffset==0

    pointsize = np.fromfile(vtpfile, dtype=np.dtype('<u8'), count=1, sep="")
    print('pointsize = ', pointsize, vtpfile.tell())
    #pointsize = struct.unpack('>Q', vtpfile.read(8))[0]
    if(pointsize / 3 / 8 != nPoints):
        raise APIError.APIError('Number of Points does not match')

    valueX = []
    valueY = []
    valueZ = []
    for x in range(0, nPoints):
        valueX.append(np.fromfile(vtpfile, dtype=np.dtype('<f8'), count=1)[0])
        valueY.append(np.fromfile(vtpfile, dtype=np.dtype('<f8'), count=1)[0])
        valueZ.append(np.fromfile(vtpfile, dtype=np.dtype('<f8'), count=1)[0])

    #print(x, vtpfile.tell(), valueX, valueY, valueZ)

    print('bytes of file read after Points: ', vtpfile.tell())

    # read Wavelength:
    wvsize = np.fromfile(vtpfile, dtype=np.dtype('<u8'), count=1, sep="")
    print('wvsize=', wvsize / 8)
    if wvsize / 8 != nLines:
        raise APIError.APIError('Number of wv does not match')
    wv = []
    for x in range(0, nLines):
        #wv.append(struct.unpack('<d', vtpfile.read(8))[0])
        wv.append(np.fromfile(vtpfile, dtype=np.dtype('<f8'), count=1)[0])
    #print(x, vtpfile.tell(), wv)

    print('bytes of file read after Wavelength: ', vtpfile.tell())

    # read Connectivity:
    connsize = np.fromfile(vtpfile, dtype=np.dtype('<u8'), count=1, sep="")
    print('connsize=', connsize / 8)
    if connsize / 8 != nPoints:
        raise APIError.APIError('Number of connectivity does not match')
    connectivity = []
    for x in range(0, nPoints):
        #connectivity.append(struct.unpack('<Q', vtpfile.read(8))[0])
        connectivity.append(
            np.fromfile(vtpfile, dtype=np.dtype('<u8'), count=1, sep="")[0])
    #print(x, connectivity)

    print('bytes of file read after Connectivity: ', vtpfile.tell())

    # read offsets:
    offsize = np.fromfile(vtpfile, dtype=np.dtype('<u8'), count=1, sep="")
    print('offsize=', offsize / 8)
    if offsize / 8 != nLines:
        raise APIError.APIError('Number of offsets does not match')

    offsets = []
    for x in range(0, nLines):
        #offsets.append(struct.unpack('<Q', vtpfile.read(8))[0])
        offsets.append(
            np.fromfile(vtpfile, dtype=np.dtype('<u8'), count=1, sep="")[0])
    #print(x, offsets)

    print('bytes of file read after offsets: ', vtpfile.tell())

    remaining = vtpfile.read(
        os.fstat(vtpfile.fileno()).st_size - vtpfile.tell())
    print('remaining=', remaining)

    # TODO: Write!
    points = []
    for x in range(0, nPoints):
        points.append(np.array([valueX[x], valueY[x], valueZ[x]]))

    #points = [np.array([0, 0, 0]), np.array([0, 0, 1]), np.array([0, 1, 2])]
    waves = np.array(wv)
    #waves = np.array([450.0])
    offsets = np.array(offsets)
    #offsets = np.array([0])

    return(points, waves, offsets)
