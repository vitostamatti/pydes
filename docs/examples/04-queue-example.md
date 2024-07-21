# Queue Example

In this example, we introduce another Py-DES component called `Queue`. Queues are an essential
part of almost every system in real life.

:::pydes.Queue
    options:
        show_object_full_path: false
        show_root_toc_entry: false
        show_root_heading: true
        show_bases: false
        show_symbol_type_heading: false

## Imports

First of all we import the necessary objects from `pydes`

```py linenums="1"
--8<-- "./docs/code/04_queue_example.py:imports"
```

## Define Model

For this example we define a first process that is going to `put` elements into
the `Queue` with a time interval.

```py linenums="1"
--8<-- "./docs/code/04_queue_example.py:example-1"
```

There is another process running that will try `get` elements from the same `Queue`
and wait if it is empty.

```py linenums="1"
--8<-- "./docs/code/04_queue_example.py:example-2"
```

## Run Simulation

With all this defined. We build the `Simulator` and the components involved. We schedule
both processes and then start the simulation.

```bash
--8<-- "./docs/code/04_queue_example.py:run"
```

The simulation output would resemble the following

```bash
--8<--
./docs/code/out/04_queue_example_out.txt
--8<--
```