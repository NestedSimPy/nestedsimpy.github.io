# Converting code

The core mental model is:

- keep the SimPy process logic,
- replace key infrastructure with branch-aware equivalents,
- run one outer trajectory,
- fork child futures when a declared boundary fires.

## From Plain SimPy To NestedSimPy

The usual substitutions are:

| Plain SimPy | NestedSimPy |
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

## Delays as distributions

The key behavioural change is how delays are written. In plain SimPy a delay is
a number that has **already been drawn**:

```python
yield env.timeout(random.expovariate(rate))   # the value is fixed right here
```

NestedSimPy takes the **distribution** instead:

```python
yield env.nested_timeout({"distribution": "exponential", "lambda": rate})
```

Passing the distribution — rather than a pre-sampled value — is what makes
branching meaningful. When the outer simulation forks at a triggering event, any
delay already in progress is **resampled** for each inner simulation, so the
branches explore genuinely different futures instead of replaying one fixed
draw. The resample is **conditional on the time already elapsed**: an
exponential is memoryless, so its residual is a fresh exponential, while a
uniform or normal delay is redrawn from its left-truncated tail — an in-progress
service is *continued* correctly, not restarted.

Supported specifications:

| Distribution | Spec |
| --- | --- |
| Exponential | `{"distribution": "exponential", "lambda": rate}` |
| Uniform | `{"distribution": "uniform", "low": a, "high": b}` |
| Normal (truncated at 0) | `{"distribution": "normal", "mean": mu, "std": sigma}` |
| Log-normal | `{"distribution": "log-normal", "mu": mu, "sigma": sigma}` |
| Deterministic | `{"distribution": "deterministic", "value": d}` |

Capped (truncated) exponential and integer-uniform variants are also available; see `nestedsimpy.sleep.resolve_distribution` for the full set.

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
env.set_inner_repetitions(3)
env.set_inner_stopping_condition(relative_time=5.0, triggering_customer_departs=True)

env.nested_run()
```

## Where To Go Next

- For the boundary language, go to {doc}`branch-triggers`.
- For stop conditions, go to {doc}`stop-rules-replay`.
- For exporting data, go to {doc}`traces-and-outputs`.
