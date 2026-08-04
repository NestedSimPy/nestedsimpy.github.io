# Process Communication

## Scenario

Adapted from SimPy's official [Process Communication example](https://simpy.readthedocs.io/en/latest/examples/process_communication.html).

This example uses `Store` objects to connect asynchronous producer and consumer
processes, including cases where the consumer is late relative to the sending
process.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_process_communication.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: [`simpy_examples/process_communication_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/process_communication_plain.py)
- NestedSimPy: [`simpy_examples/process_communication_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/process_communication_nested.py)

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/process_communication_plain.py
:language: python
:caption: simpy_examples/process_communication_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/process_communication_plain.py ../../simpy_examples/process_communication_nested.py
:title: simpy_examples/process_communication_nested.py
:context: 3
```

## Discussion

Both scenarios replace `simpy.Store` pipes with `NestedStore` objects: the one-to-one pipe is registered as `nested_id="pipe"`, and `BroadcastPipe` gives each output connection its own id (`bc_pipe_out0`, `bc_pipe_out1`), so the one-to-many run can pass the whole list to `set_triggering_objects`. Branching triggers on `store_put` in both cases. Messages change from tuples to dicts with an `item_id` and `sent_time`, and the transmission and consumer-work delays become deterministic `env.nested_timeout` calls with the `random.randint` draw kept outside. Each run also attaches `wait_time_hook` with `set_postprocessor`, adding a wait-time summary to the exported outputs. The general conversion steps are in {doc}`From SimPy to NestedSimPy <../topical-guides/branching-model>`.

