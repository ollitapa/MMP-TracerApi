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

from meshpy.tet import MeshInfo, build
from mupif import Mesh, Vertex, Cell
import numpy as np
import pickle


def generateCubeMesh():
    mesh_info = MeshInfo()
    mesh_info.set_points([
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
        (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1),
    ])
    mesh_info.set_facets([
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [0, 4, 5, 1],
        [1, 5, 6, 2],
        [2, 6, 7, 3],
        [3, 7, 4, 0],
    ])
    mesh = build(mesh_info)

    cellList = []
    vertexList = []
    mupifMesh = Mesh.UnstructuredMesh()

    print("Mesh Points:")
    for i, p in enumerate(mesh.points):
        print(i, p)
        vertexList.extend([Vertex.Vertex(i, i, p)])

    print("Point numbers in tetrahedra:")
    for i, t in enumerate(mesh.elements):
        print(i, t)
        cellList.extend([Cell.Tetrahedron_3d_lin(mupifMesh, i, i, t)])

    mupifMesh.setup(vertexList, cellList)

    return(mupifMesh)


def load2Dmesh():
    f = pickle.load(open('reflector.xxx', 'r'))
    return(f.getMesh())

if __name__ == '__main__':
    load2Dmesh()
