# Event Latency

## Scenario

This example uses a `Store` to model delayed message propagation between
processes, which is a common pattern for cables, transport links, or other
communication channels.

## Files

- Plain SimPy: `simpy_examples/event_latency_plain.py`
- NestedSimPy: `simpy_examples/event_latency_nested.py`

## Parity Goal

The nested adaptation keeps the outer message-delivery timing aligned with the
plain baseline. In tests, the received-message lines are matched directly.

## What NestedSimPy Adds

- branch triggers on store put events,
- structured traces for store traffic,
- packaged artifacts for post-run analysis.

## Code

For this pair, the best way to judge the adaptation is to read the two source
files directly.

```{codediff} ../../simpy_examples/event_latency_plain.py ../../simpy_examples/event_latency_nested.py
:left-title: event_latency_plain.py
:right-title: event_latency_nested.py
:context: 3
```

````{dropdown} Plain SimPy source
```{literalinclude} ../../simpy_examples/event_latency_plain.py
:language: python
:caption: simpy_examples/event_latency_plain.py
```
````

````{dropdown} NestedSimPy source
```{literalinclude} ../../simpy_examples/event_latency_nested.py
:language: python
:caption: simpy_examples/event_latency_nested.py
```
````

## Run

```bash
python simpy_examples/event_latency_plain.py
python simpy_examples/event_latency_nested.py
```
