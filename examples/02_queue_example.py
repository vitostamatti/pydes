from itertools import count
from typing import List, Optional
from pydes import Component, Simulator
import random


class Customer(Component):
    def __init__(self, id: int):
        self.id = id


class Queue:
    def __init__(self):
        self.elements: List[Customer] = []

    def put(self, customer: Customer):
        self.elements.append(customer)

    def get(self) -> Optional[Customer]:
        if len(self.elements) > 0:
            return self.elements.pop(0)
        else:
            return None

    def size(self) -> int:
        return len(self.elements)


class Generator(Component):
    def __init__(self, sim: Simulator, queue: Queue):
        self.sim = sim
        self.queue = queue
        self.count = count()

    def main(self):
        customer = Customer(next(self.count))
        print(f"{self.sim.now():.2f} - {customer} arrived")
        self.queue.put(customer)
        delay = random.expovariate(lambd=8.0)
        self.sim.sleep(delay)
        self.sim.schedule(self)


class Server(Component):
    def __init__(self, sim: Simulator, queue: Queue):
        self.sim = sim
        self.queue = queue
        self.current_customer: Optional[Customer] = None

    def main(self):
        if self.current_customer:
            print(f"{self.sim.now():.2f} - Finished serving {self.current_customer}")
        self.current_customer = None
        if self.queue.size() > 0:
            customer = self.queue.get()
            self.serve_customer(sim, customer)

    def serve_customer(self, sim: Simulator, customer: Customer):
        self.current_customer = customer
        print(f"{self.sim.now():.2f} - Started serving {self.current_customer}")
        service_time = random.expovariate(1.0)
        self.sim.sleep(service_time)
        self.sim.schedule(self)

    def is_available(self) -> bool:
        return self.current_customer == None


if __name__ == "__main__":
    sim = Simulator()
    queue = Queue()
    generator = Generator(sim, queue)
    server = Server(sim, queue)
    sim.schedule(generator)
    sim.schedule(server)
    sim.run(until=10)
