# --8<-- [start:imports]
from pydes import Component, Container, Simulator

# --8<-- [end:imports]


# --8<-- [start:example-1]
class Process1(Component):
    def __init__(self, sim: Simulator, container: Container):
        self.sim = sim
        self.container = container

    def main(self):
        # generating elements:
        while True:
            amount = 5
            self.sim.record(self.id, f"begin put {amount} into container")
            self.container.put(amount)
            self.sim.record(self.id, f"end put {amount} into container")
            self.sim.record(self.id, f"container level: {self.container.level()}")
            self.sim.sleep(1)


# --8<-- [end:example-1]


# --8<-- [start:example-2]
class Process2(Component):
    def __init__(self, sim: Simulator, container: Container):
        self.sim = sim
        self.container = container

    def main(self):
        while True:
            amount = 15
            self.sim.record(self.id, f"begin get {amount} from container")
            self.container.get(amount)
            self.sim.record(self.id, f"end get {amount} from container")
            self.sim.record(self.id, f"container level: {self.container.level()}")


# --8<-- [end:example-2]

# --8<-- [start:run]

sim = Simulator()
container = Container(sim)
p1 = Process1(sim, container)
p2 = Process2(sim, container)
sim.schedule(p1.main)
sim.schedule(p2.main)
sim.run(until=10)
# --8<-- [end:run]
