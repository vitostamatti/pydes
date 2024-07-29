from math import inf
from typing import Any
from pydes.core import Simulator


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

    Components are just an utility base class that tracks how many
    instances of itself are created. Its `id` property will be unique
    during the simulation.

    This property is usefull to identify different components in the simulation
    without having to set an explicit name for them, however is not a requirement
    for the `Simulation` to run.

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
    sim.schedule(process.main)

    # now you can run the simulation
    sim.run()
    ```
    """

    def __str__(self):
        return self.__name__

    @property
    def id(self):
        return self.__name__


class Event(Component):
    """An event can be waited and set by components. They are very useful to model
    trigger conditions and model interaction between different actors across the system.

    Args:
        sim: The simulator instance.

    Methods:
        wait: a component can call the `wait` method and suspend its excecution until this event is set.
        set: a component can call the `set` method and trigger the event. This causes all the waiting
            components to continue its excecution.
    """

    def __init__(self, sim: Simulator):
        self._sim = sim
        self._value = False

    def set(self):
        """Set the event."""
        self._value = True
        # self._sim.wait_for(cond=lambda: self._value)

    def wait(self):
        """Wait for the event to be set."""
        self._sim.wait_for(cond=lambda: self._value)


class State(Component):
    """Represents a state in the simulation. It is highly recommended to use Enums
    to control the possible values that a State object can take.

    Args:
        sim (Simulator): The simulator instance.
        value (Any): The initial value of the state.

    Methods:
        set: changes the state to a new provided value
        wait: waits until a certain value is set in the State.
    """

    def __init__(self, sim: Simulator, value: Any):
        self._sim = sim
        self._value = value

    def set(self, value: Any):
        """Set the state to a new value.

        Args:
            value (Any): The new value of the state.
        """
        self._value = value

    def wait(self, value: Any):
        """Wait for the state to become a specific value.

        Args:
            value (Any): The value to wait for.
        """
        self._sim.wait_for(cond=lambda: self._value == value)


class Queue(Component):
    """Queues are used to acumulate objects in a buffer and retrieved them from it.

    Args:
        sim: The simulator instance.
        capacity: The maximun lenght of the queue.

    Methods:
        put: tries to insert a new member into the queue and waits if the queue is full.
        get: tries to get one member from the queue and waits if the queue is empty.
    """

    def __init__(self, sim: Simulator, capacity: float | int = inf):
        """Constructor for Queue class.

        Args:
            sim (Simulator): The simulator instance.
        """
        self._sim = sim
        self._waiters = []
        self._capacity = capacity

    def get(self) -> Any:
        """Get an item from the queue.

        Waits until there is an item available in the queue.

        Returns:
            Any: The item retrieved from the queue.
        """
        self._sim.wait_for(cond=lambda: self.size() > 0)
        return self._waiters.pop(0)

    def put(self, member: Any):
        """Put an item into the queue or waits if the queue is full.

        Args:
            member (Any): The item to be put into the queue.
        """
        self._sim.wait_for(cond=lambda: self.size() < self._capacity)
        self._waiters.append(member)

    def size(self) -> int:
        """Get the size of the queue. Its equivalent to the number of
        member inside.

        Returns:
            int: The number of items in the queue.
        """
        return len(self._waiters)


class Resource(Component):
    """Resources can be requested and released by components and therefore are really
    useful in modeling real world scenarios quere components must be shared among different processess.

    Args:
        sim: The simulator instance.
        capacity: The capacity of the resource, default is 1.

    Methods:
        request: tries to get the ownership of this `Resource` and waits if the resource is not avialable.
        release: gives back the ownership of the `Resource` so that other user can make use of it.
    """

    def __init__(self, sim: Simulator, capacity: int = 1) -> None:
        self._sim = sim
        self._capacity = capacity
        self._users = []

    def request(self, by: Component):
        """Request the resource.

        If the resource is idle, the component can acquire it. Otherwise, it waits until the resource becomes idle.

        Args:
            by: The component requesting the resource.
        """
        if self.is_idle():
            self._users.append(by)
            # self._sim.wait_for(lambda: True)
        else:
            self._sim.wait_for(lambda: self.is_idle())
            self._users.append(by)

    def release(self, by: Component):
        """Release the resource.

        Args:
            by: The component releasing the resource.

        Raises:
            PydesError: If the component has not previously requested the resource.
        """
        if by in self._users:
            self._users.remove(by)
            # self._sim.wait_for(lambda: True)
        else:
            raise ValueError(
                f"{by} cannot release {self} because it has not been requested"
            )

    def usage(self) -> int:
        """Get the current usage of the resource."""
        return len(self._users)

    def capacity(self) -> int:
        """Get the capacity of the resource."""
        return self._capacity

    def is_idle(self) -> bool:
        """Check if the resource is idle."""
        return self.usage() < self.capacity()


class Container(Component):
    """Containers have the capability to acumulate and provide continuous
    amounts of what contains. It is particularly useful to model non discrete
    accumulators like Tanks.

    Args:
        sim: The simulator instance.
        capacity: The capacity of the container, default is 1.

    Methods:
        get: decrease the level of the container by some amount.
        put: increase the level of the container by some amount.
    """

    def __init__(self, sim: Simulator, capacity: int | float = inf) -> None:
        self._sim = sim
        self._capacity = capacity
        self._level = 0

    def get(self, amount: int | float = 1):
        """Get some amount from the container.

        Args:
            amount: The amount to get from the container, default is 1.
        """
        self._sim.wait_for(lambda: self._can_get(amount))
        self._level -= amount

    def put(self, amount: int | float = 1):
        """Put some amount into the container.

        Args:
            amount: The amount to put into the container, default is 1.
        """
        self._sim.wait_for(lambda: self._can_put(amount))
        self._level += amount

    def level(self) -> int:
        """Get the current level of the container."""
        return self._level

    def capacity(self) -> int | float:
        """Get the capacity of the container."""
        return self._capacity

    def _can_get(self, amount: int | float) -> bool:
        """Check if it's possible to get a certain amount from the container."""
        return self.level() - amount >= 0

    def _can_put(self, amount: int | float) -> bool:
        """Check if it's possible to put a certain amount into the container."""
        return self.level() + amount <= self.capacity()


class Store(Component):
    """Stores are useful to save and retrieve objects. Stores can be use to
    insert any type of object but it requires all the objects to be of the same type.

    Args:
        sim: The simulator instance.
        capacity: The capacity of the store, default is infinity.
    """

    def __init__(self, sim: Simulator, capacity: int = 1):
        self._sim = sim
        self._capacity = capacity
        self._items = []

    def get(self) -> Any:
        """Get an item from the store."""
        self._sim.wait_for(lambda: self._can_get())
        return self._items.pop(0)

    def put(self, item: Any):
        """Put an item into the store.

        Args:
            item: The item to put into the store.
        """
        self._sim.wait_for(lambda: self._can_put(item))
        self._items.append(item)

    def level(self) -> int:
        """Get the current level of the store."""
        return len(self._items)

    def capacity(self) -> int | float:
        """Get the capacity of the store."""
        return self._capacity

    def _can_get(self) -> bool:
        """Check if it's possible to get an item from the store."""
        return self.level() > 0

    def _can_put(self, item: Any) -> bool:
        """Check if it's possible to put an item into the store."""
        if self.level() == 0:
            return True
        if self.level() + 1 > self.capacity():
            return False
        if type(self._items[0]) == type(item):
            return True
        else:
            raise ValueError(
                f"Item of type {type(item)} cannot be put into store of types {type(self._items[0])}"
            )
