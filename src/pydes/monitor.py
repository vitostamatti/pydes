from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydes.core import Simulator


@dataclass
class Record:
    """Stores information about a simulation event.

    Args:
        time (float | datetime): simulation time.
        name (str): The name of the record.
        value (Any): the event value to record
        description (str|None): optional description of the recorded event
    """

    time: float | int | datetime
    name: str
    value: Any
    description: str | None


class Monitor:
    """
    The `Monitor` is simply a convenient class to record different events or moments
    during the simulation. Simulation without data analytics is useless.

    The `Monitor` is used internally by the `Simulator` and is not ment to be used outside this context.

    To record an event you simply have to call the `record` method o the simulator and pass 2 required
    parameters and optionally a third one.

    ```python
    from pydes.process import Component, Simulator

    class Process(Component):
        def __init__(self, sim: Simulator):
            self.sim = sim

        def main(self):
            for _ in range(10):
                self.sim.record(self,"start waiting")
                self.sim.sleep(2)
                self.sim.record(self,"end waiting","this is an aditional description")
    ```

    When the simulation runs, you'll see all you recorded events printed out. Besides, these records
    can be retreived for further analysis using the `records` from the `Simulator`.

    To turn off the printing of the records during simulation, you can pass 'trace=False' to the `Simulator`
    constructor.

    Args:
        sim: The simulator instance.
        trace: Indicates whether tracing is enabled or not.
    """

    def __init__(self, sim: "Simulator", trace: bool):
        self._sim = sim
        self._trace = trace
        self._values: list[Record] = []

    def reset(self):
        self._values = []

    def record(
        self,
        name: str,
        value: Any,
        description: str | None,
    ):
        """Record a simulation event.

        Args:
            name: The name associated with the event.
            value: Value associated with the event.
            description: Description of the event.
        """
        rec = Record(
            time=self._sim.now(),
            name=name,
            value=value,
            description=description,
        )
        if self._trace:
            self._display(rec)

        self._values.append(rec)

    def values(self) -> list[Record]:
        """Get recorded simulation events.

        Returns:
            list of `Record` objects.
        """
        return self._values

    def _display(self, rec):
        """Display a recorded event."""
        if len(self._values) == 0:
            self._display_header()
        self._display_record(rec)

    def _display_record(self, rec: Record):
        """Display a single record."""
        if rec.description:
            desc = (
                rec.description
                if len(rec.description) < 30
                else rec.description[:27] + "..."
            )
        else:
            desc = None
        row = [str(e) for e in [rec.time, rec.name, rec.value, desc]]

        self._display_row(row)

    def _display_header(self):
        """Display the header for the table."""
        colsize = [30, 15, 40, 30]
        sep = ["-" * s for s in colsize]
        empty = [" " * s for s in colsize]
        row = ["time", "component", "value", "description"]
        self._display_row(sep)
        self._display_row(row)
        self._display_row(sep)
        self._display_row(empty)

    def _display_row(self, row: list[str]):
        """Display a row of the table."""
        print("| {:<30} | {:<15} | {:<40} | {:<30} |".format(*row))
