# --8<-- [start:imports]
from enum import Enum
from pydes import Component, Simulator, State

# --8<-- [end:imports]


# --8<-- [start:example-1]
class States(Enum):
    FALSE = 0
    TRUE = 1


# --8<-- [end:example-1]


# --8<-- [start:example-2]
class Process1(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        self.sim.record(self.id, "wait for state")
        self.state.wait(States.TRUE)
        self.sim.record(self.id, "state wait finished")


# --8<-- [end:example-2]


# --8<-- [start:example-3]
class Process2(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        self.sim.record(self.id, "sleeps before changing state")
        self.sim.sleep(10)
        self.sim.record(self.id, "sets state")
        self.state.set(States.TRUE)
        self.sim.record(self.id, "state changed")


# --8<-- [end:example-3]

# --8<-- [start:run]
sim = Simulator()
state = State(sim, States.FALSE)
p1 = Process1(sim, state)
p2 = Process2(sim, state)
sim.schedule(p1.main)
sim.schedule(p2.main)
sim.run()
# --8<-- [end:run]
