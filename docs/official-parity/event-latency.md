# Event Latency

## Scenario

Adapted from SimPy's official [Event Latency example](https://simpy.readthedocs.io/en/latest/examples/latency.html).

This example uses a `Store` to model delayed message propagation between
processes, which is a common pattern for cables, transport links, or other
communication channels.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_event_latency.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: [`simpy_examples/event_latency_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/event_latency_plain.py)
- NestedSimPy: [`simpy_examples/event_latency_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/event_latency_nested.py)

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/event_latency_plain.py
:language: python
:caption: simpy_examples/event_latency_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/event_latency_plain.py ../../simpy_examples/event_latency_nested.py
:title: simpy_examples/event_latency_nested.py
:context: 3
```

## Discussion

Going from an existing SimPy code to NestedSimPy only requires importing the NestedSimPy package, replacing SimPy objects with NestedSimPy objects, modifying timeout commands, and configuring the nested simulation parameters.

