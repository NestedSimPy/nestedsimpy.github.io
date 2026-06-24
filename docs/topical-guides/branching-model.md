# From SimPy to NestedSimPy

We transform a given SimPy simulation code to NestedSimPy by following three
steps:

1. **Replacing SimPy objects** with corresponding NestedSimPy objects,
2. **Replacing the timeout function call**, and
3. **Configuring the nested simulation parameters**.

The process logic itself often stays very close to the original SimPy model — we
keep the SimPy process functions and change the infrastructure around them.

## 1. Replacing SimPy objects with corresponding NestedSimPy objects

Swap the SimPy environment, its primitives, and the run call for their
branch-aware equivalents:

| Plain SimPy | NestedSimPy |
| --- | --- |
| `simpy.Environment()` | `NestedEnvironment()` |
| `simpy.Resource(...)` | `NestedResource(...)` |
| `simpy.PreemptiveResource(...)` | `NestedPreemptiveResource(...)` |
| `simpy.Store(...)` | `NestedStore(...)` |
| `simpy.Container(...)` | `NestedContainer(...)` |
| `env.run()` | `env.nested_run()` |

There is not currently a separate `NestedPriorityResource` class. Priority-aware
service is handled through `NestedPreemptiveResource`, which preserves SimPy's
priority/preemption request path while adding tracing and branch hooks.

The wrapped objects play the same roles as before:

`NestedEnvironment`
: Stores branching configuration and exposes branch-aware entry points such as
  `nested_run()` and `run_single_path(...)`.

`NestedResource`, `NestedPreemptiveResource`, `NestedStore`, `NestedContainer`
: Wrapped SimPy primitives that emit structured state transitions and watcher
  callbacks.

## 2. Replacing the timeout function call

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

## 3. Configuring the nested simulation parameters

Finally, declare how the nested simulation runs — what triggers branching, how
many inner simulations to fork, and when the inner and outer runs stop. (Your own
SimPy processes — the arrival generator and the customer logic — are omitted
here; the {doc}`Simple example <../simple-example>` is the full runnable file.)

```python
env = NestedEnvironment()
server = NestedResource(env, capacity=1, nested_id="srv")
env.process(arrivals(env, server))             # your model's processes

env.set_output_options(out_dir="out/mm1_simpy", gzip_trace=False)
env.set_rng("independent")                     # each branch draws its own future
env.set_triggering_objects(nested_id="srv")
env.set_triggering_conditions({"on": "arrival", "frequency": 1})
env.set_inner_repetitions(3)
env.set_inner_stopping_condition(relative_time=5.0, triggering_customer_departs=True)
env.set_outer_stopping_condition(timeout=10.0)
env.nested_run()
```

`set_rng` chooses how the branches sample: `"independent"` gives each inner its
own random stream (so they explore different futures), while `"CRN"` shares one
stream across branches (useful when comparing policies on the same randomness).
