# Discrete Event Simulation in Python with Py-DES

In this section we’ll explore the Py-DES basic objects and its main capabilities.

## Setup

Easiest way to setup Py-DES is to install it using `pip` with the following command.

```bash
$ pip install py-des-lib
```

## Hello-World

```py linenums="1"
from pydes import Component, Simulator

class Process(Component):
    def __init__(self, sim: Simulator):
        self.sim = sim

    def main(self):
        for _ in range(10):
            print(self.sim.now(),"waiting")
            self.sim.sleep(2)
            print(self.sim.now(),"waiting")
```

Now schedule the main process object and run simulation

```py linenums="1"
sim = Simulator()
p = Process(sim)
sim.schedule(p.main)
sim.schedule(p.main)
sim.run()
```

## Simulator Object

:::pydes.Simulator
options:
show_object_full_path: false
show_root_toc_entry: false
show_root_heading: false
members: - **init**
options:
show_object_full_path: false
show_root_toc_entry: false
show_root_heading: false
members: - **init**

## Component Object

:::pydes.Component
options:
show_object_full_path: false
show_root_toc_entry: false
show_root_heading: false
members: - **init**
options:
show_object_full_path: false
show_root_toc_entry: false
show_root_heading: false
members: - **init**

## Recording Events

:::pydes.Monitor
options:
show_object_full_path: false
show_root_toc_entry: false
show_root_heading: false
members: - **init**
options:
show_object_full_path: false
show_root_toc_entry: false
show_root_heading: false
members: - **init**
