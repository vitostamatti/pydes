from importlib.metadata import version

__version__ = version("py-des-lib")

from pydes.core import Simulator
from pydes.monitor import Monitor, Record

from pydes.components import (
    Component,
    Container,
    Queue,
    Resource,
    State,
    Event,
    Store,
)

__all__ = [
    "Simulator",
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
