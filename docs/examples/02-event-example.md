# Event Example

This example is about showing the usage of the `Event` component. This component can be used as a 
condition that needs to be triggered in order to continue the simulation.

:::pydes.Event
    options:
        show_object_full_path: false
        show_root_toc_entry: false
        show_root_heading: true
        show_bases: false
        show_symbol_type_heading: false
        
        
## Imports

First of all, we import the necessary modules and classes from the `pydes` library. These imports are essential for setting up and running our simulation.

```py linenums="1"
--8<-- "./docs/code/02_event_example.py:imports"
```


## Define Model

We define `Process1`, which is one of the example processes in our simulation. `Process1` waits for an event to be triggered.

```py linenums="1"
--8<-- "./docs/code/02_event_example.py:example-1"
```

We define `Process2`, which is the second example process in our simulation. `Process2` triggers the event after a specified duration.

```py linenums="1"
--8<-- "./docs/code/02_event_example.py:example-2"
```


## Run Simulation

Finally, we set up the simulation environment, schedule the processes, and run the simulation.

```bash
--8<-- "./docs/code/02_event_example.py:run"
```

```bash
--8<--
./docs/code/out/02_event_example_out.txt
--8<--
```