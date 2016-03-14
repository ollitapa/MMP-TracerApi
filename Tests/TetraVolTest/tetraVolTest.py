from mmp_tracer_api import mmpMeshSupport as ms
import meshGenerator as generator
import numpy as np

mesh = generator.generateCubeMesh()

print(mesh)

totalVolume = 0

for cell in mesh.cells():
    print(cell)
    verts = cell.getVertices()

    p0 = np.array(verts[0].getCoordinates())
    p1 = np.array(verts[1].getCoordinates())
    p2 = np.array(verts[2].getCoordinates())
    p3 = np.array(verts[3].getCoordinates())

    a = p1 - p0
    b = p2 - p0
    c = p3 - p0

    vol = 1 / 6.0 * np.abs(np.dot(a, np.cross(b, c)))
    totalVolume += vol
    print(vol)

print("Total volume: %.f" % totalVolume)
