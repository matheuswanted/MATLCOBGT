from gameTheoryUnit import gameTheoryUnit
from sensor import sensor

class controlUnit:
    def __init__(self, clock, sensor):
        self.clock = clock
        self.min_yellow_time = 4
        self.last_transition_time = -100
        self.last_plan = ''
        self.lanes = sensor.getControlledLanes()
        self.last_change = -100
        self.sensor = sensor
        self.mid_transition = False
        #self.num_players = len(sensor.getPlayers())

    def chain(self, *tuples):
        for t in tuples:
            for i, v in enumerate(t):
                yield v

    def convert_plan(self,plan):
        d = dict((lane.id, lane.value) for lane in self.chain(plan[0].lanes, plan[1].lanes))
        normalized = ''.join(d[lane_id] for lane_id in self.lanes)
        normalized = normalized.replace('R','r')
        return normalized

    def complete_transition(self):
        if self.clock.diff(self.last_transition_time) >= self.min_yellow_time:
            self.simple_transition_strategy(self.next_plan)

    def simple_transition_strategy(self, plan):
        self.mid_transition = False
        self.last_plan = plan
        self.last_transition_time = self.clock.get_time()
        self.sensor.setEnvironment(plan)

    def yellow_transition_strategy(self, plan):
        self.next_plan = plan
        self.last_plan = self.last_plan.replace('G','y')
        self.last_transition_time = self.clock.get_time()
        self.mid_transition = True
        self.sensor.setEnvironment(self.last_plan)

    def execute_transition(self, next_plan):
        plan = self.convert_plan(next_plan)

        if self.last_plan == '': #or self.num_players <2:
            self.simple_transition_strategy(plan)

        elif plan != self.last_plan:
            self.yellow_transition_strategy(plan)

    def minimun_green_achieved(self):
        return 'G' not in self.last_plan or self.clock.diff(self.last_transition_time) >= 5

class autonomousPoint:
    def __init__(self, tls_id, clock):
        self.sensor = sensor(tls_id)
        self.agent = gameTheoryUnit(self.sensor.getPlayers(), tls_id)
        self.controlUnit = controlUnit(clock, self.sensor)

    def update(self):
        if not self.controlUnit.mid_transition:
            if self.controlUnit.minimun_green_achieved():
                env = self.sensor.getEnvironment()
                plan = self.agent.update(env)
                self.controlUnit.execute_transition(plan)
        else:
            self.controlUnit.complete_transition()