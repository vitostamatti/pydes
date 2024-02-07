from pydes import Monitor, Simulator, Component, Record
from pytest import fixture


@fixture
def sim():
    return Simulator()


def test_monitor(sim: Simulator):
    m = Monitor(sim, trace=False)
    c = Component()
    m.record(c, 1, "desc")
    assert m.values() == [Record(0, c, 1, "desc")]


def test_monitor_trace(capsys):
    sim = Simulator()
    m = Monitor(sim, trace=True)
    c = Component()
    m.record(c, 1, "desc")
    stdout = capsys.readouterr()
    rows = stdout.out.split("\n")
    colsize = [30, 15, 40, 30]
    sep = ["-" * s for s in colsize]
    empty = [" " * s for s in colsize]
    header = ["time", "component", "value", "description"]
    fmt = "| {:<30} | {:<15} | {:<40} | {:<30} |"

    row = [0, "Component.1", 1, "desc"]
    assert rows[0] == fmt.format(*sep)
    assert rows[1] == fmt.format(*header)
    assert rows[2] == fmt.format(*sep)
    assert rows[3] == fmt.format(*empty)
    assert rows[4] == fmt.format(*row)
