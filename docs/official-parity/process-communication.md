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

The same model under NestedSimPy. **New lines are highlighted green and modified
lines amber**, relative to the plain baseline above; long unchanged runs are
folded — click to expand them.

```{codeannotate} ../../simpy_examples/process_communication_plain.py ../../simpy_examples/process_communication_nested.py
:title: simpy_examples/process_communication_nested.py
:context: 3
```

## Discussion

The pipe `simpy.Store` becomes `NestedStore`, and branching triggers on **`store_put`** — each message published. The producer and consumer processes are unchanged, so message delivery matches plain SimPy.

## Run

```bash
python simpy_examples/process_communication_plain.py
python simpy_examples/process_communication_nested.py
```
