# --8<-- [start:imports]
from datetime import datetime, timedelta
from pydes import Component, Simulator

# --8<-- [end:imports]


# --8<-- [start:example-1]
class State(Component):
    def __init__(self, value):
        self.value = value


class Process1(Component):
    def __init__(self, sim: Simulator):
        self.sim = sim

    def main(self):
        for _ in range(3):
            self.sim.record(self.id, "waiting")
            self.sim.sleep(timedelta(minutes=10))
            self.sim.record(self.id, "waiting")


class Process2(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        for _ in range(3):
            self.sim.record(self.id, "waiting")
            self.sim.sleep(timedelta(minutes=2))
            self.sim.record(self.id, "waiting")

        self.sim.record(state.id, "change state")
        self.state.value = True


class Process3(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        self.sim.record(self.id, "wait state")
        self.sim.wait_for(lambda: self.state.value)
        self.sim.record(self.id, "wait state")


# --8<-- [end:example-1]

# --8<-- [start:run]
now = datetime.now()
sim = Simulator(init=datetime.now())
state = State(value=False)
p1 = Process1(sim)
p1_1 = Process1(sim)
p2 = Process2(sim, state)
p3 = Process3(sim, state)

sim.schedule(p1.main)
sim.schedule(p1_1.main, at=now + timedelta(minutes=1))
sim.schedule(p2.main, at=now + timedelta(minutes=10))
sim.schedule(p3.main)
sim.run(until=datetime.max)

# --8<-- [end:run]
