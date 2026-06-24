# Using NestedSimPy

These pages walk through the workflow once you know what the package is for:
how to convert a plain SimPy model, where simulations branch, when they stop,
and how to visualize and export the result.

````{grid} 1 1 2 2
:gutter: 2

```{grid-item-card} Converting code
:link: branching-model
:link-type: doc

The shift from plain SimPy to NestedSimPy: an instrumented environment,
instrumented primitives, and a branch-aware run.
```

```{grid-item-card} Triggering events
:link: branch-triggers
:link-type: doc

Where the outer simulation forks — arrivals, state predicates, and published
events used as branch boundaries.
```

```{grid-item-card} Stopping conditions
:link: stop-rules-replay
:link-type: doc

How the outer run and each inner run decide when to stop — by time, by the
anchor customer departing, or a custom condition.
```

```{grid-item-card} Visualization
:link: visualization
:link-type: doc

Plot the outer trajectory and the inner branches of a finished run with the
`OutputManager`.
```

```{grid-item-card} Exporting data
:link: traces-and-outputs
:link-type: doc

Turn a run into datasets — the outer sample path, per-branch tables, and the
aggregated feature/label table for prediction.
```
````

```{toctree}
:hidden:
:maxdepth: 1

branching-model
branch-triggers
stop-rules-replay
visualization
traces-and-outputs
```
