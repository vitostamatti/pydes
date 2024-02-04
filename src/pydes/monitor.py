from dataclasses import dataclass
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydes.core import Component, Simulator


@dataclass
class Record:
    """Stores information about a simulation event."""

    time: float
    component: str
    value: Any
    description: str | None


class Monitor:
    """Stores values which change during simulation.

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
        component: "Component",
        value: Any,
        description: str | None,
    ):
        """Record a simulation event.

        Args:
            component: The component associated with the event.
            value: Value associated with the event.
            description: Description of the event.
        """
        rec = Record(
            time=self._sim.now(),
            component=str(component),
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
        row = [str(e) for e in [rec.time, rec.component, rec.value, desc]]

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
