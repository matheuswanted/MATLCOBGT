from collections import namedtuple

Player = namedtuple('Player', ['actions','non_conflicting_actions'])
Environment = namedtuple('Environment', ['lanes','occupation'])
Lane = namedtuple('Lane', ['id','vehicles','vehicles_count','capacity','occupation'])
Action = namedtuple('Action', ['lanes'])
LaneAction = namedtuple('LaneAction',['id', 'light_id', 'light_value'])

class autonomousPoint:
    def __init__(self, sensor):
        self.sensor = sensor
        self.agent = baseAgent(sensor.getPlayers())

    def update(self):
        env = self.sensor.getEnvironment()
        plan = self.agent.update(env)
        self.sensor.setEnvironment(plan)

class sensor:
    def __init__(self):
        pass

    def getEnvironment(self):
        pass

    def setEnvironment(self,plan):
        pass

    def getPlayers(self):
        pass

    
class baseAgent:
    def __init__(self, players):
        self.lane_utility_matrix = dict()
        self.payoff_matrix = dict()
        self.load_payoff_matrix(players)

    def load_payoff_matrix(self, players):
        for a1 in players[0].actions :
            for a2 in players[1].actions :
                for l1 in a1.lanes:
                    if l1.light_value == 'g' and any( l2.light_value for l2 in a2.lanes):
                        self.payoff_matrix[(a1,a2)] = (-100,-100)

            if not self.payoff_matrix.has_key((a1,a2)):
                self.payoff_matrix[(a1,a2)] = (0,0)

    def utility(self, env):
        for lane in env.lanes:
            orb = -1 if lane.output_lane.vehicles_count / lane.output_lane.capacity >= 0.95 else 1
            vrr = lane.capacity / (lane.occupation / env.occupation)
            ru = 0
            for vehicle in lane.vehicles:
                if vehicle > 1 :
                    evr = vrr + (vehicle/7)*vrr
                    ru += evr
                else:
                    ru += 1
            self.lane_utility_matrix[lane.id] = (orb,ru)

    def plan_actions(self):
        for a1, a2 in self.payoff_matrix.keys :
            if self.payoff_matrix[(a1,a2)] != (-100,-100):
                self.payoff_matrix[(a1,a2)] = (self.payoff(a1), self.payoff(a2))

    def payoff(self, action):
        if all(l.light_value == 'r' for l in action.lanes) : 
            return sum( self.lane_utility_matrix[l.id][1] for l in action.lanes)
        else:
            return sum(self.lane_utility_matrix[l.id][0]* self.lane_utility_matrix[l.id][1] if l.light == 'v' else 0 for l in action.lanes)

    def act(self):
        best_action = None
        best_plan = (-100,-100)
        for action, plan in self.payoff_matrix.iteritems():
            if plan[0] > best_plan[0] and plan[1]> best_plan[1]:
                best_plan = plan
                best_action = action
        return best_action


    def update(self, env):
        self.utility(env)
        self.plan_actions()
        return self.act()
