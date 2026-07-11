---
orphan: true
---

# NestedSimPy in 10 Minutes

NestedSimPy is easiest to understand as a small layer on top of SimPy:

1. Build your model with a `NestedEnvironment`.
2. Replace plain SimPy primitives with instrumented ones such as `NestedResource`, `NestedPreemptiveResource`, `NestedStore`, or `NestedContainer`.
3. Use `env.nested_timeout(...)` instead of raw `env.timeout(...)` where branch-safe sleeps matter.
4. Declare when branches should be launched.
5. Run once and inspect packaged outputs.

## Install

NestedSimPy requires Python 3.9+ and runs on top of SimPy. Install it from
GitHub — either with `pip` directly, or by cloning the repository.

**With pip:**

```bash
pip install "git+https://github.com/NestedSimPy/nestedsimpy.git"
```

**Or download the source and install it:**

```bash
git clone https://github.com/NestedSimPy/nestedsimpy.git
cd nestedsimpy
pip install .
```

After either, `import nestedsimpy` works from anywhere. For the optional Plotly
figures, install the extra: `pip install "nestedsimpy[plot] @ git+https://github.com/NestedSimPy/nestedsimpy.git"`.

```{note}
NestedSimPy is under active development. The code repository and PyPI release are
not public yet, so the `git+https://…` and `pip install nestedsimpy` commands
above will work only once the package is published. Until then, try it in the
browser via the [Simple example](simple-example) Colab.
```

## First Run

The smallest walkthrough is the branching M/M/1 demo. From a clone of the
repository:

```bash
python simpy_examples/mm1_nested.py
```

It runs the outer SimPy trajectory and, at each arrival, launches inner simulations
that each explore a possible future from that state.

## Compare Against Plain SimPy

```bash
python simpy_examples/mm1_plain.py     # plain SimPy M/M/1 baseline
python simpy_examples/mm1_nested.py    # the same model, under NestedSimPy
```

The plain script is a standard SimPy M/M/1. The NestedSimPy version keeps the
same model and adds branching — see {doc}`simple-example` for the line-by-line
comparison.

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
  callbacks used by trigger events.

`NestedPreemptiveResource`, `NestedStore`, `NestedContainer`
: Instrumented SimPy primitives for priority/preemption, buffered item flow, and
  shared-level state.

`env.nested_timeout(...)`
: Distribution-aware sleep helper that can resample residual time correctly
  after a trigger point.

## Typical Flow

```python
env = NestedEnvironment()
server = NestedResource(env, capacity=1, nested_id="srv")

env.set_triggering_objects(nested_id="srv")
env.set_triggering_conditions({"on": "arrival", "frequency": 1})
env.set_inner_repetitions(2)
env.set_inner_stopping_condition(relative_time=5.0)

env.nested_run()
```

## Where To Go Next

- For the main concept guides, go to {doc}`topical-guides/index`.
- For the public examples story, go to {doc}`official-parity/index`.
- For the runtime, the API surface, and the raw data format, go to
  {doc}`api/index`.
