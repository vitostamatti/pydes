# --8<-- [start:imports]
from pydes import Simulator, Component, Resource

# --8<-- [end:imports]


# --8<-- [start:example-1]
class Process1(Component):
    def __init__(self, sim: Simulator, resource: Resource):
        self.sim = sim
        self.resource = resource

    def main(self):
        self.sim.record(self.id, "requesting resource")
        self.resource.request(self)
        self.sim.record(self.id, "resource aquired")
        self.sim.sleep(10)
        self.sim.record(self.id, "releasing resource")
        self.resource.release(self)
        self.sim.record(self.id, "resource released")


# --8<-- [end:example-1]


# --8<-- [start:example-2]
class Process2(Component):
    def __init__(self, sim: Simulator, resource: Resource):
        self.sim = sim
        self.resource = resource

    def main(self):
        self.sim.record(self.id, "sleeps before requesting")
        self.sim.sleep(5)
        self.sim.record(self.id, "requesting resource")
        self.resource.request(self)
        self.sim.record(self.id, "resource aquired")
        self.sim.sleep(10)
        self.sim.record(self.id, "releasing resource")
        self.resource.release(self)
        self.sim.record(self.id, "resource released")


# --8<-- [end:example-2]

# --8<-- [start:run]
sim = Simulator()
resource = Resource(sim)
p1 = Process1(sim, resource)
p2 = Process2(sim, resource)
sim.schedule(p1.main)
sim.schedule(p2.main)
sim.run()
# --8<-- [end:run]
