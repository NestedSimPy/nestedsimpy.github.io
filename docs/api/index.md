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

## Replay

To re-run a single branch deterministically — for example, to inspect a path a
full run already surfaced — use `run_single_path(...)`:

```python
env.run_single_path(trigger_index=2, branch_index=0, seed=1234)
```

## On disk

A run lands under the output directory (set by `set_output_options`) in two
layers — raw traces, then packaged datasets:

```text
nested_output/<experiment>/<outer_id>/
  raw/                       # raw JSONL traces + manifests
    outer/                   #   the outer run (trace.jsonl, manifest.json)
    j=0001/k=00/             #   one folder per branch (j = trigger, k = branch)
  exports/                   # packaged datasets, in three forms:
    [seed][j,bnd][inner].csv    #   per-inner files (+ [seed]-outer.csv, metric JSONs)
    state_wide.csv …            #   consolidated tables (state_wide/long, events)
    user_waits.csv              #   a postprocessor's own metric
```

The {doc}`raw-data` page details the raw event stream, the manifest fields, and
the per-branch metrics; {doc}`Exporting data <../topical-guides/traces-and-outputs>`
explains the three export forms and the `OutputManager` that reads them.

```{toctree}
:hidden:
:maxdepth: 1

simpy-core
reporting
raw-data
```
