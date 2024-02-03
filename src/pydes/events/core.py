from math import inf
from abc import ABC, abstractmethod
from heapq import heappush, heappop
from itertools import count
from typing import List, Optional, Tuple


class Event(ABC):
    """Abstract base class for events in the simulation."""

    @abstractmethod
    def trigger(self, sim: "Simulator"):
        """Method to trigger the event.

        Args:
            sim (Simulator): The simulator instance.
        """
        pass


class Simulator:
    """Simulator class for discrete event simulation.
    Args:
        init_time (Optional[float]): Initial simulation time, default is 0.0.
    """

    def __init__(self, init_time: Optional[float] = 0.0):
        self._now = init_time
        self._events: List[Tuple[float, int, Event]] = []
        self._ecount = count()

    def now(self) -> float:
        """Get the current simulation time."""
        return self._now

    def schedule(self, event: Event, delay: float = 0, priority: int = 0):
        """Schedule an event to be triggered after a delay.

        Args:
            event (Event): The event to be scheduled.
            delay (float): The delay after which the event should be triggered, default is 0.
            priority (int): The priority of the event, default is 0.
        """
        heappush(self._events, (self._now + delay, priority, next(self._ecount), event))

    def __next(self) -> Event:
        """Get the next event to be triggered."""
        self._now, _, _, event = heappop(self._events)
        return event

    def run(self, until: float = inf):
        """Run the simulation until the given time.

        Args:
            until (float): The time until which to run the simulation, default is infinity.
        """
        while len(self._events) > 0 and self._now < until:
            event = self.__next()
            event.trigger(self)
