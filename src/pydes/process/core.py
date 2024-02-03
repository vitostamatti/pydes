"""
This is the pydes.process.core module
"""

from heapq import heappush, heappop
from itertools import count
from math import inf
from typing import Any, Callable, Optional, Tuple, Union
from greenlet import greenlet
from dataclasses import dataclass

from datetime import datetime, timedelta


class Simulator:
    """Implements the simulator's business logic.

    Decides who will run next. Processes post conditions and times they are interested in.

    Args:
        initial_time: The initial simulation time specified as a float or datetime object.
        trace: Indicates whether tracing is enabled or not.
    """

    def __init__(self, initial_time: float | datetime = 0, trace: bool = True):
        self._conds: list[Tuple[greenlet, Callable[[], bool]]] = []
        self._times = []
        self._ctimes = count()
        self._monitor = Monitor(self, trace)
        self._init_time = initial_time
        self._now = initial_time

    def record(
        self, component: "Component", description: str, value: Any | None = None
    ):
        """Record a simulation event.

        Args:
            component: The component associated with the event.
            description: Description of the event.
            value: Value associated with the event.
        """
        self._monitor.record(component, description, value)

    def records(self) -> list["Record"]:
        """Get recorded simulation events."""
        return self._monitor.values()

    def schedule(
        self,
        what: "Component",
        at: float | timedelta | None = None,
        after: float | timedelta | None = None,
    ):
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

    def wait_for(self, cond: Callable[[], bool], until: float | timedelta = None):
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

    def sleep(self, duration: float | timedelta | None = None):
        """Sleep for the given duration.

        Args:
            duration (float): Duration to sleep for.
        """
        if duration == None:
            return
        self.sleep_until(self.now() + duration)

    def sleep_until(self, until: float | timedelta | None = None):
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
        when: float | timedelta | None = None,
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

    def now(self) -> float | datetime:
        """Return current simulation time."""
        return self._now

    def _pop(self) -> Optional[greenlet]:
        """Pops out a process which may run *now*.

        Returns:
            greenlet or None: A greenlet object or None if no process can run now.
        """
        for process, cond in self._conds:
            if cond():
                self._conds.remove((process, cond))
                return process
        return None

    def run(self, until: float | timedelta = None):
        """Start simulation."""
        if isinstance(self._now, float):
            until = inf
        if isinstance(self._now, datetime):
            until = datetime.max
        while True:
            # Is anybody wakeable?
            process = self._pop()

            # Advance time & retry
            while process == None:
                # if we reached the max running time we return and end simulation
                if self._now >= until:
                    return
                # Do we still have process waiting for a new time?
                if self._times:
                    self._now, _ = heappop(self._times)
                    process = self._pop()
                # if not, the simulation is over
                else:
                    return
            # Switch to it
            process.switch()
            # Back to scheduling

    def reset(self):
        self._conds: list[Tuple[greenlet, Callable[[], bool]]] = []
        self._times = []
        self._monitor.reset()
        self._now = self._init_time

    def next(self):
        """Switch to the next awakeable process."""
        greenlet.getcurrent().parent.switch()

    # def _check_time_type(self, time: float | timedelta):
    # if type(self._now) != type(time):
    # raise PydesError("Simulation time ")
    # isinstance(self._now, datetime) and isinstance(time, timedelta)


@dataclass
class Record:
    """Stores information about a simulation event."""

    time: float
    component: str
    description: str
    value: Any


class Monitor:
    """Stores values which change during simulation.

    Args:
        sim (Simulator): The simulator instance.
        trace (bool): Indicates whether tracing is enabled or not.
    """

    def __init__(self, sim: "Simulator", trace: bool):
        self._sim = sim
        self._trace = trace
        self._values: list[Record] = []

    def reset(self):
        self._values = []

    def record(
        self, component: "Component", description: str, value: Any | None = None
    ):
        """Record a simulation event.

        Args:
            component (Component): The component associated with the event.
            description (str): Description of the event.
            value (Any): Value associated with the event.
        """
        rec = Record(
            time=self._sim.now(),
            component=str(component),
            description=description,
            value=value,
        )
        if self._trace:
            self._display(rec)

        self._values.append(rec)

    def values(self) -> list[Record]:
        """Get recorded simulation events."""
        return self._values

    def _display(self, rec):
        """Display a recorded event."""
        if len(self._values) == 0:
            self._display_header()
        self._display_record(rec)

    def _display_record(self, rec: Record):
        """Display a single record."""
        desc = (
            rec.description
            if len(rec.description) < 40
            else rec.description[:37] + "..."
        )
        row = [str(e) for e in [rec.time, rec.component, desc, rec.value]]

        self._display_row(row)

    def _display_header(self):
        """Display the header for the table."""
        colsize = [30, 15, 40, 15]
        sep = ["-" * s for s in colsize]
        empty = [" " * s for s in colsize]
        row = ["time", "component", "description", "value"]
        self._display_row(sep)
        self._display_row(row)
        self._display_row(sep)
        self._display_row(empty)

    def _display_row(self, row: list[str]):
        """Display a row of the table."""
        print("| {:<30} | {:<15} | {:<40} | {:<15} |".format(*row))


class _MetaComponent(type):
    """Metaclass used to track the number of instances of every component subclass."""

    __component_instance_count = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__component_instance_count:
            cls.__component_instance_count[cls] = 0
        else:
            cls.__component_instance_count[cls] += 1

        instance = super().__call__(*args, **kwargs)

        instance.__name__ = f"{cls.__name__}.{cls.__component_instance_count[cls]}"

        return instance


class Component(metaclass=_MetaComponent):
    """Base class for components in the simulation."""

    def main(self):
        """Main method to be implemented by subclasses."""
        pass

    def __str__(self):
        return self.__name__


class PydesError(Exception):
    """Custom pydes exception for simulation errors"""

    pass
