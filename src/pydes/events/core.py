from enum import Enum
from math import inf
from abc import ABC, abstractmethod
from heapq import heappush, heappop
from itertools import count
from typing import List, Optional, Tuple


class AbstractEvent(ABC):
    @abstractmethod
    def trigger(self, sim: "AbstractSimulator"):
        pass


class AbstractSimulator(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def schedule(self, event: AbstractEvent, delay: float):
        pass


class Simulator(AbstractSimulator):
    def __init__(self, init_time: Optional[float] = 0.0):
        self._now = init_time
        self._events: List[Tuple[float, int, AbstractEvent]] = []
        self._ecount = count()

    def now(self) -> float:
        return self._now

    def schedule(self, event: AbstractEvent, delay: float = 0):
        heappush(self._events, (self._now + delay, next(self._ecount), event))

    def __next(self) -> AbstractEvent:
        self._now, _, event = heappop(self._events)
        return event

    def run(self, until: float = inf):
        while len(self._events) > 0 and self._now < until:
            event = self.__next()
            event.trigger(self)
