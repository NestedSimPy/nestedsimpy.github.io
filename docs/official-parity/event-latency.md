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
```

## Discussion

The cable's internal `simpy.Store` becomes a `NestedStore` with `nested_id="cable_store"`, and branching triggers on `store_put` — each message entering the cable. The cable delay and the sender's interval become deterministic `env.nested_timeout` calls, and the `put` into the store is now yielded. Messages change from plain strings to dicts carrying an `item_id`, so individual items can be followed through the store. The general conversion steps are in {doc}`From SimPy to NestedSimPy <../topical-guides/branching-model>`.

