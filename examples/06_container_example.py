from pydes import Component, Container
from pydes import Simulator


class Process1(Component):
    def __init__(self, sim: Simulator, container: Container):
        self.sim = sim
        self.container = container

    def main(self):
        # generating elements:
        while True:
            amount = 5
            self.sim.record(self, f"begin put {amount} into container")
            self.container.put(amount)
            self.sim.record(self, f"end put {amount} into container")
            self.sim.record(self, f"container level: {self.container.level()}")
            self.sim.sleep(1)


class Process2(Component):
    def __init__(self, sim: Simulator, container: Container):
        self.sim = sim
        self.container = container

    def main(self):
        while True:
            amount = 15
            self.sim.record(self, f"begin get {amount} from container")
            self.container.get(amount)
            self.sim.record(self, f"end get {amount} from container")
            self.sim.record(self, f"container level: {self.container.level()}")


if __name__ == "__main__":
    sim = Simulator()
    container = Container(sim)
    p1 = Process1(sim, container)
    p2 = Process2(sim, container)
    sim.schedule(p1)
    sim.schedule(p2)
    sim.run(until=10)
