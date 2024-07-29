# --8<-- [start:imports]
from dataclasses import dataclass
from pydes import Component, Store, Simulator

# --8<-- [end:imports]


# --8<-- [start:example-1]
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
            self.sim.record(self.id, "start put")
            self.store.put(e)
            self.sim.record(self.id, "end put")
            self.sim.record(self.id, f"store level: {self.store.level()}")
            self.sim.sleep(5)
            i += 1


# --8<-- [end:example-1]


# --8<-- [start:example-2]
class Process2(Component):
    def __init__(self, sim: Simulator, store: Store):
        self.sim = sim
        self.store = store

    def main(self):
        while True:
            self.sim.record(self.id, "start get")
            e = self.store.get()
            self.sim.record(self.id, f"end get: {e}")
            self.sim.record(self.id, f"store level: {self.store.level()}")
            self.sim.sleep(20)


# --8<-- [end:example-2]

# --8<-- [start:run]

sim = Simulator()
store = Store(sim, 3)
p1 = Process1(sim, store)
p2 = Process2(sim, store)
sim.schedule(p1.main)
sim.schedule(p2.main)
sim.run(until=20)
# --8<-- [end:run]
