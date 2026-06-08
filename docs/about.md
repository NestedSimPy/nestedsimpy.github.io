# About

PyNestedSim is a SimPy-focused project for branching, replay, and trace-based
analysis of discrete-event models.

This site is organized around how PyNestedSim extends familiar SimPy models.

## Scope

The current site covers:

- SimPy usage and branch-aware execution
- official SimPy parity examples
- API reference for the SimPy-facing package surface
- instrumented `Resource`, `PreemptiveResource`, `Store`, and `Container` paths

Ciw-related experiments are not part of this public documentation set.

## Project Links

- GitHub: `https://github.com/happywhy0928/NestedSimPy_Web`
- Documentation site: `https://happywhy0928.github.io/NestedSimPy_Web/`

## Source Layout

- `nested-sim/nestedsim`
  Core package implementation
- `nested-sim/examples`
  Native PyNestedSim examples and reporting wrappers
- `simpy_examples`
  Official SimPy parity adaptations
- `queueing_examples`
  Downstream application-specific experiments

## Documentation Layout

- {doc}`getting-started`
- {doc}`topical-guides/index`
- {doc}`official-parity/index`
- {doc}`api/index`
- {doc}`architecture`
