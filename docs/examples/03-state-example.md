# State Example

In this example, we introduce another Py-DES component called `State`. States are an extension of
events that can take a finite number of values and can be waited for one of them in particular.

:::pydes.State
    options:
        show_object_full_path: false
        show_root_toc_entry: false
        show_root_heading: true
        show_bases: false
        show_symbol_type_heading: false

## Imports

First of all we import the necessary objects from `pydes`

```py linenums="1"
--8<-- "./docs/code/03_state_example.py:imports"
```

## Define Model

For this example we will define a `State` that can take two possible values.
Of course this same behavior could be achieved using simply an `Event`, but
the idea is to showcase the usage of the `State` component.

```py linenums="1"
--8<-- "./docs/code/03_state_example.py:example-1"
```

There is one process that will stop its execution until the state
is set to a specific value.

```py linenums="1"
--8<-- "./docs/code/03_state_example.py:example-2"
```

The other process is going to be responsible of changing the `State` into
its new value. This will be done after a delay and thus delaying the advance
of the other process until the change in the state.

```py linenums="1"
--8<-- "./docs/code/03_state_example.py:example-3"
```

## Run Simulation

With all this defined. We build the `Simulator` and the components involved. We schedule
both processes and then start the simulation.

```bash
--8<-- "./docs/code/03_state_example.py:run"
```

The simulation output would resemble the following:

```bash
--8<--
./docs/code/out/03_state_example_out.txt
--8<--
```