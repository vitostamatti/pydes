def test_import_events():
    from pydes.events import Simulator

    sim = Simulator()
    assert isinstance(sim, Simulator)


def test_import_process():
    from pydes.process import Simulator

    sim = Simulator()
    assert isinstance(sim, Simulator)
