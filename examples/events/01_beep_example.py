# Beep Example
from pydes.events import Simulator, Event


class Beep(Event):
    def trigger(self, sim: Simulator):
        print(f"The time is {sim.now()}")


if __name__ == "__main__":
    sim = Simulator(0.0)
    sim.schedule(Beep(), 4.0)
    sim.schedule(Beep(), 3.0)
    sim.schedule(Beep(), 1.0)
    sim.schedule(Beep(), 2.0)
    sim.run(until=3)
