# API Reference

This API section is intentionally scoped to the SimPy-facing surface of
PyNestedSim.

The main split is:

- `Topical Guides`: concept-first pages if you want the big picture before the
  full module reference.
- `SimPy Core API`: environment, branch driver, instrumented primitives, sleep,
  events, state, trace, and typed configuration structures.
- `Reporting API`: postprocess and packaged reporting helpers.

````{grid} 1 1 2 2
:gutter: 2

```{grid-item-card} Topical Guides
:link: ../topical-guides/index
:link-type: doc

Start there if you want a concept-first explanation before reading the module
reference.
```

```{grid-item-card} SimPy Core API
:link: simpy-core
:link-type: doc

Read the API for `NestedEnvironment`, `NestedResource`,
`NestedPreemptiveResource`, `NestedStore`, `NestedContainer`, boundary
compilation, branch execution, sleep handling, tracing, and state capture.
```

```{grid-item-card} Reporting API
:link: reporting
:link-type: doc

Read the API for packaged outputs, export helpers, and reusable reporting and
plotting utilities.
```
````

```{toctree}
:maxdepth: 1

simpy-core
reporting
```
