# Process Example

This example illustrates how to use the `Component` class and the `sleep` method of the `Simulator` in a simulation scenario.

## Imports

To begin, import the necessary classes from `pydes`.

```python
from pydes import Component, Simulator
```

## Define Model

Next, define your processes by creating a class that extends the `Component` class and implements its `main` method.

Inside the `main` method, you can control the simulation time and process flow using various methods provided by the `Simulator`. Here, we use the `sleep` method to pause execution for a specified duration before continuing with the component's process. While this component is inactive, other processes can progress within the simulation.

Additionally, you may want to record information about the process using the `record` method of the `Simulator`.

In this simple example, we're modeling a process that repeatedly sleeps for a given time and then restarts. There are two approaches to model this:

Use an infinite `while` loop within the `main` method to encapsulate the process logic.

```py linenums="1" hl_lines="1 11"
--8<-- "./docs/code/01_process_example.py:example-1"
```

Alternatively, activate the `Component` within the `main` method by passing `self.main` to the `schedule` method.

```py linenums="1" hl_lines="11"
--8<-- "./docs/code/01_process_example.py:example-2"
```

## Run Simulation

To execute the simulation with these two different processes, create a `Simulator` object and schedule both components.

```py linenums="1"
--8<-- "./docs/code/01_process_example.py:run-example"
```

The simulation output would resemble the following:

```bash
--8<--
./docs/code/out/01_process_example_out.txt
--8<--
```
