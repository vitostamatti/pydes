# Timer Example

This example demostrates the basic usage of the `Component` class and 
the `sleep` method of the `Simulator`. 

First of all, you need to import the `Simulator` and the `Component` classes 
from `pydes`


```py
from pydes import Component, Simulator
```

To define your processes you need to define a class excending the Component and 
implement the `main` method of this class. 

Inside the `main` method, you can use different `Simulator` methods to control 
the flow of the simulation time and the advance of the procesess. In this case,
we use the `sleep` method to "wait" for a given time before continuing with the 
process of the component. While this component is "sleeping", other process can 
take control of the simulation and advance in its own process if they need to

Besides the sleep, we want to record some information about the process. For 
this we use the `record` method of the `Simulator`.

In this short example, we're going to model an infinite process that is going to 
sleep for a given time and then restart. To model this situation, there'are two possible approaches.

*  Defining a while infinite loop in the body of the main method and model all the process inside this loop.

```py linenums="1" hl_lines="1 11"
--8<-- "./examples/01_process_example.py:example-1"
```

* Alternatively, one could define the activation of the `Component` inside 
the `main` method by passing `self` to the `schedule` method.

```py linenums="1" hl_lines="11"
--8<-- "./examples/01_process_example.py:example-2"
```

To run the simulation with these two different timers, you have to 
create the `Simulator` object and `schedule` both Timer components

```py linenums="1"
--8<-- "./examples/01_process_example.py:run-example"
```

The outputs of this simulation would look something like this.

```bash
--8<--
./examples/out/01_process_example_out.txt
--8<--
```
