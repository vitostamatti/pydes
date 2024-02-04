<figure markdown>
  ![Logo](./assets/pydes.png){ width="500" }
</figure>


# Welcome to Py-DES

**py-des** is a Python package designed to simplify the process of discrete event simulation, providing users with an intuitive and efficient framework for modeling and analyzing complex systems. Built upon the principles of simplicity, flexibility, and performance, **py-des** aims to offer a streamlined solution for simulation tasks across various domains, including operations research, computer science, and manufacturing.

## Key Principles

- **Simplicity:** **py-des** prioritizes ease of use, allowing users to quickly define simulation models and scenarios without unnecessary complexity.

- **Flexibility:** With **py-des**, users have the flexibility to customize simulation through the usage of predefined and custom `Components`. From simple simulations to complex scenarios involving multiple entities and interactions, **py-des** adapts to diverse use cases with ease.


## Getting Started

To begin using **py-des**, simply install the package via pip (_comming soon_):

```bash
pip install py-des
```

First define your main process extending the `Component` and defining a `main` method. 

```py
from pydes.process import Component, Simulator

class Process(Component):
    def __init__(self, sim: Simulator):
        self.sim = sim

    def main(self):
        for _ in range(10):
            self.sim.record(self, "waiting", 1)
            self.sim.sleep(2)
            self.sim.record(self, "waiting", 0)
```

Now schedule the main process object and run simulation

```py
sim = Simulator()
p = Process(sim)
sim.schedule(p)
sim.run()
```

Start your journey in the [overview](overview.md) section or check out the [examples](examples.md) for guidance on how to create simulation environments, schedule events, and analyze simulation outcomes.


## Feedback and Support

If you have any questions, suggestions, or feedback regarding **py-des**, feel free to reach out via GitHub issues or the official communication channels. Your input is invaluable in shaping the future development of the library and ensuring that it meets the needs of its users.

