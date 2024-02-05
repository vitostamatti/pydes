# --8<-- [start:imports]
from dataclasses import dataclass
import random
from pydes import Component, Queue, Simulator

# --8<-- [end:imports]


# --8<-- [start:example-1]
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
            self.sim.record(self, "inserted element into queue")
            self.sim.record(self, "{self.queue.size()} elements in queue")
            i += 1


# --8<-- [end:example-1]


# --8<-- [start:example-2]
class Process2(Component):
    def __init__(self, sim: Simulator, queue: Queue):
        self.sim = sim
        self.queue = queue

    def main(self):
        while True:
            self.sim.record(self, "requesting an element from queue")
            e = self.queue.get()
            self.sim.record(self, f"got {e} from queue")
            self.sim.record(self, "waiting before getting next element")
            self.sim.sleep(random.randint(10, 20))


# --8<-- [end:example-2]

# --8<-- [start:run]
sim = Simulator()
queue = Queue(sim)
p1 = Process1(sim, queue)
p2 = Process2(sim, queue)
sim.schedule(p1)
sim.schedule(p2)
sim.run(until=100)
# --8<-- [end:run]
