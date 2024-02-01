from pydes.events import AbstractEvent, Simulator


class Timeout(AbstractEvent):
    def __init__(self, time: float):
        self.time = time

    def trigger(self, sim: Simulator):
        print(f"The time is {sim.now()}")
        sim.schedule(self, self.time)


if __name__ == "__main__":
    sim = Simulator(0.0)
    sim.schedule(Timeout(10), 0)
    sim.run(100)
