# --8<-- [start:example]
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


# --8<-- [end:example]


# --8<-- [start:run-example]
print("Timer 1")
sim = Simulator()
timer = Timer1(sim, time=10)
sim.schedule(timer)
sim.run(30)
print("Timer 2")
sim.reset()
timer = Timer2(sim, time=10)
sim.schedule(timer)
sim.run(30)
# --8<-- [end:run-example]
