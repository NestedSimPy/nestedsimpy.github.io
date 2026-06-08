# PyNestedSim

PyNestedSim adds branching, replay, and trace-based analysis to SimPy models.

This site is focused on SimPy usage and on parity adaptations of the official
SimPy examples.

```{note}
This documentation set covers the SimPy path only. Ciw-related experiments are
not part of the public site.
```

````{grid} 1 1 2 2
:gutter: 2

```{grid-item-card} PyNestedSim in 10 Minutes
:link: getting-started
:link-type: doc

Start with the shortest SimPy-first path through the project: instrument a
model, declare branch boundaries, run once, and inspect packaged outputs.
```

```{grid-item-card} Topical Guides
:link: topical-guides/index
:link-type: doc

Read focused guides for branching, triggers, stop rules, replay, and output
packaging without dropping straight into the full API reference.
```

```{grid-item-card} Official SimPy Parity
:link: official-parity/index
:link-type: doc

See the public examples story for the project: parity adaptations of the
official SimPy examples, with PyNestedSim layered on top.
```

```{grid-item-card} API Reference
:link: api/index
:link-type: doc

Browse the SimPy-facing API surface for the environment, resources, branch
driver, tracing layer, and reporting helpers.
```

```{grid-item-card} About
:link: about
:link-type: doc

See the project scope, source layout, and project links.
```
````

## Why PyNestedSim

PyNestedSim is for cases where a plain SimPy model is not enough because you
want to:

- fork the future at meaningful decision boundaries,
- replay a branch from a captured manifest,
- collect structured traces instead of only ad hoc printouts,
- package runs into exports that can be analyzed after execution.

## What PyNestedSim Adds

- Instrumented SimPy primitives for `Resource`, `PreemptiveResource`, `Store`, and `Container`
- Declarative branch triggers on arrivals, state predicates, and events
- Branch-local stop rules and replay from manifests
- Structured traces and packaged CSV/Plotly exports
- Parity adaptations for the official SimPy example set covered by this site

## Sections

`PyNestedSim in 10 Minutes`
: Short tutorial path for the core SimPy workflow.

`Official SimPy Parity`
: The examples section. This is the primary public examples story for the
  project.

`Topical Guides`
: Concept pages for branching, triggers, stop rules, replay, and outputs.

`API Reference`
: SimPy-facing API surface for the instrumented environment, resources,
  branch driver, tracing, and reporting layers.

`Architecture`
: Short runtime-oriented explanation of how branching is layered onto SimPy.

`About`
: Project scope, source layout, and project links.

## At a Glance

| Topic | Current public scope |
| --- | --- |
| Modeling baseline | SimPy |
| Main examples story | Official SimPy parity |
| Public API docs | SimPy-facing modules only |
| Ciw | Not covered in this site |

## Documentation Map

```{toctree}
:maxdepth: 2
:caption: Contents

getting-started
topical-guides/index
official-parity/index
api/index
architecture
about
```

## Project Layout

- `nested-sim/nestedsim`: core SimPy instrumentation package
- `nested-sim/examples`: native PyNestedSim examples and plotting/postprocess utilities
- `simpy_examples`: official SimPy parity adaptations
- `nested-sim/tests/simpy_cases/examples/test_official_examples.py`: parity smoke tests

## Positioning

SimPy is the baseline modeling framework. PyNestedSim sits on top of that
baseline and keeps the outer behavior of known examples intact while adding
branching, traces, replay, and analysis outputs.
