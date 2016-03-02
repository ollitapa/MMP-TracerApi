from mmp_tracer_api import mmpMeshSupport as ms
import meshGenerator as generator

mesh = generator.load2Dmesh()

print(mesh)

totalVolume = 0

for cell in mesh.cells():
    print(cell)

    # Calculate volume
    vol = ms.computeCellVolumeOrArea(cell)
    totalVolume += vol
    print(vol)

totalVolume *= 10**6

print("Total volume: %f mm^2" % (totalVolume))
