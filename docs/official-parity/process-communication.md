# Process Communication

## Scenario

This example uses `Store` objects to connect asynchronous producer and consumer
processes, including cases where the consumer is late relative to the sending
process.

## Files

- Plain SimPy: `simpy_examples/process_communication_plain.py`
- NestedSimPy: `simpy_examples/process_communication_nested.py`

## Parity Goal

The nested adaptation keeps the visible communication output aligned with the
plain example while adding branchable store traffic underneath.

## What NestedSimPy Adds

- branch triggers on store puts,
- structured traces for inter-process message flow,
- packaged outputs for comparing alternative futures.

## Code

This pair stays readable enough that showing the actual source is more useful
than summarizing it abstractly.

````{dropdown} Plain SimPy source
```{literalinclude} ../../simpy_examples/process_communication_plain.py
:language: python
:caption: simpy_examples/process_communication_plain.py
```
````

````{dropdown} NestedSimPy source
```{literalinclude} ../../simpy_examples/process_communication_nested.py
:language: python
:caption: simpy_examples/process_communication_nested.py
```
````

## Run

```bash
python simpy_examples/process_communication_plain.py
python simpy_examples/process_communication_nested.py
```
