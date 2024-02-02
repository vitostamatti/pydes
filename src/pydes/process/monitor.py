from dataclasses import dataclass
from typing import Any, List

from pydes.process.components import Component
from pydes.process.core import Simulator


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

    def __init__(self, sim: Simulator, trace: bool):
        self._sim = sim
        self._trace = trace
        self._values: List[Record] = []

    def reset(self):
        self._values = []

    def record(self, component: Component, description: str, value: Any | None = None):
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

    def values(self) -> List[Record]:
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
