# Simple example

This page walks through the smallest end-to-end example: a single **M/M/1
queue**, first as a plain SimPy model and then adapted for NestedSimPy, with the
outputs a nested run produces.

## Plain SimPy vs. NestedSimPy

```{note}
TODO — drop in the minimal M/M/1 *plain SimPy* model and its *NestedSimPy*
adaptation here, shown side by side (or as a diff) so the delta is obvious.
```

<!-- Once the minimal mm1_plain.py / mm1_nested.py are available, embed them:
````{tab-set}
```{tab-item} Plain SimPy
```{literalinclude} ../simpy_examples/mm1_plain.py
:language: python
```
```
```{tab-item} NestedSimPy
```{literalinclude} ../simpy_examples/mm1_nested.py
:language: python
```
```
````
-->

## What a nested run produces

```{note}
TODO — add the output visualization (the branch plot) and a summary table of
per-branch results from this run.
```

## Next

- {doc}`official-parity/index` — the same idea applied to the full set of
  official SimPy examples.
- {doc}`topical-guides/index` — how triggers, stop rules, and outputs work.
