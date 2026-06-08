# Simple example

This page walks through the smallest end-to-end example: a single **M/M/1
queue**, first as a plain SimPy model and then adapted for NestedSimPy, with the
outputs a nested run produces.

## Plain SimPy vs. NestedSimPy

```{note}
TODO — drop in the minimal M/M/1 *plain SimPy* model and its *NestedSimPy*
adaptation here, shown side by side (or as a diff) so the delta is obvious.
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

```{note}
TODO — add a summary table of per-branch results from this run. (Figure labels
will be updated to match the standard terminology later.)
```

## Next

- {doc}`official-parity/index` — the same idea applied to the full set of
  official SimPy examples.
- {doc}`topical-guides/index` — how triggers, stop rules, and outputs work.
