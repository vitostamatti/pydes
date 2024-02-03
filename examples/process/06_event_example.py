from dataclasses import dataclass
import random
from pydes.process import Simulator, Component, Resource


class Process1(Component):
    def __init__(self, sim: Simulator, event: Resource):
        self.sim = sim
        self.state = event

    def main(self):
        self.sim.record(self, "wait for event")
        self.state.wait()
        self.sim.record(self, "event was triggered")


class Process2(Component):
    def __init__(self, sim: Simulator, state: Resource):
        self.sim = sim
        self.state = state

    def main(self):
        self.sim.record(self, "sleeps before triggering event")
        self.sim.sleep(10)
        self.sim.record(self, "sets event")
        self.state.set()
        self.sim.record(self, "event was set")


if __name__ == "__main__":
    sim = Simulator()
    state = Resource(sim)
    p1 = Process1(sim, state)
    p2 = Process2(sim, state)
    sim.schedule(p1)
    sim.schedule(p2)
    sim.run()
