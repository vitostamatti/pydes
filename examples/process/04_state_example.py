from enum import Enum
from pydes.process import Component, Simulator, State


class States(Enum):
    FALSE = 0
    TRUE = 1


class Process1(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        self.sim.record(self, "wait for state")
        self.state.wait(States.TRUE)
        self.sim.record(self, "state wait finished")


class Process2(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        self.sim.record(self, "sleeps before changing state")
        self.sim.sleep(10)
        self.sim.record(self, "sets state")
        self.state.set(States.TRUE)
        self.sim.record(self, "state changed")


if __name__ == "__main__":
    sim = Simulator()
    state = State(sim, States.FALSE)
    p1 = Process1(sim, state)
    p2 = Process2(sim, state)
    sim.schedule(p1)
    sim.schedule(p2)
    sim.run()
