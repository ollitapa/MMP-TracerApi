from mmpsimpleraytracer import MMPSimpleRaytracer
from comsol_api import MMPComsolDummy  # REPLACE!
from mupif import Property, PropertyID, FieldID, ValueType

if __name__ == '__main__':

    tracerApp = MMPSimpleRaytracer('localhost')
    comsolApp = MMPComsolDummy('localhost')  # REPLACE

    print(tracerApp)
    print(comsolApp)

    # Connect fields
    print('Connecting Fields...')
    fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
    fHeat = comsolApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

    tracerApp.setField(fTemp)
    tracerApp.setField(fHeat)
    print('Fields connected')

    # Solve

    tracerApp.solveStep(0, runInBackground=False)
    comsolApp.solveStep(0)

    print('Writing VTK-file')
    fid = open('test_heat_field.vtk', mode='w')
    fid.write(str(fHeat.field2VTKData()))
    fid.close()

    print("Done!")
