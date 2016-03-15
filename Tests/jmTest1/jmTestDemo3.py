import clientConfig3 as cConf
from mmp_tracer_api import objID
from comsol_api import MMPComsolDummy
from mupif import *
import logging
logger = logging.getLogger()

import time as timeTime
start = timeTime.time()
logger.info('Timer started')

# locate nameserver
ns = PyroUtil.connectNameServer(
    nshost=cConf.nshost, nsport=cConf.nsport, hkey=cConf.hkey)

# localize JobManager running on (remote) server and create a tunnel to it
# allocate the first application app1
try:
    mieSolverAppRec = PyroUtil.allocateApplicationWithJobManager(
        ns, cConf.mieSolverJobManRec, cConf.jobNatPorts.pop(0),
        cConf.sshClient, cConf.options, cConf.sshHost)

    tracerSolverAppRec = PyroUtil.allocateApplicationWithJobManager(
        ns, cConf.tracerSolverJobManRec, cConf.jobNatPorts.pop(0),
        cConf.sshClient, cConf.options, cConf.sshHost)

    mieApp = mieSolverAppRec.getApplication()
    tracerApp = tracerSolverAppRec.getApplication()

except Exception as e:
    logger.exception(e)
else:
    if((tracerApp is not None) and (mieApp is not None)):
        logger.info("solvers are not None")

        mieSolverSignature = mieApp.getApplicationSignature()
        logger.info("Working mie solver on server " + mieSolverSignature)

        tracerSolverSignature = tracerApp.getApplicationSignature()
        logger.info("Working tracer solver on server " + tracerSolverSignature)

        #mieApp = MMPMie('localhost')
        #tracerApp = MMPRaytracer('localhost')
        comsolApp = MMPComsolDummy('localhost')

        # Connect functions
        pScat = mieApp.getProperty(PropertyID.PID_ScatteringCrossSections, 0,
                           objID.OBJ_PARTICLE_TYPE_1)

        pPhase = mieApp.getProperty(PropertyID.PID_InverseCumulativeDist, 0,
                            objID.OBJ_PARTICLE_TYPE_1)


        tracerApp.setFunction(pScat)
        tracerApp.setFunction(pPhase)

        # Connect fields
        fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
        fHeat = comsolApp.getField(FieldID.FID_Thermal_absorption_volume, 0)

        tracerApp.setField(fTemp)
        tracerApp.setField(fHeat)

        # Connect properties

        # Emission spectrum
        import numpy as np

        a = {}
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



        # Particle density
        vDens = 0.00000003400
        pDens = Property.Property(value=vDens,
                                  propID=PropertyID.PID_ParticleNumberDensity,
                                  valueType=ValueType.Scalar,
                                  time=0.0,
                                  units=None,
                                  objectID=objID.OBJ_CONE)
        tracerApp.setProperty(pDens)

        # Number of rays to trace
        pRays = Property.Property(value=100,
                                  propID=PropertyID.PID_NumberOfRays,
                                  valueType=ValueType.Scalar,
                                  time=0.0,
                                  units=None,
                                  objectID=objID.OBJ_CONE)
        tracerApp.setProperty(pRays)

        # Solve
        mieApp.solveStep(0)
        logger.debug("mieApp.isSolved=", mieApp.isSolved())  # True

        tracerApp.solveStep(0, runInBackground=False)
        comsolApp.solveStep(0)

        # Plot data to file
        logger.info("Saving vtk")
        v = fTemp.field2VTKData()
        v.tofile('testTemperature.vtk')
        v = fHeat.field2VTKData()
        v.tofile('testHeat.vtk')

    else:
        logger.debug("Connection to server failed, exiting")


finally:
    logger.debug("terminating apps...")

    if mieSolverAppRec:
        mieSolverAppRec.terminateAll()
    if tracerSolverAppRec:
        tracerSolverAppRec.terminateAll()
