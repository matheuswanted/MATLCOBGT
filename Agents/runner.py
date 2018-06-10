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
from autonomousPoint import autonomousPoint
from sensor import sensor
from common import TYPES_PRIORITY

def run(all_tls):
    """execute the TraCI control loop"""
    step = 0
    #traci.trafficlight.setPhase("0", 2)
    tlss = traci.trafficlight.getIDList()

    TYPES_PRIORITY['typeNS'] = 7
    TYPES_PRIORITY['typeWE'] = 1
    TYPES_PRIORITY['DEFAULT_VEHTYPE'] = 1

    aps = [autonomousPoint(sensor(tls)) for tls in tlss if all_tls or tls.split("_")[0] != 'st']

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        for ap in aps:
            ap.update()
        step += 1
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--onlyactuated", action="store_true", default=False)
    optParser.add_option("-c", help="Sumo config file inside folder")
    optParser.add_option("-t", help="Trip output")
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
    traci.start([sumoBinary, "-c", options.c,"--tripinfo-output", options.t])
    run(not options.onlyactuated)
