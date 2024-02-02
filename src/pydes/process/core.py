from heapq import heappush, heappop
from itertools import count
from math import inf
from typing import Any, AnyStr, Callable, List, Optional, Tuple
from greenlet import greenlet

from pydes.process.components import Component
from pydes.process.monitor import Monitor, Record


class PydesError(Exception):
    """Custom pydes exception for simulation errors"""

    pass


class Simulator:
    """Implements the simulator's business logic.

    Decides who will run next. Processes post conditions and times they are interested in.

    Args:
        initial_time (float): The initial simulation time.
        trace (bool): Indicates whether tracing is enabled or not.
    """

    def __init__(self, initial_time: float = 0, trace: bool = True):
        self._conds: List[Tuple[greenlet, Callable[[], bool]]] = []
        self._times = []
        self._ctimes = count()
        self._monitor = Monitor(self, trace)
        self._init_time = initial_time
        self._now = initial_time

    def record(
        self, component: Component, description: str, value: Optional[Any] = None
    ):
        """Record a simulation event.

        Args:
            component (Component): The component associated with the event.
            description (str): Description of the event.
            value (Any): Value associated with the event.
        """
        self._monitor.record(component, description, value)

    def records(self) -> List[Record]:
        """Get recorded simulation events."""
        return self._monitor.values()

    def schedule(self, what: Component, at: float = None, after: float = None):
        """Launch a process.

        Activates a process either immediately (if both `at` and `after` are None) or after a delay.

        Args:
            what (Component): A class having a main() method.
            at (float): Simulation time to activate the process, default is None.
            after (float): Delay activation with specified time, default is None.
        """

        def main():
            self.sleep_until(at)
            self.sleep(after)
            what.main()
            self.next()  # switch to another greenlet, or else execution "fall"
            # is resumed from the parent's last switch()

        # Add it to the event-queue and launch it as soon as possible.
        self._schedule(who=greenlet(main), cond=lambda: True)

    def wait_for(self, cond: Callable[[], bool], until=None):
        """Wait for a condition to become true.

        Suspends this process until the condition becomes true.

        Args:
            cond (Callable[[], bool]): Function to test.
            until (float): Maximum simulation time to wait for condition to become true, default is None.
        """
        if until != None:
            if until < self.now():
                raise PydesError(
                    f"{until} cannot be smaller than current time {self.now()}"
                )
            self._schedule(cond=lambda: cond() or (self.now() == until), when=until)
        else:
            self._schedule(cond=cond)
        self.next()

    def sleep(self, duration: Optional[float] = None):
        """Sleep for the given duration.

        Args:
            duration (float): Duration to sleep for.
        """
        if duration == None:
            return
        self.sleep_until(self.now() + duration)

    def sleep_until(self, until: Optional[float] = None):
        """Sleep until the given simulation time.

        Args:
            until (float): Simulation time to sleep until.
        """
        if until == None:
            return
        if until == self.now():
            return

        if until < self.now():
            raise PydesError(
                f"{until} cannot be smaller than current time {self.now()}"
            )
        self._schedule(cond=lambda: self.now() == until, when=until)
        self.next()

    def _schedule(
        self,
        who: Optional[greenlet] = None,
        cond: Optional[Callable[[], bool]] = None,
        when: Optional[float] = None,
    ):
        """Post a condition or a time.

        Args:
            who (greenlet, optional): Greenlet object, default is None.
            cond (Callable[[], bool], optional): Condition to post, default is None.
            when (float, optional): Time to post the condition, default is None.
        """
        if who == None:
            who = greenlet.getcurrent()
        if cond:
            self._conds.append((who, cond))
        if when:
            heappush(self._times, (when, next(self._ctimes)))

    def now(self) -> float:
        """Return current simulation time."""
        return self._now

    def __pop(self) -> Optional[greenlet]:
        """Pops out a process which may run *now*.

        Returns:
            greenlet or None: A greenlet object or None if no process can run now.
        """
        for process, cond in self._conds:
            if cond():
                self._conds.remove((process, cond))
                return process
        return None

    def run(self, until: float = inf):
        """Start simulation."""
        while True:
            # Is anybody wakeable?
            process = self.__pop()

            # Advance time & retry
            while process == None:
                # if we reached the max running time we return and end simulation
                if self._now >= until:
                    return
                # Do we still have process waiting for a new time?
                if self._times:
                    self._now, _ = heappop(self._times)
                    process = self.__pop()
                # if not, the simulation is over
                else:
                    return
            # Switch to it
            process.switch()
            # Back to scheduling

    def reset(self):
        self._conds: List[Tuple[greenlet, Callable[[], bool]]] = []
        self._times = []
        self._monitor.reset()
        self._now = self._init_time

    def next(self):
        """Switch to the next awakeable process."""
        greenlet.getcurrent().parent.switch()
