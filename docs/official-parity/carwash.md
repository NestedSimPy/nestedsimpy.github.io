# Carwash

## Scenario

Cars arrive at a carwash with a limited number of washing machines. If a machine
is busy, they wait in queue; once a machine is free, they start washing and
leave when finished.

## Files

- Plain SimPy: `simpy_examples/carwash_plain.py`
- NestedSimPy: `simpy_examples/carwash_nested.py`

## Parity Goal

The nested version preserves the outer printed sequence of arrivals, service
starts, and departures from the plain example. The test suite compares those
outer messages directly.

## What NestedSimPy Adds

- instrumented queue and service-state traces,
- branch outputs rooted at the wash resource,
- packaged run folders that can be plotted after the run.

## Code

The adaptation stays close to the original carwash logic. Expand the source
files directly below to inspect the actual delta.

````{dropdown} Plain SimPy source
```{literalinclude} ../../simpy_examples/carwash_plain.py
:language: python
:caption: simpy_examples/carwash_plain.py
```
````

````{dropdown} NestedSimPy source
```{literalinclude} ../../simpy_examples/carwash_nested.py
:language: python
:caption: simpy_examples/carwash_nested.py
```
````

## Run

```bash
python simpy_examples/carwash_plain.py
python simpy_examples/carwash_nested.py
```
