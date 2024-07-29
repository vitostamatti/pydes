from pydes import Component, Simulator


# --8<-- [start:example-1]
class Process1(Component):
    def __init__(self, sim: Simulator, time: float = 10):
        self.sim = sim
        self.time = time

    def main(self):
        i = 0
        while True:
            self.sim.record(self.id, "running loop")
            i += 1
            self.sim.sleep(self.time)


# --8<-- [end:example-1]


# --8<-- [start:example-2]
class Process2(Component):
    def __init__(self, sim: Simulator, time: float = 10):
        self.sim = sim
        self.time = time

    def main(self):
        i = 0
        self.sim.record(self.id, "running loop")
        i += 1
        self.sim.sleep(self.time)
        self.sim.schedule(self.main)


# --8<-- [end:example-2]


# --8<-- [start:run-example]
print("Process 1")
sim = Simulator()
process1 = Process1(sim, time=10)
sim.schedule(process1.main)
sim.run(30)
print("Process 2")
sim.reset()
process2 = Process2(sim, time=10)
sim.schedule(process2.main)
sim.run(30)
# --8<-- [end:run-example]
