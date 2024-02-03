from dataclasses import dataclass
import random
from pydes.process import Simulator, Component, Resource


class Process1(Component):
    def __init__(self, sim: Simulator, resource: Resource):
        self.sim = sim
        self.resource = resource

    def main(self):
        self.sim.record(self, "requesting resource")
        self.resource.request(self)
        self.sim.record(self, "resource aquired")
        self.sim.sleep(10)
        self.sim.record(self, "releasing resource")
        self.resource.release(self)
        self.sim.record(self, "resource released")


class Process2(Component):
    def __init__(self, sim: Simulator, resource: Resource):
        self.sim = sim
        self.resource = resource

    def main(self):
        self.sim.record(self, "sleeps before requesting")
        self.sim.sleep(5)
        self.sim.record(self, "requesting resource")
        self.resource.request(self)
        self.sim.record(self, "resource aquired")
        self.sim.sleep(10)
        self.sim.record(self, "releasing resource")
        self.resource.release(self)
        self.sim.record(self, "resource released")


if __name__ == "__main__":
    sim = Simulator()
    resource = Resource(sim)
    p1 = Process1(sim, resource)
    p2 = Process2(sim, resource)
    sim.schedule(p1)
    sim.schedule(p2)
    sim.run()
