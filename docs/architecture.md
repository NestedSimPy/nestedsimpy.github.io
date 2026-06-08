# Architecture

This page is the short SimPy-focused architecture view for NestedSimPy.

## Runtime Loop

At a high level, the runtime does five things:

1. instrument the SimPy model,
2. run one outer trajectory,
3. fork child futures when a boundary fires,
4. collect per-branch traces and manifests,
5. package outputs for inspection and plotting.

## Main Building Blocks

`NestedEnvironment`
: Holds branch configuration, run controls, replay helpers, and branch-safe
  timeout wrappers.

`NestedResource`, `NestedPreemptiveResource`, `NestedStore`, `NestedContainer`
: Wrapped SimPy primitives that emit structured state transitions and watcher
  callbacks.

`NestedPreemptiveResource`
: The priority/preemption-aware resource path. NestedSimPy does not currently
  expose a separate ``NestedPriorityResource`` wrapper.

`safe_sleep` / `env.nested_timeout(...)`
: Sleep registration layer used so pending delays can be resampled correctly
  after a fork.

`branch_after_simpy`
: The SimPy branch driver. It runs the outer simulation, detects boundaries, forks
  children, reseeds or restores RNG state, and writes manifests.

`trace` and `postprocess`
: The trace layer writes JSONL events; the postprocess layer turns those traces
  into packaged exports such as CSV and Plotly outputs.

## SimPy-Only Scope

This site currently describes only the SimPy path:

- SimPy branch triggers
- SimPy resources, stores, and containers
- SimPy parity examples
- SimPy reporting helpers