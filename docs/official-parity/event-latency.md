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

### Plain SimPy

```{literalinclude} ../../simpy_examples/event_latency_plain.py
:language: python
:caption: simpy_examples/event_latency_plain.py
```

### NestedSimPy

The same model under NestedSimPy. **New lines are highlighted green and modified
lines amber**, relative to the plain baseline above; long unchanged runs are
folded — click to expand them.

```{codeannotate} ../../simpy_examples/event_latency_plain.py ../../simpy_examples/event_latency_nested.py
:title: simpy_examples/event_latency_nested.py
:context: 3
```

## Run

```bash
python simpy_examples/event_latency_plain.py
python simpy_examples/event_latency_nested.py
```
