from pydes import Simulator
from datetime import datetime
from pytest import fixture
from greenlet import greenlet


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
