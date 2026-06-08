# Topical Guides

This section groups the main concepts behind the SimPy-facing PyNestedSim
workflow.

Use these pages when you already know what the package is for and want a more
direct explanation of how the moving parts fit together.

````{grid} 1 1 2 2
:gutter: 2

```{grid-item-card} Branching Model
:link: branching-model
:link-type: doc

Understand the main shift from plain SimPy to PyNestedSim: instrumented
environments, instrumented primitives, and branch-aware execution.
```

```{grid-item-card} Branch Triggers
:link: branch-triggers
:link-type: doc

See how arrivals, state predicates, and published events can be used as branch
boundaries.
```

```{grid-item-card} Stop Rules and Replay
:link: stop-rules-replay
:link-type: doc

See how outer and inner runs stop, and how a specific path can be replayed.
```

```{grid-item-card} Traces and Outputs
:link: traces-and-outputs
:link-type: doc

Learn how traces, manifests, exports, and packaged reporting outputs are laid
out on disk.
```
````

```{toctree}
:maxdepth: 1

branching-model
branch-triggers
stop-rules-replay
traces-and-outputs
```
