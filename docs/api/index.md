# Implementation

How NestedSimPy is built underneath the SimPy-facing API: the runtime that drives
branching, the module reference, and the raw data each run records. The whole
site describes only the SimPy path.

## Runtime loop

At a high level, the runtime does five things:

1. instrument the SimPy model,
2. run one outer trajectory,
3. fork child futures when a boundary fires,
4. collect per-branch traces and manifests,
5. package outputs for inspection, visualization, and export.

## Main building blocks

`NestedEnvironment`
: Holds branch configuration, run controls, replay helpers, and branch-safe
  timeout wrappers.

`NestedResource`, `NestedPreemptiveResource`, `NestedStore`, `NestedContainer`
: Wrapped SimPy primitives that emit structured state transitions and watcher
  callbacks. `NestedPreemptiveResource` is the priority/preemption-aware path;
  there is no separate `NestedPriorityResource` wrapper.

`safe_sleep` / `env.nested_timeout(...)`
: Sleep registration layer so pending delays can be resampled correctly after a
  fork.

`branch_after_simpy`
: The SimPy branch driver. It runs the outer simulation, detects boundaries,
  forks children, reseeds or restores RNG state, and writes manifests.

`trace` and `postprocess`
: The trace layer writes JSONL events; the postprocess layer turns those traces
  into packaged exports (CSV and Plotly outputs).

`OutputManager`
: The post-hoc interface over a packaged run — see
  {doc}`../topical-guides/visualization` and
  {doc}`../topical-guides/traces-and-outputs`.

## Module reference

````{grid} 1 1 2 2
:gutter: 2

```{grid-item-card} SimPy Core API
:link: simpy-core
:link-type: doc

`NestedEnvironment`, the instrumented primitives, the branch driver, sleep,
events, state, trace, and the typed configuration structures.
```

```{grid-item-card} Reporting API
:link: reporting
:link-type: doc

Postprocessing, the packaged reporting helpers, and the `OutputManager`.
```
````

## Raw data

Before packaging, a run writes raw JSONL traces and manifests under `raw/`. The
{doc}`raw-data` page describes the event stream, the manifest fields, and the
per-branch metrics that packaging produces.

```{toctree}
:maxdepth: 1

simpy-core
reporting
raw-data
```
