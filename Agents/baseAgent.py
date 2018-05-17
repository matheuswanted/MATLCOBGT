from common import *
    
class baseAgent:
    def __init__(self, players):
        self.lane_utility_matrix = dict()
        self.payoff_matrix = dict()
        self.load_payoff_matrix(players)

    def load_payoff_matrix(self, players):

        any_green = lambda action: any(v for i, v in enumerate(action.lanes) if v.value == 'G')
        #print "load payoff"
        for a1 in players[0].actions :
            any_green_a1 = any_green(a1)
            #print a1,any_green_a1
            for a2 in players[1].actions :
                self.payoff_matrix[(a1,a2)] = (-100,-100) if any_green_a1 and any_green(a2) else (0,0)
                #print (a1,a2), self.payoff_matrix[(a1,a2)]

    def utility(self, env):
        for lane in env.lanes.itervalues():
            vrr = lane.capacity / (lane.occupation / env.occupation)
            print lane.capacity
            orb = -1 if lane.output_occupation >= 0.95 else 1
            ru = 0
            for vehicle in lane.vehicles:
                if vehicle > 1 :
                    print 'priorit in ' + lane.id
                    ru += vrr + (vehicle/7)*vrr
                else:
                    ru += 1
            self.lane_utility_matrix[lane.id] = UtilityValue(orb,ru)
            print lane.id, self.lane_utility_matrix[lane.id]

    def plan_actions(self):
        for a1, a2 in self.payoff_matrix.keys() :
            if self.payoff_matrix[(a1,a2)] != (-100,-100):
                self.payoff_matrix[(a1,a2)] = (self.payoff(a1), self.payoff(a2))
                #print self.payoff_matrix[(a1,a2)]

    def payoff(self, action):
        all_red_payoff = 0
        otherwise_payoff = 0
        for i, laneAction in enumerate(action.lanes):
            utility = self.lane_utility_matrix[laneAction.id]

            if laneAction.value == 'R':
                all_red_payoff -= utility.ru
            else:
                otherwise_payoff += utility.orb * utility.ru
        
        return all_red_payoff if otherwise_payoff == 0 else otherwise_payoff

    def act(self):
        best_action = None
        best_payoff = (-100,-100)
        for action, payoff in self.payoff_matrix.iteritems():
            print action,payoff
            if payoff[0] > best_payoff[0] and payoff[1]> best_payoff[1]:
                best_payoff = payoff
                best_action = action
        return best_action

    def update(self, env):
        self.utility(env)
        self.plan_actions()
        return self.act()
