from pytest import fixture
from pydes import Simulator, State, Event, Store, Container, Queue, Resource


@fixture
def sim():
    return Simulator()


def test_state(sim: Simulator):
    class A:
        def __init__(self, sim: Simulator, state: State):
            self.sim = sim
            self.state = state

        def main(self):
            self.state.wait(1)

    class B:
        def __init__(self, sim: Simulator, state: State):
            self.sim = sim
            self.state = state

        def main(self):
            self.sim.sleep(10)
            self.state.set(1)

    c = State(sim, 0)
    a = A(sim, c)
    b = B(sim, c)
    sim.schedule(a)
    sim.schedule(b)
    sim.run()
    assert sim.now() == 10
    assert c._value == 1


def test_store(sim: Simulator):
    class A:
        def __init__(self, sim: Simulator, store: Store):
            self.sim = sim
            self.store = store
            self.stored = None

        def main(self):
            self.stored = self.store.get()

    class B:
        def __init__(self, sim: Simulator, store: Store):
            self.sim = sim
            self.store = store

        def main(self):
            self.sim.sleep(10)
            self.store.put("something")

    c = Store(sim)
    a = A(sim, c)
    b = B(sim, c)
    sim.schedule(a)
    sim.schedule(b)
    sim.run()
    assert sim.now() == 10
    assert len(c._items) == 0
    assert c.level() == 0
    assert a.stored == "something"


def test_event(sim: Simulator):
    class A:
        def __init__(self, sim: Simulator, event: Event):
            self.sim = sim
            self.event = event

        def main(self):
            self.event.wait()

    class B:
        def __init__(self, sim: Simulator, event: Event):
            self.sim = sim
            self.event = event

        def main(self):
            self.sim.sleep(10)
            self.event.set()

    c = Event(sim)
    a = A(sim, c)
    b = B(sim, c)
    sim.schedule(a)
    sim.schedule(b)
    sim.run()
    assert sim.now() == 10
    assert c._value is True


def test_container(sim: Simulator):
    class A:
        def __init__(self, sim: Simulator, container: Container):
            self.sim = sim
            self.container = container

        def main(self):
            self.container.get(5)

    class B:
        def __init__(self, sim: Simulator, container: Container):
            self.sim = sim
            self.container = container

        def main(self):
            self.sim.sleep(10)
            self.container.put(10)

    c = Container(sim)
    a = A(sim, c)
    b = B(sim, c)
    sim.schedule(a)
    sim.schedule(b)
    sim.run()
    assert sim.now() == 10
    assert c.level() == 5


def test_queue(sim: Simulator):
    class A:
        def __init__(self, sim: Simulator, queue: Queue):
            self.sim = sim
            self.queue = queue
            self.stored = None

        def main(self):
            self.stored = self.queue.get()

    class B:
        def __init__(self, sim: Simulator, queue: Queue):
            self.sim = sim
            self.queue = queue

        def main(self):
            self.sim.sleep(10)
            self.queue.put("something")

    c = Queue(sim)
    a = A(sim, c)
    b = B(sim, c)
    sim.schedule(a)
    sim.schedule(b)
    sim.run()
    assert sim.now() == 10
    assert len(c._waiters) == 0
    assert c.size() == 0
    assert a.stored == "something"


def test_resource(sim: Simulator):
    class A:
        def __init__(self, sim: Simulator, resource: Resource):
            self.sim = sim
            self.resource = resource

        def main(self):
            self.resource.request(self)
            self.sim.sleep(10)
            self.resource.release(self)

    class B:
        def __init__(self, sim: Simulator, resource: Resource):
            self.sim = sim
            self.resource = resource

        def main(self):
            self.sim.sleep(5)
            self.resource.request(self)
            # self.sim.sleep(10)
            # self.resource.release(self)

    c = Resource(sim)
    a = A(sim, c)
    b = B(sim, c)
    sim.schedule(a)
    sim.schedule(b)
    sim.run()
    assert sim.now() == 10
    assert c.usage() == 1
