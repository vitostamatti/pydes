# Discrete Event Simulation in Python with Py-DES

In this set of examples, we’ll explore the Py-DES library and its main capabilities. 

## Setup

Easiest way to setup Py-DES is to install it using `pip` with the following command.

```bash
$ pip install py-des
```

## Hello-World


```py
from pydes.process import Component, Simulator

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

```py
sim = Simulator()
p = Process(sim)
sim.schedule(p)
sim.run()
```

## Simulator Object

:::pydes.process.Simulator
    options:
        show_object_full_path: false
        show_root_toc_entry: false
        show_root_heading: false
        members:
        - __init__


## Component Object

:::pydes.process.Component
    options:
        show_object_full_path: false
        show_root_toc_entry: false
        show_root_heading: false
        members:
        - __init__

## Recording Events

:::pydes.process.Monitor
    options:
        show_object_full_path: false
        show_root_toc_entry: false
        show_root_heading: false
        members:
        - __init__


## Predefined Components

:::pydes.process.components.Queue
    options:
        show_object_full_path: false
        show_root_toc_entry: false
        show_root_heading: true
        members:
        - __init__
  
<!--   
        <!-- - Store
        - State
        - Container
        - Resource -->