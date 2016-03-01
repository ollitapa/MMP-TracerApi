from mmp_tracer_api import MMPRaytracer, objID
from mmp_mie_api import MMPMie
from comsol_api import MMPComsolDummy
from mupif import Property, PropertyID, FieldID, ValueType
import logging
import ex_em_import

if __name__ == '__main__':

    logger = logging.getLogger()

    import time as timeTime
    start = timeTime.time()
    logger.info('Timer started')

    mieApp = MMPMie('localhost')
    tracerApp = MMPRaytracer('localhost')
    comsolApp = MMPComsolDummy('localhost')

    # Point data conversion to false. Speeds up testing
    tracerApp._convertPointData = False

    logger.info('Applications loaded:')
    print(mieApp)
    print(tracerApp)
    print(comsolApp)

    # Connect functions

    logger.info('Connecting Mie properties...')
    pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                               objID.OBJ_PARTICLE_TYPE_1)

    pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                                objID.OBJ_PARTICLE_TYPE_1)

    logger.info('Props received...')
    tracerApp.setProperty(pScat, objID.OBJ_PARTICLE_TYPE_1)
    tracerApp.setProperty(pPhase, objID.OBJ_PARTICLE_TYPE_1)
    logger.info('Props connected')

    # Connect fields
    logger.info('Connecting Fields...')
    fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
    fHeat = comsolApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

    tracerApp.setField(fTemp)
    tracerApp.setField(fHeat)
    logger.info('Fields connected')

    # Connect properties
    # Particle density
    logger.info('Setting Properties...')
    vDens = 0.00000003400
    pDens = Property.Property(value=vDens,
                              propID=PropertyID.PID_ParticleNumberDensity,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
    tracerApp.setProperty(pDens)

    # Number of rays
    nRays = Property.Property(value=100,
                              propID=PropertyID.PID_NumberOfRays,
                              valueType=ValueType.Scalar,
                              time=0.0,
                              units=None,
                              objectID=objID.OBJ_CONE)
    tracerApp.setProperty(nRays)

    # Emission spectrum
    em = Property.Property(value=ex_em_import.getEm(),
                           propID=PropertyID.PID_EmissionSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_CONE)
    tracerApp.setProperty(em)

    # Excitation spectrum
    ex = Property.Property(value=ex_em_import.getEx(),
                           propID=PropertyID.PID_EmissionSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_CONE)
    tracerApp.setProperty(ex)

    # Absorption spectrum
    aabs = Property.Property(value=ex_em_import.getAbs(),
                             propID=PropertyID.PID_EmissionSpectrum,
                             valueType=ValueType.Scalar,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_CONE)
    tracerApp.setProperty(aabs)

    logger.info('Properties set!')

    # Solve
    mieApp.solveStep(0)
    logger.debug("mieApp.isSolved=", mieApp.isSolved())  # True

    tracerApp.solveStep(0, runInBackground=False)
    # comsolApp.solveStep(0)

    # Plot data to file
    logger.info("Saving vtk")
    #v = fTemp.field2VTKData()
    # v.tofile('testTemperature.vtk')
    #v = fHeat.field2VTKData()
    # v.tofile('testHeat.vtk')

    logger.debug("terminating apps...")
