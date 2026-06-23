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

- Plain SimPy: `simpy_examples/process_communication_plain.py`
- NestedSimPy: `simpy_examples/process_communication_nested.py`

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

The plain SimPy model is unchanged except for the nesting setup: the message pipes are a `NestedStore`, the run is `env.nested_run()`, and branching fires on **every store put** (a message sent), forking **1 inner simulation** that runs for **20 time units, or until the message is consumed**.

## Run

```bash
python simpy_examples/process_communication_plain.py
python simpy_examples/process_communication_nested.py
```
