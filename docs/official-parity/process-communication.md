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

Going from an existing SimPy code to NestedSimPy only requires importing the NestedSimPy package, replacing SimPy objects with NestedSimPy objects, modifying timeout commands, and configuring the nested simulation parameters.

