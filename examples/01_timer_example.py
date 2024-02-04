from pydes import Component, Simulator


class Timer1(Component):
    def __init__(self, sim: Simulator, time: float = 10):
        self.sim = sim
        self.time = time

    def main(self):
        i = 0
        while True:
            self.sim.record(
                self,
                "running loop",
                0,
            )
            i += 1
            self.sim.sleep(self.time)


class Timer2(Component):
    def __init__(self, sim: Simulator, time: float = 10):
        self.sim = sim
        self.time = time

    def main(self):
        i = 0
        self.sim.record(
            self,
            "running loop",
            0,
        )
        i += 1
        self.sim.sleep(self.time)
        self.sim.schedule(self)


if __name__ == "__main__":
    sim = Simulator()
    timer = Timer1(sim, time=10)
    sim.schedule(timer)
    sim.run(100)

    sim.reset()
    timer = Timer2(sim, time=10)
    sim.schedule(timer)
    sim.run(100)
