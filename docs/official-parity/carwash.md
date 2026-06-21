# Carwash

```{seealso}
Based on SimPy's official [Carwash example](https://simpy.readthedocs.io/en/latest/examples/carwash.html).
```

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

### Plain SimPy

```{literalinclude} ../../simpy_examples/carwash_plain.py
:language: python
:caption: simpy_examples/carwash_plain.py
```

### NestedSimPy

The same model under NestedSimPy. **New lines are highlighted green and modified
lines amber**, relative to the plain baseline above; long unchanged runs are
folded — click to expand them.

```{codeannotate} ../../simpy_examples/carwash_plain.py ../../simpy_examples/carwash_nested.py
:title: simpy_examples/carwash_nested.py
:context: 3
```

## Run

```bash
python simpy_examples/carwash_plain.py
python simpy_examples/carwash_nested.py
```
