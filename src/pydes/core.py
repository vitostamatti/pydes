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


class Simulator:
    """`Simulator` is the central object of Py-DES and is used to model all the process and events of the system.

    Its main objective is to schedule process and events and then execute them in a time-ordered way.

    Args:
        initial_time: The initial simulation time specified as a float or datetime object.
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

    def __init__(self, initial_time: float | datetime = 0, trace: bool = True):
        self._conds: list[Tuple[greenlet, Callable[[], bool]]] = []
        self._times = []
        self._ctimes = count()
        self._monitor = Monitor(self, trace)
        self._init_time = initial_time
        self._now = initial_time

    def record(
        self, component: "Component", value: Any, description: str | None = None
    ):
        """Record a simulation event.

        Args:
            component: The component associated with the event.
            value: Value associated with the event.
            description: Description of the event.
        """
        self._monitor.record(component, value, description)

    def records(self) -> list[Record]:
        """Get recorded simulation events.

        Returns:
            list of `Record` objects
        """
        return self._monitor.values()

    def schedule(
        self,
        comp: "Component",
        at: float | timedelta | None = None,
        after: float | timedelta | None = None,
    ):
        """Activates a process either immediately (if both `at` and `after` are None) or after a delay.

        Args:
            comp: A class having a main() method.
            at: Simulation time to activate the process, default is None.
            after: Delay activation with specified time, default is None.
        """

        def main():
            self.sleep_until(at)
            self.sleep(after)
            comp.main()
            self._next()  # switch to another greenlet, or else execution "fall"
            # is resumed from the parent's last switch()

        # Add it to the event-queue and launch it as soon as possible.
        self._schedule(gl=greenlet(main), cond=lambda: True)

    def wait_for(self, cond: Callable[[], bool], until: float | timedelta = None):
        """Wait for a condition to become true.

        Suspends this process until the condition becomes true.

        Args:
            cond: Function to test.
            until: Maximum simulation time to wait for condition to become true, default is None.
        """
        if until is not None:
            if until < self.now():
                raise PydesError(
                    f"{until} cannot be smaller than current time {self.now()}"
                )
            self._schedule(cond=lambda: cond() or (self.now() == until), time=until)
        else:
            self._schedule(cond=cond)
        self._next()

    def sleep(self, duration: float | timedelta | None = None):
        """Sleep for the given duration.

        Args:
            duration: Duration to sleep for.
        """
        if duration is None:
            return
        self.sleep_until(self.now() + duration)

    def sleep_until(self, until: float | timedelta | None = None):
        """Sleep until the given simulation time.

        Args:
            until: Simulation time to sleep until.
        """
        if until is None:
            return
        if until == self.now():
            return

        if until < self.now():
            raise PydesError(
                f"{until} cannot be smaller than current time {self.now()}"
            )
        self._schedule(cond=lambda: self.now() == until, time=until)
        self._next()

    def _schedule(
        self,
        gl: greenlet | None = None,
        cond: Callable[[], bool] | None = None,
        time: float | timedelta | None = None,
    ):
        """Schedules a condition or a time.

        Args:
            who: Greenlet object, default is None.
            cond: Condition to post, default is None.
            when: Time to post the condition, default is None.
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

    def run(self, until: float | timedelta = inf):
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

    def _next(self):
        """Switch to the next awakeable process."""
        greenlet.getcurrent().parent.switch()


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
    """
    Base class for components in the simulation.

    All subclasses of `Component` can define a `main` method which is the
    underlying process that this `Component` is going to be excecuting.

    Once the `main` method is defined, this component can be scheduled into the
    simulation using the `schedule` method of `Simulator`

    ```python
    from pydes.process import Component, Simulator

    # define the component with a main method
    class Process(Component):
        def __init__(self, sim: Simulator):
            self.sim = sim

        def main(self):
            for _ in range(10):
                print(self.sim.now(),"waiting")
                self.sim.sleep(2)
                print(self.sim.now(),"waiting")

    # create the simulator object
    sim = Simulator()

    # create an instance of the Component
    process = Process(sim)

    # schedule the process in the simulator
    sim.schedule(process)

    # now you can run the simulation
    sim.run()
    ```
    """

    def main(self):
        """Main method to be implemented by subclasses."""
        pass

    def __str__(self):
        return self.__name__


class PydesError(Exception):
    """Custom pydes exception for simulation errors"""

    pass
