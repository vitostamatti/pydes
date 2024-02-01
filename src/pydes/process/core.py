from dataclasses import dataclass, asdict
from heapq import heappush, heappop
from typing import Any, Callable, List, Tuple
from greenlet import greenlet


class MetaComponent(type):
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
    def main(self):
        pass


@dataclass
class Record:
    time: float
    component: str
    description: str
    value: Any


@dataclass
class MonitorDisplayConfig:
    time_col_size: int
    component_col_size: int
    description_col_size: int
    value_col_size: int


## Stores values which change during simulation
class Monitor:
    ## Constructor
    # @param[in] name Name to associate to this Monitor
    def __init__(self, sim: "Simulator", trace: bool):
        self._sim = sim
        self._trace = trace
        self._values: List[Record] = []

    def record(self, component: Component, description: str, value: Any):
        ## Store the specified value
        # Stores the tuples simulation time, specified value
        rec = Record(
            time=self._sim.now(),
            component=component.__name__,
            description=description,
            value=value,
        )
        if self._trace:
            self._display(rec)

        self._values.append(rec)

    def _display(self, rec):
        if len(self._values) == 0:
            self._display_header()
        else:
            self._display_record(rec)

    def _display_record(self, rec: Record):
        desc = (
            rec.description
            if len(rec.description) < 60
            else rec.description[:57] + "..."
        )
        row = [rec.time, rec.component, desc, rec.value]
        self._print_row(row)

    def _display_header(self):
        row = ["-" * 15, "-" * 15, "-" * 60, "-" * 15]
        self._print_row(row)
        row = ["time", "component", "description", "value"]
        self._print_row(row)
        row = ["-" * 15, "-" * 15, "-" * 60, "-" * 15]
        self._print_row(row)
        row = [" " * 15, " " * 15, " " * 60, " " * 15]
        self._print_row(row)

    def _print_row(self, row: list):
        print("| {:<15} | {:<15} | {:<60} | {:<15} |".format(*row))

    def __iter__(self):
        ## Iterate over the stored values
        # @return iterator of simulation time, value tuples.
        return self._values.__iter__()

    def values(self) -> List[Record]:
        return self._values


class PydesError(Exception):
    pass


class Simulator:
    ## Implements the simulator's "business logic"
    # Decides who will run next. Processes post
    # conditions and times they are interested in.

    def __init__(self, initial_time: float = 0, trace: bool = True):
        ## Constructor
        self._conds: List[Tuple[greenlet, Callable[[], bool]]] = []
        self._times = []
        self._monitor = Monitor(self, trace)
        self._now = initial_time

    def record(self, component: Component, description: str, value: Any):
        self._monitor.record(component, description, value)

    def records(self) -> List[Record]:
        return self._monitor.values()

    def activate(self, what: Component, at: float = None, after: float = None):
        ## Launch a process
        # Activated a process, either immediately (if both at and after are None)
        # or after a delay.
        # @param[in] what A class having a main() method
        # @param[in] at At what simulation time to activate the process or None
        # @param[in] after Delay activation with specified time or None
        def main():
            self.sleep_until(at)
            self.sleep(after)
            what.main()
            self.next()  # switch to another greenlet, or else execution "fall"
            # is resumed from the parent's last switch()

        # Add it to the event-queue and launch it as soon as possible.
        self._schedule(who=greenlet(main), cond=lambda: True)

    def wait_for(self, cond, until=None):
        ## Wait for a condition to become true
        # Suspends this process until the condition becomes true. If until is specified
        # wake the process up at the specified simulation time.
        # @param cond Function to test
        # @param until Maximum simulation time to wait for condition to become true
        if until != None:
            if until < self.now():
                raise PydesError(
                    f"{until} cannot be smaller than current time {self.now()}"
                )
            self._schedule(cond=lambda: cond() or (self.now() == until), when=until)
        else:
            self._schedule(cond=cond)
        self.next()

    def sleep(self, duration):
        ## Sleeps a for the given duration
        if duration == None:
            return
        self.sleep_until(self.now() + duration)

    def sleep_until(self, until):
        ## Sleeps until the given simulation time
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
        self, who: greenlet = None, cond: Callable[[], bool] = None, when: float = None
    ):
        ## Post a condition or a time
        if who == None:
            who = greenlet.getcurrent()
        if cond:
            self._conds.append((who, cond))
        if when:
            heappush(self._times, when)

    def now(self):
        ## Returns current simulation time
        return self._now

    def __pop(self) -> greenlet:
        """
        Pops out a process which may run *now*.
        Returns None if no process can run now.
        """
        for process, cond in self._conds:
            if cond():
                self._conds.remove((process, cond))
                return process
        return None

    def simulate(self):
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

    ## Switched to the next awakeable process
    def next(self):
        greenlet.getcurrent().parent.switch()
