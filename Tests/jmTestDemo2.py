import clientConfig2 as cConf
from mupif import *
import logging
logger = logging.getLogger()

import time as timeTime
start = timeTime.time()
logger.info('Timer started')

#locate nameserver
ns = PyroUtil.connectNameServer(nshost=cConf.nshost, nsport=cConf.nsport, hkey=cConf.hkey)

#localize JobManager running on (remote) server and create a tunnel to it
#allocate the first application app1
try:
    #thermalSolverAppRec = PyroUtil.allocateApplicationWithJobManager( ns, cConf.thermalSolverJobManRec, cConf.jobNatPorts.pop(0), cConf.sshClient, cConf.options, cConf.sshHost )
    mieSolverAppRec = PyroUtil.allocateApplicationWithJobManager( ns, cConf.mieSolverJobManRec, cConf.jobNatPorts.pop(0), cConf.sshClient, cConf.options, cConf.sshHost )
    #mechanicalSolverAppRec = PyroUtil.allocateApplicationWithJobManager( ns, cConf.mechanicalSolverJobManRec, cConf.jobNatPorts.pop(0), cConf.sshClient, cConf.options, cConf.sshHost )

    tracerSolverAppRec = PyroUtil.allocateApplicationWithJobManager( ns, cConf.tracerSolverJobManRec, cConf.jobNatPorts.pop(0), cConf.sshClient, cConf.options, cConf.sshHost )

    
    mieApp = mieSolverAppRec.getApplication()
    
    tracerApp = tracerSolverAppRec.getApplication()
    
except Exception as e:
    logger.exception(e)
else:
    if((tracerApp is not None) and (mieApp is not None)):
        logger.info("solvers are not None")


        mieSolverSignature=mieApp.getApplicationSignature()
        logger.info("Working mie solver on server " + mieSolverSignature)

        tracerSolverSignature=tracerApp.getApplicationSignature()
        logger.info("Working tracer solver on server " + tracerSolverSignature)


        #initialize the apps:
        from mmp_mie_api import MMPMie
        from comsol_api import MMPComsolDummy
        from mmp_tracer_api import MMPRaytracer, objID

        #mieApp = MMPMie('localhost')
        #tracerApp = MMPRaytracer('localhost')
        comsolApp = MMPComsolDummy('localhost')

        # Connect functions
        fScat = mieApp.getFunction(FunctionID.FuncID_ScatteringCrossSections, 0)

        fPhase = mieApp.getFunction(FunctionID.FuncID_ScatteringInvCumulDist, 0)
       

        tracerApp.setFunction(fScat) 
        tracerApp.setFunction(fPhase)

        # Connect fields
        fTemp = comsolApp.getField(FieldID.FID_Temperature, 0)
        fHeat = comsolApp.getField(FieldID.FID_HeatSourceVol, 0)

        tracerApp.setField(fTemp)
        tracerApp.setField(fHeat)

        # Connect properties
        # Particle density
        vDens = 0.00000003400
        pDens = Property.Property(value=vDens, propID = PropertyID.PID_ParticleNumberDensity, valueType = ValueType.Scalar, time = 0.0, units=None, objectID=objID.OBJ_CONE)
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
        print("mieApp.isSolved=", mieApp.isSolved()) #True

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
    print("terminating apps...")
    if mieSolverAppRec: mieSolverAppRec.terminateAll()
    if tracerSolverAppRec: tracerSolverAppRec.terminateAll()




