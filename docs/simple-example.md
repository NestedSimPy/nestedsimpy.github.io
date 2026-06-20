# Simple example

This page walks through the smallest end-to-end example: a single **M/M/1
queue**, first as a plain SimPy model and then adapted for NestedSimPy, with the
outputs a nested run produces.

## Plain SimPy vs. NestedSimPy

The plain model is a standard SimPy M/M/1 queue. The NestedSimPy version keeps
the same outer behavior and adds instrumented primitives, a triggering event,
and inner simulations.

### Plain SimPy

```{literalinclude} ../simpy_examples/mm1_plain.py
:language: python
:caption: simpy_examples/mm1_plain.py
```

### NestedSimPy

The same model under NestedSimPy. **New lines are highlighted green and modified
lines amber**, relative to the plain baseline above; long unchanged runs are
folded — click to expand them.

```{codeannotate} ../simpy_examples/mm1_plain.py ../simpy_examples/mm1_nested.py
:title: simpy_examples/mm1_nested.py
:context: 3
```

```{tip}
Download: {download}`mm1_plain.py <../simpy_examples/mm1_plain.py>` ·
{download}`mm1_nested.py <../simpy_examples/mm1_nested.py>`
```

## What a nested run produces

```{figure} _static/mm1-nested-illustration.svg
:alt: Number of customers over time for an M/M/1 queue, showing the outer simulation in black with inner simulations forked at two triggering events.
:width: 100%

A nested run of the M/M/1 queue. The **black** line is the outer simulation
(number of customers over time). At each **triggering event** (dots), the outer
simulation pauses and forks a set of **inner simulations** (light lines) that
each explore a possible future from that state.
```

## Next

- {doc}`official-parity/index` — the same idea applied to the full set of
  official SimPy examples.
- {doc}`topical-guides/index` — how triggers, stop rules, and outputs work.
