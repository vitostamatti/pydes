from importlib.metadata import version

__version__ = version("py-des-lib")

from pydes.core import Simulator, PydesError, Component
from pydes.monitor import Monitor, Record

from pydes.components import (
    Container,
    Queue,
    Resource,
    State,
    Event,
    Store,
)

__all__ = [
    "Simulator",
    "PydesError",
    "Monitor",
    "Record",
    "Component",
    "Container",
    "Queue",
    "Event",
    "State",
    "Resource",
    "Store",
]
