from dataclasses import dataclass
import random
from pydes import Component, Queue
from pydes import Simulator


@dataclass
class Element:
    id: int


class Process1(Component):
    def __init__(self, sim: Simulator, queue: Queue):
        self.sim = sim
        self.queue = queue

    def main(self):
        # generating elements:
        i = 0
        while True:
            e = Element(i)
            self.sim.record(self, f"wait before inserting {e} into queue")
            self.sim.sleep(random.randint(5, 10))
            self.queue.put(e)
            self.sim.record(self, f"inserted element into queue")
            self.sim.record(self, f"{self.queue.size()} elements in queue")
            i += 1


class Process2(Component):
    def __init__(self, sim: Simulator, queue: Queue):
        self.sim = sim
        self.queue = queue

    def main(self):
        while True:
            self.sim.record(self, f"requesting an element from queue")
            e = self.queue.get()
            self.sim.record(self, f"got {e} from queue")
            self.sim.record(self, f"waiting before getting next element")
            self.sim.sleep(random.randint(10, 20))


if __name__ == "__main__":
    sim = Simulator()
    queue = Queue(sim)
    p1 = Process1(sim, queue)
    p2 = Process2(sim, queue)
    sim.schedule(p1)
    sim.schedule(p2)
    sim.run(until=100)
