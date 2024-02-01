from dataclasses import dataclass, asdict
from heapq import heappush, heappop
from typing import Any, AnyStr, Callable, List, Optional, Tuple
from greenlet import greenlet


class MetaComponent(type):
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


class Component(metaclass=MetaComponent):
    """Base class for components in the simulation."""

    def main(self):
        """Main method to be implemented by subclasses."""
        pass


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
        self._values: List[Record] = []

    def record(self, component: Component, description: str, value: Any):
        """Record a simulation event.

        Args:
            component (Component): The component associated with the event.
            description (str): Description of the event.
            value (Any): Value associated with the event.
        """
        rec = Record(
            time=self._sim.now(),
            component=component.__name__,
            description=description,
            value=value,
        )
        if self._trace:
            self._display(rec)

        self._values.append(rec)

    def values(self) -> List[Record]:
        """Get recorded simulation events."""
        return self._values

    def _display(self, rec):
        """Display a recorded event."""
        if len(self._values) == 0:
            self._display_header()
        else:
            self._display_record(rec)

    def _display_record(self, rec: Record):
        """Display a single record."""
        desc = (
            rec.description
            if len(rec.description) < 60
            else rec.description[:57] + "..."
        )
        row = [str(e) for e in [rec.time, rec.component, desc, rec.value]]

        self._display_row(row)

    def _display_header(self):
        """Display the header for the table."""
        colsize = [15, 15, 60, 15]
        sep = ["-" * s for s in colsize]
        empty = [" " * s for s in colsize]
        row = ["time", "component", "description", "value"]
        self._display_row(sep)
        self._display_row(row)
        self._display_row(sep)

        self._display_row(empty)

    def _display_row(self, row: List[str]):
        """Display a row of the table."""
        print("| {:<15} | {:<15} | {:<60} | {:<15} |".format(*row))


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
        self._monitor = Monitor(self, trace)
        self._now = initial_time

    def record(self, component: Component, description: str, value: Any):
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

    def activate(self, what: Component, at: float = None, after: float = None):
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
            heappush(self._times, when)

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

    def simulate(self):
        """Start simulation."""
        while True:
            # Is anybody wakeable?
            process = self.__pop()

            # Advance time & retry
            while process == None:
                # Do we still have process waiting for a new time?
                if self._times:
                    self._now = heappop(self._times)
                    process = self.__pop()
                # if not, the simulation is over
                else:
                    return
            # Switch to it
            process.switch()
            # Back to scheduling

    def next(self):
        """Switch to the next awakeable process."""
        greenlet.getcurrent().parent.switch()
