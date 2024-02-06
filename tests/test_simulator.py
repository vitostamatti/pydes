from pydes import Simulator
from datetime import datetime
from pytest import fixture
from greenlet import greenlet

from pydes.core import Component


@fixture
def sim():
    return Simulator()


def test_init_no_args():
    sim = Simulator()
    assert isinstance(sim, Simulator)


def test_init_with_float():
    sim = Simulator(10)
    assert isinstance(sim, Simulator)
    assert sim.now() == 10


def test_init_with_datetime():
    sim = Simulator(datetime.max)
    assert isinstance(sim, Simulator)
    assert sim.now() == datetime.max


def test_init_without_trate():
    sim = Simulator(trace=False)
    assert isinstance(sim, Simulator)
    assert sim._monitor._trace is False


def test__schedule_with_gl_and_cond(sim: Simulator):
    gl = greenlet(run=lambda: True)

    def cond():
        return True

    sim._schedule(gl=gl, cond=cond)
    gl_, cond_ = sim._conds.pop()
    assert gl == gl_
    assert cond == cond_


def test__schedule_without_gl_but_with_cond(sim: Simulator):
    gl = greenlet.getcurrent()  # main process

    def cond():
        return True

    # if no gl is provided then we assign the current one
    # in this case, the current one is going to be main
    sim._schedule(cond=cond)
    gl_, cond_ = sim._conds.pop()
    assert gl_ == gl
    assert cond == cond_


def test__schedule_with_gl_cond_and_time(sim: Simulator):
    gl = greenlet(run=lambda: True)

    def cond():
        return True

    sim._schedule(gl=gl, cond=cond, time=10)
    gl_, cond_ = sim._conds.pop()
    time_, ctime_ = sim._times.pop()
    assert gl == gl_
    assert cond == cond_
    assert time_ == 10
    assert ctime_ == 0


def test_schedule_after(sim: Simulator):
    c = Component()
    sim.schedule(c, 0, 10)
    sim.run()
    assert sim.now() == 10


def test_schedule_at(sim: Simulator):
    c = Component()
    sim.schedule(c, 10, 0)
    sim.run()
    assert sim.now() == 10


def test_sleep(sim: Simulator):

    class C(Component):
        def __init__(self, sim: Simulator):
            self.sim = sim

        def main(self):
            self.sim.sleep(10)

    sim.schedule(C(sim))
    sim.run()
    assert sim.now() == 10


def test_sleep_until(sim: Simulator):

    class A(Component):
        def __init__(self, sim: Simulator):
            self.sim = sim

        def main(self):
            self.sim.sleep_until(10)

    sim.schedule(A(sim))
    sim.run()
    assert sim.now() == 10


def test_wait_for(sim: Simulator):

    class A(Component):
        def __init__(self, sim: Simulator, flag):
            self.sim = sim
            self.flag = flag

        def main(self):
            self.sim.wait_for(cond=lambda: self.flag.value)

    class B(Component):
        def __init__(self, sim: Simulator, flag):
            self.sim = sim
            self.flag = flag

        def main(self):
            self.sim.sleep(10)
            self.flag.value = True

    class Flag:
        value = False

    flag = Flag()
    a = A(sim, flag)
    b = B(sim, flag)
    sim.schedule(a)
    sim.schedule(b)
    sim.run()
    assert sim.now() == 10
    assert a.flag.value is True
    assert b.flag.value is True


def test_wait_for_until(sim: Simulator):

    class A(Component):
        def __init__(self, sim: Simulator, flag):
            self.sim = sim
            self.flag = flag
            self.time = sim.now()

        def main(self):
            self.sim.wait_for(cond=lambda: self.flag.value, until=5)
            self.time = sim.now()

    class B(Component):
        def __init__(self, sim: Simulator, flag):
            self.sim = sim
            self.flag = flag

        def main(self):
            self.sim.sleep(10)
            self.flag.value = True
            self.time = sim.now()

    class Flag:
        value = False

    flag = Flag()
    a = A(sim, flag)
    b = B(sim, flag)
    sim.schedule(a)
    sim.schedule(b)
    sim.run()
    assert sim.now() == 10
    assert a.flag.value is True
    assert b.flag.value is True
    assert a.time == 5
    assert b.time == 10
