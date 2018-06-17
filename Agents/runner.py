#!/usr/bin/env python
# # Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2017 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26
# @version $Id$

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
#import multiprocessing

#import ptvsd
#ptvsd.enable_attach("my_secret", address = ('0.0.0.0', 3000))

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.environ.get("SUMO_HOME")+"/tools")  # tutorial in tests
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
import threading
from autonomousPoint import autonomousPoint
from sensor import sensor
from common import *

def update(ap):
    ap.update()
    return 1

def run(all_tls):
    """execute the TraCI control loop"""
    tlss = traci.trafficlight.getIDList()

    TYPES_PRIORITY['typeNS'] = 7
    TYPES_PRIORITY['typeWE'] = 1
    TYPES_PRIORITY['DEFAULT_VEHTYPE'] = 1
    TYPES_PRIORITY['PRT'] = 1
    clock = environmenClock(traci)
    v_mem = VehicleMemory(traci)
    l_mem = LaneMemory(traci)
    
    aps = [autonomousPoint(tls, clock) for tls in tlss if all_tls or tls.split("_")[0] != 'st']
    

    while clock.run():
        loaded = traci.simulation.getDepartedIDList()
        for v_id in loaded:
            tp = traci.vehicle.getTypeID(v_id)
            v_mem.put(v_id, Vehicle(tp))
        loaded = traci.simulation.getArrivedIDList()

        for v_id in loaded:
            v_mem.remove(v_id)
        
        v_mem.update_context()   
        l_mem.update_context() 
        
        for ap in aps:
            ap.update()
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--onlyactuated", action="store_true", default=False)
    optParser.add_option("-c", help="Sumo config file inside folder")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    #generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", options.c, "--ignore-route-errors"])
    run(not options.onlyactuated)
