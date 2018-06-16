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

def getVehiclePriority(vehId, laneSize, lane_occupation):
    t = traci.vehicle.getTypeID(vehId)
    p = TYPES_PRIORITY[t]
    if p > 1:
        v_pos = traci.vehicle.getLanePosition(vehId)
        v_spd = traci.vehicle.getSpeed(vehId)
        v_pos_next = v_spd*3
        #print (v_pos,v_spd,v_pos_next,laneSize,lane_occupation)
        if 1-(v_pos+v_pos_next)/laneSize > max(lane_occupation,(v_pos_next-laneSize)/laneSize, 0.1):
            p = 1
        #print p
    return p

class sensor:
    def __init__(self, id):
        self.id = id
        self.links = traci.trafficlight.getControlledLinks(self.id)
        self.controlledLanes = traci.trafficlight.getControlledLanes(self.id)
        self.lanes = {}
        self.players = [Player(), Player()]
        self.players_loaded = False
        self.load()

    def getEnvironment(self):

        subs = traci.lane.getSubscriptionResults()

        for k,v in self.lanes.iteritems():
            lane = subs[k]
            v.id = k
            v.occupation = lane[LANE_OCCUPANCY]
            v.vehicles =  [getVehiclePriority(vc, lane[LANE_LENGTH], v.occupation) for vc in lane[LANE_V_IDS]]
            v.vehicles_count = lane[LANE_V_NUMBER]
            v.output_occupation = numpy.mean([subs[n][LANE_OCCUPANCY] for n in v.output_lanes])
            v.capacity = math.floor(lane[LANE_LENGTH] / DEFAULT_V_LENGTH)
            #v.width = lane[LANE_WIDTH]
            #v.max_speed = lane[LANE_SPEED]
        return Environment(numpy.mean([l.occupation for l in self.lanes.itervalues()]), self.lanes)

                
    def load(self):
        #print "loading sensor"
        for l in self.links:
            try:
                if not self.lanes.has_key(l[0][0]):
                    self.lanes[l[0][0]] = Lane(l[0][0])
                if l[0][1]:
                    self.lanes[l[0][0]].output_lanes.append(l[0][1])

                self.subscribeLane(l[0][0])
                self.subscribeLane(l[0][1])
            except Exception as e:
                print self.id
                print l
                raise e


    def subscribeLane(self,laneId):
        traci.lane.subscribe(laneId, [LANE_OCCUPANCY, LANE_V_NUMBER, LANE_V_IDS, LANE_LENGTH])

    def setEnvironment(self,plan):
        traci.trafficlight.setRedYellowGreenState(self.id, plan)

    def getControlledLanes(self):
        return self.controlledLanes

    def getPlayers(self):
        if self.players_loaded:
            return self.players    
        config = traci.trafficlight.getCompleteRedYellowGreenDefinition(self.id)

        greeniest_phase = ""
        greeniest_phase_greens = 0

        for phase in config[0]._phases:
            #print phase
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

        #print self.players[0].actions

        return self.players
