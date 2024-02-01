from dataclasses import dataclass
from itertools import count
from typing import List, Optional
from pydes.events import AbstractEvent, Simulator
import random


@dataclass
class Customer:
    id: int


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


class Generator(AbstractEvent):
    def __init__(self, queue: Queue):
        self.queue = queue
        self.count = count()

    def trigger(self, sim: Simulator):
        customer = Customer(next(self.count))
        print(f"{sim.now():.2f} - {customer} arrived")
        self.queue.put(customer)
        delay = random.expovariate(lambd=8.0)
        sim.schedule(self, delay)


class Server(AbstractEvent):
    def __init__(self, queue: Queue):
        self.queue = queue
        self.current_customer: Optional[Customer] = None

    def trigger(self, sim: Simulator):
        if self.current_customer:
            print(f"{sim.now():.2f} - Finished serving {self.current_customer}")
        self.current_customer = None
        if self.queue.size() > 0:
            customer = self.queue.get()
            self.serve_customer(sim, customer)

    def serve_customer(self, sim: Simulator, customer: Customer):
        self.current_customer = customer
        print(f"{sim.now():.2f} - Started serving {self.current_customer}")
        service_time = random.expovariate(1.0)
        sim.schedule(self, service_time)

    def is_available(self) -> bool:
        return self.current_customer == None


if __name__ == "__main__":
    queue = Queue()
    generator = Generator(queue)
    server = Server(queue)
    sim = Simulator(0.0)
    sim.schedule(generator)
    sim.schedule(server)
    sim.run(until=10)
