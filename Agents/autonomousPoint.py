from baseAgent import *

class autonomousPoint:
    def __init__(self, sensor):
        self.sensor = sensor
        self.agent = baseAgent(sensor.getPlayers())

    def update(self):
        env = self.sensor.getEnvironment()
        plan = self.agent.update(env)
        self.sensor.setEnvironment(plan)