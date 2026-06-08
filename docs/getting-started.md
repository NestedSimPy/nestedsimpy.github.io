# NestedSimPy in 10 Minutes

NestedSimPy is easiest to understand as a small layer on top of SimPy:

1. Build your model with a `NestedEnvironment`.
2. Replace plain SimPy primitives with instrumented ones such as `NestedResource`, `NestedPreemptiveResource`, `NestedStore`, or `NestedContainer`.
3. Use `env.nested_timeout(...)` instead of raw `env.timeout(...)` where branch-safe sleeps matter.
4. Declare when branches should fork.
5. Run once and inspect packaged outputs.

## Install

From the repository root:

```bash
python3 -m pip install -r nested-sim/requirements.txt
```

## First Run

The smallest native walkthrough is the branching M/M/1 demo:

```bash
cd nested-sim
python examples/run_mm1_simpy.py --postprocess --plot-static
```

That command:

- runs the outer SimPy trajectory,
- spawns inner simulations at the configured arrival boundaries,
- packages the run into `raw/` and `exports/`,
- writes CSV summaries and an HTML plot.

## Compare Against Plain SimPy

To compare the branching demo against its plain baseline:

```bash
cd nested-sim
python examples/run_mm1_simpy_plain.py
python examples/run_mm1_simpy.py --postprocess
```

The plain script shows baseline behavior. The NestedSimPy version preserves the
same model logic while adding branch generation and output packaging.

## Mental Model

Think of NestedSimPy as a layer that leaves your SimPy process logic in place
but swaps in branch-aware infrastructure:

- `simpy.Environment` becomes `NestedEnvironment`,
- `simpy.Resource` can become `NestedResource`,
- `simpy.PreemptiveResource` can become `NestedPreemptiveResource`,
- `simpy.Store` can become `NestedStore`,
- `simpy.Container` can become `NestedContainer`,
- `env.timeout(...)` becomes `env.nested_timeout(...)` where residual resampling
  matters,
- `env.run()` becomes `env.nested_run()` after branch conditions are configured.

## Three Objects To Remember

`NestedEnvironment`
: SimPy environment wrapper with branch configuration, branch-safe timeout
  helpers, and run/replay entry points.

`NestedResource`
: Instrumented resource that records queue transitions and exposes watcher
  callbacks used by branch boundaries.

`NestedPreemptiveResource`, `NestedStore`, `NestedContainer`
: Instrumented SimPy primitives for priority/preemption, buffered item flow, and
  shared-level state.

`env.nested_timeout(...)`
: Distribution-aware sleep helper that can resample residual time correctly
  after a fork.

## Typical Flow

```python
env = NestedEnvironment()
server = NestedResource(env, capacity=1, nested_id="srv")

env.set_nested_triggering_objects(nested_id="srv")
env.set_nesting_conditions({"on": "arrival", "frequency": 1})
env.set_inner_repetitions(2)
env.set_inner_stopping_condition(relative_time=5.0)

env.nested_run()
```

## Where To Go Next

- For the main concept guides, go to {doc}`topical-guides/index`.
- For the public examples story, go to {doc}`official-parity/index`.
- For the SimPy-facing API surface, go to {doc}`api/index`.
- For the runtime model, go to {doc}`architecture`.
