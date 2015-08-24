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

import numpy as np
from meshpy.geometry import generate_extrusion
from matplotlib import pylab as plt
from mpl_toolkits.mplot3d import Axes3D
from meshpy.tet import MeshInfo, build

rz = [(0, 0), (1, 0), (1.5, 0.5),  (2, 1), (0, 1)]

base = []

for theta in np.linspace(0, 2 * np.pi, 40):

    x = np.sin(theta)
    y = np.cos(theta)
    base.extend([(x, y)])


(points, facets,
 facet_holestarts, markers) = generate_extrusion(rz_points=rz, base_shape=base)


p_array = np.array(points)
xs = p_array[:, 0]
ys = p_array[:, 1]
zs = p_array[:, 2]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xs, ys, zs)


for f in facets:
    plt.plot(xs[list(f[0])], ys[list(f[0])], zs[list(f[0])])
plt.show()
for i_facet, poly_list in enumerate(facets):
    print(poly_list)

mesh_info = MeshInfo()
mesh_info.set_points(points)
mesh_info.set_facets_ex(facets, facet_holestarts, markers)
mesh = build(mesh_info)
print(mesh.elements)

mesh.write_vtk('test.vtk')
