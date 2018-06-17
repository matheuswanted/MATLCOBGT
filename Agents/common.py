from collections import namedtuple
import itertools

#Player = namedtuple('Player', ['actions','non_conflicting_actions', 'lanes'])
#Lane = namedtuple('Lane', ['id','output','vehicles','vehicles_count','capacity','occupation'])
Action = namedtuple('Action', ['lanes'])
LaneAction = namedtuple('LaneAction',['id', 'value'])
UtilityValue = namedtuple('UtilityValue',['orb', 'ru'])
Environment = namedtuple('Environment',['occupation','lanes'])
#Vehicle = namedtuple('Vehicle',['lanePosition','speed','type'])

TYPES_PRIORITY = dict()

LANE_V_NUMBER = 0x10
LANE_V_IDS = 0x12
LANE_OCCUPANCY = 0x13
LANE_LENGTH= 0x44
LANE_WIDTH = 0x4d
LANE_SPEED = 0x41
VEHICLE_LANE_POSITION = 0x56
VEHICLE_SPEED = 0x40
DEFAULT_V_LENGTH = 5

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class LaneMemory:
    __metaclass__ = Singleton
    def __init__(self, traci):
            self.mem = {}
            self.traci = traci
    def get_lanes(self):
        return self.mem
    def update_context(self):
        self.mem = self.traci.lane.getSubscriptionResults()

class VehicleMemory:
    __metaclass__ = Singleton
    def __init__(self, traci):
            self.mem = {}
            self.traci = traci

    def put(self, key, value):
        self.mem[key] = value
        self.traci.vehicle.subscribe(key,[VEHICLE_LANE_POSITION, VEHICLE_SPEED])

    def get(self,key):
        return self.mem[key]

    def remove(self, key):
        del self.mem[key]

    def update_context(self):
        results = self.traci.vehicle.getSubscriptionResults()

        for k,v in results.iteritems():
            veh = self.mem[k]
            veh.speed = v[VEHICLE_SPEED]
            veh.lanePosition = v[VEHICLE_LANE_POSITION]

class Vehicle:
    def __init__(self, type_id):
        self.speed = 0
        self.type = TYPES_PRIORITY[type_id]
        self.lanePosition = None

class Player:
    def __init__(self):
        self.lanes = []
        self.actions = []

    def expandActions(self):
        self.actions = []
        for combination in  itertools.product('GR',repeat=len(self.lanes)):
            self.actions.append( Action( tuple([LaneAction(self.lanes[i].id, v) for i, v in enumerate(combination)]) ) )

class Lane:
    def __init__(self, id):
        self.id = id
        self.output_occupation = 0
        self.output_lanes = []
        self.vehicles = []
        self.vehicles_count = 0
        self.capacity = 0
        self.occupation = 0

class environmenClock:
    def __init__(self, traci):
        self.actual_time = -1
        self.traci = traci

    def get_time(self):
        return self.actual_time

    def diff(self, time):
        return self.actual_time - time

    def run(self):
        exists_steps = self.traci.simulation.getMinExpectedNumber() > 0
        if exists_steps:
            self.traci.simulationStep()
            self.actual_time += 1
        return exists_steps