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
from meshpy.geometry import generate_extrusion
from matplotlib import pylab as plt
from mpl_toolkits.mplot3d import Axes3D


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


def generateConeMesh(plot=True):
    x0 = 0
    y0 = 0
    z0 = 1
    h = 1
    r_bottom = 1.3
    r_top = 1.5
    r_scale = r_top / r_bottom

    rz = [(0, z0),
          (1, z0),
          (r_scale, z0 + h),
          (0, z0 + h)]

    base = []

    # Create circle
    for theta in np.linspace(0, 2 * np.pi, 40):
        x = r_bottom * np.sin(theta)
        y = r_bottom * np.cos(theta)
        base.extend([(x, y)])

    (points, facets,
     facet_holestarts, markers) = generate_extrusion(rz_points=rz,
                                                     base_shape=base)

    if plot:
        p_array = np.array(points)
        xs = p_array[:, 0] + x0
        ys = p_array[:, 1] + y0
        zs = p_array[:, 2]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, zs)

        for f in facets:
            plt.plot(xs[list(f[0])], ys[list(f[0])], zs[list(f[0])])

        if True:
            axLim = ax.get_w_lims()
            MAX = np.max(axLim)
            for direction in (-1, 1):
                for point in np.diag(direction * MAX * np.array([1, 1, 1])):
                    ax.plot(
                        [point[0]], [point[1]], [np.abs(point[2])], 'w')
        x = [0, 0]
        y = [0, 0]
        z = [1, 1 + 0.2]
        plt.plot(x, y, z)
        plt.show()

    mesh_info = MeshInfo()
    mesh_info.set_points(points)
    mesh_info.set_facets_ex(facets)
    mesh = build(mesh_info)
    # print(mesh.elements)

    cellList = []
    vertexList = []
    mupifMesh = Mesh.UnstructuredMesh()

    for i, p in enumerate(mesh.points):
        p = (p[0] + x0, p[1] + y0, p[2])
        vertexList.extend([Vertex.Vertex(i, i, p)])

    for i, t in enumerate(mesh.elements):
        cellList.extend([Cell.Tetrahedron_3d_lin(mupifMesh, i, i, t)])

    mupifMesh.setup(vertexList, cellList)

    return(mupifMesh)
