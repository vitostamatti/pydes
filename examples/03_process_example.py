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
            self.sim.sleep(10)
            self.sim.record(self, "waiting", 0)


class Process2(Component):
    def __init__(self, sim: Simulator, state: State):
        self.sim = sim
        self.state = state

    def main(self):
        for _ in range(10):
            self.sim.record(self, "waiting", 1)
            self.sim.sleep(2)
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
    sim = Simulator()
    state = State(value=False)
    fb1 = Process1(sim)
    fb1_1 = Process1(sim)
    fb2 = Process2(sim, state)
    fb3 = Process3(sim, state)

    sim.schedule(fb1)
    sim.schedule(fb1_1, at=1)
    sim.schedule(fb2, at=20)
    sim.schedule(fb3)
    sim.run()

    sim.records()
