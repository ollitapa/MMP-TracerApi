from mmp_tracer_api import MMPRaytracer, objID
from mmp_mie_api import MMPMie
from comsol_api import MMPComsolDummy
from mupif import Property, PropertyID, FieldID, ValueType
import logging
import os

if not os.path.isdir('runFolder'):
    os.mkdir('runFolder')
os.chdir('runFolder')

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

    #from pkg_resources import resource_filename

    # Emission spectrum
    import numpy as np

    #a = {'wavelengths': None, 'intensities': None}
    a = {}
    #A=np.loadtxt(resource_filename(__name__, "data/InvCumul_EM_GREEN.dat"))
    A = np.loadtxt('../../../mmp_tracer_api/data/EM_GREEN.dat')
    a['wavelengths'] = A[:, 0]
    a['intensities'] = A[:, 1]
    em = Property.Property(value=a,
                           propID=PropertyID.PID_EmissionSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_1)
    tracerApp.setProperty(em)

    # Excitation spectrum
    b = {}
    B = np.loadtxt('../../../mmp_tracer_api/data/EX_GREEN.dat')
    b['wavelengths'] = B[:, 0]
    b['intensities'] = B[:, 1]
    ex = Property.Property(value=b,
                           propID=PropertyID.PID_ExcitationSpectrum,
                           valueType=ValueType.Scalar,
                           time=0.0,
                           units=None,
                           objectID=objID.OBJ_PARTICLE_TYPE_1)
    tracerApp.setProperty(ex)

    # Absorption spectrum
    c = {}
    C = np.loadtxt('../../../mmp_tracer_api/data/Abs_GREEN.dat')
    c['wavelengths'] = C[:, 0]
    c['intensities'] = C[:, 1]
    aabs = Property.Property(value=c,
                             propID=PropertyID.PID_AsorptionSpectrum,
                             valueType=ValueType.Scalar,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_PARTICLE_TYPE_1)
    tracerApp.setProperty(aabs)



    logger.info('Properties set!')

    # Solve
    mieApp.solveStep(0)
    logger.debug("mieApp.isSolved=", mieApp.isSolved())  # True

    tracerApp.solveStep(0, runInBackground=False)
    # comsolApp.solveStep(0)

    # Plot data to file
    logger.info("Saving vtk")
    fHeat2 = tracerApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

    v = fHeat2.field2VTKData()
    v.tofile('testHeat.vtk')

    logger.debug("terminating apps...")
