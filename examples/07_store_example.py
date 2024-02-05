from dataclasses import dataclass
from pydes import Component, Store, Simulator


@dataclass
class Element:
    id: int


class Process1(Component):
    def __init__(self, sim: Simulator, store: Store):
        self.sim = sim
        self.store = store

    def main(self):
        # generating elements:
        i = 0
        while True:
            e = Element(i)
            self.sim.record(self, f"start put")
            self.store.put(e)
            self.sim.record(self, f"end put")
            self.sim.record(self, f"store level: {self.store.level()}")
            self.sim.sleep(5)
            i += 1


class Process2(Component):
    def __init__(self, sim: Simulator, store: Store):
        self.sim = sim
        self.store = store

    def main(self):
        while True:
            self.sim.record(self, f"start get")
            e = self.store.get()
            self.sim.record(self, f"end get: {e}")
            self.sim.record(self, f"store level: {self.store.level()}")
            self.sim.sleep(20)


if __name__ == "__main__":
    sim = Simulator()
    store = Store(sim, 3)
    p1 = Process1(sim, store)
    p2 = Process2(sim, store)
    sim.schedule(p1)
    sim.schedule(p2)
    sim.run(until=100)
