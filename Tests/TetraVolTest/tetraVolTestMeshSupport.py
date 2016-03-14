from mmp_tracer_api import mmpMeshSupport as ms
import meshGenerator as generator
from mupif import CellGeometryType, Cell
import types

mesh = generator.generateCubeMesh()

print(mesh)

totalVolume = 0

for cell in mesh.cells():
    print(cell)

    # Fake cell type to test Error generation
    def getGeometryType(self):
        return(CellGeometryType.CGT_QUAD)

    #cell.getGeometryType = types.MethodType(getGeometryType, cell)

    vol = ms.computeCellVolumeOrArea(cell)
    totalVolume += vol
    print(vol)

print("Total volume: %.f" % totalVolume)
