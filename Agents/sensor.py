from common import *
import math
import numpy
import os
import sys
try:
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME"),"/tools"))  # tutorial in tests
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci

def getVehiclePriority(vehId):
    t = traci.vehicle.getTypeID(vehId)
    return TYPES_PRIORITY[t]

class sensor:
    def __init__(self, id):
        self.id = id
        self.links = traci.trafficlight.getControlledLinks(self.id)
        self.controlledLanes = traci.trafficlight.getControlledLanes(self.id)
        self.lanes = {}
        self.players = [Player(), Player()]
        self.load()

    def getEnvironment(self):

        subs = traci.lane.getSubscriptionResults()

        for k,v in self.lanes.iteritems():
            lane = subs[k]
            v.occupation = lane[LANE_OCCUPANCY]
            v.vehicles =  [getVehiclePriority(vc) for vc in lane[LANE_V_IDS]]
            v.vehicles_count = lane[LANE_V_NUMBER]
            v.output_occupation = numpy.mean([subs[n][LANE_OCCUPANCY] for n in v.output_lanes])
            v.capacity = math.floor(lane[LANE_LENGTH] / DEFAULT_V_LENGTH)
        return Environment(numpy.mean([l.occupation for l in self.lanes.itervalues()]), self.lanes)

                
    def load(self):
        print "loading sensor"
        for l in self.links:
            if not self.lanes.has_key(l[0][0]):
                self.lanes[l[0][0]] = Lane(l[0][0])
            if l[0][1]:
                self.lanes[l[0][0]].output_lanes.append(l[0][1])

            self.subscribeLane(l[0][0])
            self.subscribeLane(l[0][1])

    def subscribeLane(self,laneId):
        traci.lane.subscribe(laneId, [LANE_OCCUPANCY, LANE_V_NUMBER, LANE_V_IDS, LANE_LENGTH])

    def chain(self, *tuples):
        for t in tuples:
            for i, v in enumerate(t):
                yield v

    def setEnvironment(self,plan):
        d = dict((lane.id, lane.value) for lane in self.chain(plan[0].lanes, plan[1].lanes))
        r = ''.join(d[lane_id] for lane_id in self.controlledLanes)
        print r
        traci.trafficlight.setRedYellowGreenState(self.id, r)

    def getPlayers(self):       
        config = traci.trafficlight.getCompleteRedYellowGreenDefinition(self.id)

        greeniest_phase = ""
        greeniest_phase_greens = 0

        for phase in config[0]._phases:
            print phase
            if greeniest_phase_greens < phase._phaseDef.lower().count('g'):
                greeniest_phase = phase._phaseDef.lower()
                greeniest_phase_greens = phase._phaseDef.lower().count('g')
        
        for i, v in enumerate(greeniest_phase):
            if v == 'g':
                self.players[0].lanes.append(self.lanes[self.controlledLanes[i]])
            else:
                self.players[1].lanes.append(self.lanes[self.controlledLanes[i]])

        self.players[0].expandActions()
        self.players[1].expandActions()

        print self.players[0].actions

        return self.players
