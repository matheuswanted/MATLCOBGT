from common import *
    
class gameTheoryUnit:
    def __init__(self, players, id):
        self.lane_utility_matrix = dict()
        self.action_sets = []
        self.load_payoff_matrix(players)
        self.id = id

    def load_payoff_matrix(self, players):
        any_green = lambda action: any(v for i, v in enumerate(action.lanes) if v.value == 'G')
        for a1 in players[0].actions :
            any_green_a1 = any_green(a1)
            for a2 in players[1].actions :
                if not (any_green_a1 and any_green(a2)):
                    self.action_sets.append((a1,a2))

    def init_utility(self, lane, env):
        if lane.occupation != 0 and env.occupation != 0:
            vrr = lane.capacity / (lane.occupation / env.occupation)
        else:
            vrr = 1
        orb = -1 if lane.output_occupation >= 0.95 else 1
        ru = 0
        return vrr, orb, ru

    def utility(self, env):
        for lane in env.lanes.itervalues():
            vrr, orb, ru = self.init_utility(lane, env)
            for vehicle in lane.vehicles:
                if vehicle > 1 :
                    ru += vrr + (vehicle/7)*vrr
                else:
                    ru += 1
            self.lane_utility_matrix[lane.id] = UtilityValue(orb,ru)

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


    def apply_gametheory(self):
        best_action = None
        best_payoff = -200
        payoff_mem = {}
        for a1, a2 in self.action_sets:

            if not payoff_mem.has_key(a1):
                payoff_mem[a1] = self.payoff(a1)

            if not payoff_mem.has_key(a2):
                payoff_mem[a2] = self.payoff(a2)

            payoff = payoff_mem[a1] + payoff_mem[a2]

            if payoff > best_payoff:
                best_payoff = payoff
                best_action = (a1, a2)
        return best_action


    def update(self, env):
        self.utility(env)
        return self.apply_gametheory()
