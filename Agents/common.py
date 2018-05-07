from collections import namedtuple
import itertools

#Player = namedtuple('Player', ['actions','non_conflicting_actions', 'lanes'])
#Lane = namedtuple('Lane', ['id','output','vehicles','vehicles_count','capacity','occupation'])
Action = namedtuple('Action', ['lanes'])
LaneAction = namedtuple('LaneAction',['id', 'value'])
UtilityValue = namedtuple('UtilityValue',['orb', 'ru'])
Environment = namedtuple('Environment',['occupation','lanes'])

TYPES_PRIORITY = dict()

LANE_V_NUMBER = 0x10
LANE_V_IDS = 0x12
LANE_OCCUPANCY = 0x13
LANE_LENGTH= 0x44
DEFAULT_V_LENGTH = 5

class Player:
    def __init__(self):
        self.lanes = []
        self.actions = []

    def expandActions(self):
        self.actions = []
        for combination in  itertools.combinations('GR',len(self.lanes)):
            self.actions.append( Action( LaneAction(self.lanes[i].id, v) for i, v in enumerate(combination) ) )

class Lane:
    def __init__(self, id):
        self.id = id
        self.output_occupation = 0
        self.output_lanes = []
        self.vehicles = []
        self.vehicles_count = 0
        self.capacity = 0
        self.occupation = 0