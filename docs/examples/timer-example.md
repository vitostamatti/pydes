# Timer Example

This example demostrates the basic usage of the `sleep` method and shows
two different ways of modeling a Timer in `pydes`.

```py
--8<-- "./examples/01_timer_example.py:example"
```

To run the simulation with these two different timers, you have to 
create the `Simulator` object and `schedule` both Timer components

```py
--8<-- "./examples/01_timer_example.py:run-example"
```

The outputs of this simulation would look something like this.

```bash
--8<--
./examples/out/01_timer_example_out.txt
--8<--
```
