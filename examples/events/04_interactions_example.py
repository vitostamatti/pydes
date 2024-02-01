from enum import Enum
import random
from typing import Optional
from pydes.events import Event, Simulator


class PersonState(Enum):
    SUSCEPTIBLE = 0
    INFECTIOUS = 1
    RECOVERED = 2


class Population:
    def __init__(
        self, mean_infectuous_duration: float, mean_interconcat_interval: float
    ):
        self.mean_infectuous_duration = mean_infectuous_duration
        self.mean_interconcat_interval = mean_interconcat_interval
        self.people = []
        self.state_count = [0 for _ in range(len(PersonState))]

    def insert(self, person: "Person"):
        self.people.append(person)
        self.state_count[person.state.value] += 1

    def sample(self) -> Optional["Person"]:
        if len(self.people) > 0:
            return random.choice(self.people)
        else:
            None

    def display(self):
        for state in PersonState:
            print(f"{str(state.name)}: {self.state_count[state.value]}")


class Person(Event):
    def __init__(self, state: PersonState, population: Population):
        self.state: PersonState = state
        self.next_state: Optional[PersonState] = None
        self.population: Population = population
        self.recovery_time: Optional[float] = None

    def trigger(self, sim: Simulator):
        if self.next_state == PersonState.INFECTIOUS:
            self.make_contact(sim)
            self.schedule(sim)

        self.population.state_count[self.state.value] -= 1
        self.state = self.next_state
        self.population.state_count[self.state.value] += 1
        self.dislpay(sim)

    def make_contact(self, sim: Simulator):
        other = self.population.sample()

        if other.state != PersonState.SUSCEPTIBLE:
            return

        other.recovery_time = random.expovariate(
            self.population.mean_infectuous_duration
        )
        other.schedule(sim)

    def schedule(self, sim: Simulator):
        next_contact_time = random.expovariate(
            self.population.mean_interconcat_interval
        )
        if next_contact_time + sim.now() < self.recovery_time:
            self.next_state = PersonState.INFECTIOUS
            sim.schedule(self, next_contact_time)

        else:
            self.next_state = PersonState.RECOVERED
            sim.schedule(self, self.recovery_time)

    def dislpay(self, sim: Simulator):
        print(f"Time: {sim.now()}")
        self.population.display()
        print("-" * 20)


if __name__ == "__main__":
    sim = Simulator()
    population = Population(10.0, 4.0)

    # healty people
    for n in range(800):
        p = Person(PersonState.SUSCEPTIBLE, population)
        population.insert(p)

    # infected people
    for n in range(100):
        p = Person(PersonState.INFECTIOUS, population)
        p.recovery_time = random.expovariate(population.mean_infectuous_duration)
        population.insert(p)
        p.schedule(sim)

    sim.run(until=10)
