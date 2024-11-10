"""
This is the pydes.process.core module
"""

from heapq import heappush, heappop
from itertools import count
from math import inf
from typing import Any, Callable, Tuple
from greenlet import greenlet
from datetime import datetime, timedelta
from pydes.monitor import Monitor, Record


# ConditionType = Callable[[], bool]
# ProcessType = greenlet
class Simulator:
    """`Simulator` is the central object of Py-DES and is used to model all the process and events of the system.

    Its main objective is to schedule process and events and then execute them in a time-ordered way.

    Args:
        init: The initial simulation time specified as a float or datetime object.
        trace: Indicates whether tracing is enabled or not.

    Simulators can be instantiated either using numeric time (float or int) or datetime time.

    To create a `Simulator` with numeric time units simply ommit the argument or pass a specific
    `until` argument.
    ```python
    sim = Simulator(until=10)
    ```

    If you prefer to use datetime objects, you can pass to the until argument a `datetime` object.

    ```python
    from datetime import datetime
    sim = Simulator(until=datetime.max)
    ```

    Once you created the `Simulator` object you can start modeling your procesess using its differents methods.

    Methods:
        sleep: Sleep for the given duration.
        sleep_until: Sleep until the given simulation time.
        wait_for: Suspends the process until a condition becomes true.
        schedule: Activates a process either immediately (if both `at` and `after` are None) or after a delay.
        run: Starts simulation.
        record: records an event by passing a component a value and optionally a description.
        records: returns a list with all the recors that were saved during the simulation.

    """

    def __init__(self, init: int | float | datetime = 0, trace: bool = True):
        self._conds: list[tuple[greenlet, Callable[[], bool]]] = []
        self._times: list[tuple[int | float | datetime, int]] = []
        self._ctimes = count()
        self._monitor = Monitor(self, trace)
        self._init_time = init
        self._now = init

    def record(self, name: str, value: Any, description: str | None = None):
        """Record a simulation event.

        Args:
            name: The name associated with the event.
            value: Value associated with the event.
            description: Description of the event.
        """
        self._monitor.record(name, value, description)

    def records(self) -> list[Record]:
        """Get recorded simulation events.

        Returns:
            list of `Record` objects
        """
        return self._monitor.values()

    def schedule(
        self,
        func: Callable[[], None],
        at: int | float | datetime | None = None,
        after: int | float | timedelta | None = None,
    ):
        """Schedules a function either immediately (if both `at` and `after` are None) or after a delay.

        Args:
            func: A function to be scheduled and runned during the simulation.
            at: Simulation time to activate the process, default is None.
            after: Delay activation with specified time, default is None.

        ```python
        sim = Simulator(until=10)

        class Process:
            def __init__(self, sim:Simulation):
                self.sim = sim
            def main(self):
                while True:
                    print("this is my process running")
                    self.sim.sleep(10)

        process = Process(sim)
        sim.schedule(proc.main)
        ```

        """

        def main():
            self.sleep_until(at)
            self.sleep(after)
            func()
            self._next()  # switch to another greenlet, or else execution "fall"
            # is resumed from the parent's last switch()

        # Add it to the event-queue and launch it as soon as possible.
        self._schedule(gl=greenlet(main), cond=lambda: True)

    def wait_for(
        self, cond: Callable[[], bool], timeout: int | float | timedelta | None = None
    ):
        """Wait for a condition to become true.

        Suspends this process until the condition becomes true.

        Args:
            cond: Function to test.
            timeout: Maximum simulation time to wait for condition to become true, default is None.
        """
        if timeout is not None:
            time = self._add_to_time(self.now(), timeout)
            self._schedule(cond=lambda: cond() or (self.now() == time), time=time)
        else:
            self._schedule(cond=cond)
        self._next()

    def sleep(self, duration: int | float | timedelta | None = None):
        """Sleep for the given duration.

        Args:
            duration: Duration to sleep for.
        """
        if duration is None:
            return
        time = self._add_to_time(self.now(), duration)
        self.sleep_until(time)

    def _add_to_time(self, t: int | float | datetime, d: int | float | timedelta):
        if isinstance(t, (float, int)) and isinstance(d, (float, int)):
            return t + d
        elif isinstance(t, datetime) and isinstance(d, timedelta):
            return t + d
        else:
            raise TypeError(
                f"time of type {type(t)} and duration of type {type(d)} are not compatible"
            )

    def sleep_until(self, until: int | float | datetime | None = None):
        """Sleep until the given simulation time.

        Args:
            until: Simulation time to sleep until.
        """
        if until is None:
            return

        if until == self.now():
            return

        now = self.now()
        if isinstance(until, float) and isinstance(now, float):
            if until < now:
                raise ValueError("Until time cannot be less than current time")
        elif isinstance(until, datetime) and isinstance(now, datetime):
            if until < now:
                raise ValueError("Until time cannot be less than current time")

        self._schedule(cond=lambda: self.now() == until, time=until)
        self._next()

    def _schedule(
        self,
        gl: greenlet | None = None,
        cond: Callable[[], bool] | None = None,
        time: int | float | datetime | None = None,
    ):
        """Schedules a condition or a time.

        Args:
            gl: Greenlet object, default is None.
            cond: Condition to post, default is None.
            time: Time to schedule the condition, default is None.
        """
        if gl is None:
            gl = greenlet.getcurrent()
        if cond:
            self._conds.append((gl, cond))
        if time:
            heappush(self._times, (time, next(self._ctimes)))

    def now(self) -> float | datetime:
        """Return current simulation time.

        Returns:
            current time expressed as float or datetime depending on the initial simulation time.
        """
        return self._now

    def _pop(self) -> greenlet | None:
        """Pops out a process which may run *now*.

        Returns:
            greenlet or None: A greenlet object or None if no process can run now.
        """
        for process, cond in self._conds:
            if cond():
                self._conds.remove((process, cond))
                return process
        return None

    def run(self, until: int | float | datetime = inf):
        """Start simulation.

        Args:
            until: maximum simulation time expressed as datetime or float.
        """
        while True:
            # Is anybody wakeable?
            process = self._pop()

            # Advance time & retry
            while process is None:
                # if we reached the max running time we return and end simulation
                if (
                    isinstance(self._now, (float, int))
                    and isinstance(until, (float, int))
                    and self._now >= until
                ):
                    return
                elif (
                    isinstance(self._now, datetime)
                    and isinstance(until, datetime)
                    and self._now >= until
                ):
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

    def _next(self):
        """Switch to the next awakeable process."""
        greenlet.getcurrent().parent.switch()  # type: ignore
