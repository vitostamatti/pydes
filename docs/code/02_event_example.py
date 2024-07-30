# --8<-- [start:imports]
from pydes import Simulator, Component, Event


# --8<-- [end:imports]


# --8<-- [start:example-1]
class Process1(Component):
    def __init__(self, sim: Simulator, event: Event):
        self.sim = sim
        self.event = event

    def main(self):
        self.sim.record(self.id, "wait for event")
        self.event.wait()
        self.sim.record(self.id, "event was triggered")


# --8<-- [end:example-1]


# --8<-- [start:example-2]
class Process2(Component):
    def __init__(self, sim: Simulator, event: Event):
        self.sim = sim
        self.event = event

    def main(self):
        self.sim.record(self.id, "sleeps before triggering event")
        self.sim.sleep(10)
        self.sim.record(self.id, "sets event")
        self.event.set()
        self.sim.record(self.id, "event was set")


# --8<-- [end:example-2]

# --8<-- [start:run]
sim = Simulator()
event = Event(sim)
p1 = Process1(sim, event)
p2 = Process2(sim, event)
sim.schedule(p1.main)
sim.schedule(p2.main)
sim.run()
# --8<-- [end:run]
