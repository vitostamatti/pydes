from datetime import datetime, timedelta
from pydes import Component, Simulator


class State(Component):
    def __init__(self, value):
        self.value = value


class Process1(Component):
    def __init__(self, sim: Simulator):
        self.sim = sim

    def main(self):
        for _ in range(10):
            self.sim.record(
                self,
                "waiting",
                1,
            )

            self.sim.sleep(timedelta(minutes=10))
            self.sim.record(self, "waiting", 0)


class Process2(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        for _ in range(10):
            self.sim.record(self, "waiting", 1)
            self.sim.sleep(timedelta(minutes=2))
            self.sim.record(self, "waiting", 0)

        self.sim.record(state, "change state", True)
        self.state.value = True


class Process3(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        self.sim.record(self, "wait state", 1)
        self.sim.wait_for(lambda: self.state.value)
        self.sim.record(self, "wait state", 0)


if __name__ == "__main__":
    now = datetime.now()
    sim = Simulator(initial_time=datetime.now())
    state = State(value=False)
    p1 = Process1(sim)
    p1_1 = Process1(sim)
    p2 = Process2(sim, state)
    p3 = Process3(sim, state)

    sim.schedule(p1)
    sim.schedule(p1_1, at=now + timedelta(minutes=1))
    sim.schedule(p2, at=now + timedelta(minutes=10))
    sim.schedule(p3)
    sim.run()

    sim.records()
