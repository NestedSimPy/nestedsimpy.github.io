# Branching Model

The core mental model is:

- keep the SimPy process logic,
- replace key infrastructure with branch-aware equivalents,
- run one outer trajectory,
- fork child futures when a declared boundary fires.

## From Plain SimPy To PyNestedSim

The usual substitutions are:

| Plain SimPy | PyNestedSim |
| --- | --- |
| `simpy.Environment()` | `NestedEnvironment()` |
| `simpy.Resource(...)` | `NestedResource(...)` |
| `simpy.PreemptiveResource(...)` | `NestedPreemptiveResource(...)` |
| `simpy.Store(...)` | `NestedStore(...)` |
| `simpy.Container(...)` | `NestedContainer(...)` |
| `env.timeout(...)` | `env.nested_timeout(...)` |
| `env.run()` | `env.nested_run()` |

The process logic itself often stays very close to the original SimPy model.

There is not currently a separate `NestedPriorityResource` class. Priority-aware
service is handled through `NestedPreemptiveResource`, which preserves SimPy's
priority/preemption request path while adding tracing and branch hooks.

## Core Objects

`NestedEnvironment`
: Stores branching configuration and exposes branch-aware entry points such as
  `nested_run()` and `run_single_path(...)`.

`NestedResource`, `NestedPreemptiveResource`, `NestedStore`, `NestedContainer`
: Wrapped SimPy primitives that emit structured state transitions and watcher
  callbacks.

`env.nested_timeout(...)`
: Branch-aware timeout helper that tracks pending sleeps so residual durations
  can be resampled after a fork.

## Typical Configuration Flow

```python
env = NestedEnvironment()
server = NestedResource(env, capacity=1, nested_id="srv")

env.set_output_options(out_dir="out/mm1_simpy", gzip_trace=False)
env.set_nested_triggering_objects(nested_id="srv")
env.set_nesting_conditions({"on": "arrival", "frequency": 1})
env.set_inner_repetitions(2)
env.set_inner_stopping_condition(relative_time=5.0, triggering_customer_departs=True)

env.nested_run()
```

## Runtime Shape

At runtime, PyNestedSim does four things around the underlying SimPy model:

1. runs the outer trajectory,
2. watches for the configured boundary,
3. forks child futures at that boundary,
4. records traces, manifests, and packaged outputs for the outer and inner runs.

## Where To Go Next

- For the boundary language, go to {doc}`branch-triggers`.
- For branch termination and replay, go to {doc}`stop-rules-replay`.
- For disk outputs, go to {doc}`traces-and-outputs`.
