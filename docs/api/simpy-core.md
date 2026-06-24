# SimPy Core API

This page documents the SimPy-facing public surface of NestedSimPy: the
environment, instrumented primitives, sleep helpers, the branch driver, the
event bus, and state/trace/typed-config utilities. Each signature is followed by
what it does.

```{note}
For a guided introduction rather than a reference, start with
{doc}`Using NestedSimPy <../topical-guides/index>`.
```

## Environment

### `NestedEnvironment`

A SimPy `Environment` wrapper that tracks registered resources, holds the
branching configuration, and drives nested runs. Construct it like a SimPy
environment: `env = NestedEnvironment()`.

**Resources & timeouts**

```python
nested_timeout(specification, *, label=None, metadata=None) -> simpy.events.Event
register_resource(resource, name=None)
register(resource, name=None)            # fluent mirror of nestedsimpy.register
get_resource(name)
iter_resources() -> Iterable[tuple[str, Any]]
```

- **`nested_timeout`** — sleep for a delay drawn from `specification` (a
  distribution spec, not a pre-sampled number) so the residual can be resampled
  per branch on a fork. See {doc}`Converting code <../topical-guides/branching-model>`.
- **`register_resource`** / **`register`** — register an instrumented resource
  under a name for later lookup; `register` returns it for fluent chaining.
- **`get_resource`** / **`iter_resources`** — look up one registered resource by
  name, or iterate `(name, resource)` pairs.

**Branching configuration**

```python
set_inner_repetitions(count)
set_rng(mode='CRN', *, policy_fn=None)
set_outer_seed(seed)
set_inner_seed(seed)
set_nested_triggering_objects(*names, nested_id=None)   # which objects can trigger
set_nesting_conditions(spec)                            # when a trigger fires a branch
set_inner_stopping_condition(*, relative_time=None, absolute_time=None,
                            triggering_customer_departs=False, event=None)
set_outer_stopping_condition(*, timeout=None, max_arrivals=None)
set_output_options(*, out_dir='./out/simpy', gzip_trace=True, ...)
clear_branching()
```

- **`set_inner_repetitions`** — how many inner simulations fork at each
  triggering event.
- **`set_rng`** — RNG strategy: `'CRN'` (common random numbers across branches)
  or `'independent'` (each branch its own stream); `policy_fn(k, env)` supplies a
  per-branch policy for rollout/lookahead.
- **`set_outer_seed`** / **`set_inner_seed`** — seed the outer baseline run, and
  optionally fix the inner-branch seed base.
- **`set_nested_triggering_objects`** — which instrumented object(s) are watched
  for triggers. See {doc}`Triggering events <../topical-guides/branch-triggers>`.
- **`set_nesting_conditions`** — the boundary that fires a branch (on an arrival,
  a state predicate, or a published event).
- **`set_inner_stopping_condition`** — when each inner branch stops (a relative
  or absolute time, the anchor customer departing, or a `StartStopSpec`). See
  {doc}`Stopping conditions <../topical-guides/stop-rules-replay>`.
- **`set_outer_stopping_condition`** — when the outer run stops (a timeout or an
  arrival count).
- **`set_output_options`** — where traces are written, whether they are gzipped,
  and the branch-record layout.
- **`clear_branching`** — forget the stored branching configuration.

```{note}
`configure_branching(...)` and `set_outer_timeout(...)` are one-call /
back-compatible wrappers over the methods above; `set_nesting_triggers` is the
older name for `set_nested_triggering_objects`.
```

**Post-processing & run**

```python
set_postprocessor(fn, *, output_name='user_metrics.json', **options)
set_post_processing_options(**options)
set_user_output_enabled(enabled)
nested_run(**overrides) -> None
run_single_path(*, trigger_index, branch_index, seed=None, **overrides) -> None
```

- **`set_postprocessor`** — register a user hook that runs after packaging to
  produce a custom metric/dataset (e.g. the bundled wait-time hook). See
  {doc}`Exporting data <../topical-guides/traces-and-outputs>`.
- **`set_post_processing_options`** — packaging preferences (e.g. whether to
  package and print outputs); `get_post_processing_options()` reads them back.
- **`set_user_output_enabled`** — toggle the example `print`s (inner branches are
  silenced by default so forked runs don't spam stdout).
- **`nested_run`** — run the configured nested simulation.
- **`run_single_path`** — re-run one branch `(trigger_index, branch_index)`
  deterministically, for inspecting a path a full run surfaced.

## Instrumented primitives

Drop-in replacements for SimPy primitives. Each records queue transitions, emits
structured trace events, and notifies the boundary watchers that drive
branching. Construct them like their SimPy counterparts plus a `nested_id`, e.g.
`NestedResource(env, capacity=1, nested_id="srv")`.

### `NestedResource` / `NestedPreemptiveResource`

```python
request(*args, job_id=None, tags=None, **kwargs) -> simpy.events.Event
release(req) -> simpy.events.Event
queue_length() -> int
set_capacity(new_capacity) -> None
describe_state() -> dict
watch(cb) -> Callable[[], None]
```

- **`request`** / **`release`** — the SimPy request/release, instrumented to
  attach metadata and emit trace markers. `NestedPreemptiveResource` adds
  priority/preemption (there is no separate `NestedPriorityResource`).
- **`queue_length`** — waiting jobs, excluding those in service.
- **`set_capacity`** — change the capacity at runtime (emits `capacity_changed`).
- **`describe_state`** — the exported state schema for this object.
- **`watch`** — register a callback fired on every boundary event; returns an
  unsubscribe callable.

### `NestedStore` / `NestedContainer`

```python
put(item) -> simpy.events.Event       # NestedStore: an item
get() -> simpy.events.Event
put(amount) -> simpy.events.Event      # NestedContainer: an amount
get(amount) -> simpy.events.Event
describe_state() -> dict
watch(cb) -> Callable[[], None]
```

- **`NestedStore.put` / `.get`** — submit/withdraw one item, emitting put/get
  lifecycle events (a `store_put` can be a triggering event).
- **`NestedContainer.put` / `.get`** — add/remove an amount of bulk material.
- **`describe_state`** / **`watch`** — as above.

### `register`

```python
register(resource, nested_id=None, *, name=None)
```

- Register `resource` under `nested_id` and return it for fluent usage.

## Sleep helpers

```python
safe_sleep(env, distribution, *, label=None, metadata=None, ...) -> simpy.events.Event
resolve_distribution(spec) -> SleepDistribution
```

- **`safe_sleep`** — the branch-friendly sleep underneath `nested_timeout`. When
  an inner branch resumes a sleep already in progress, the remaining duration is
  drawn from the *conditional* distribution `S | S > elapsed`.
- **`resolve_distribution`** — coerce a spec dict into a `SleepDistribution`.
- **`SleepDistribution`** — encapsulates the (conditional) sampling logic.

## Branch driver

```python
branch_after_simpy(env, *, K, primary='srv', branch_on={'on': 'arrival', 'nth': 1},
                   inner_time_horizon=None, rng='CRN', seed=2025, policy_fn=None,
                   out_dir='./out/simpy', ...) -> None
branch_after(env_or_sim, backend='auto', **kwargs) -> None
```

- **`branch_after_simpy`** — the low-level driver `nested_run` calls: run the
  outer simulation, fork `K` children at each boundary, and write traces and
  manifests. Most users configure `NestedEnvironment` and call `nested_run`
  instead of calling this directly.
- **`branch_after`** — dispatch to the appropriate backend (currently SimPy).

## Events

```python
publish_event(name, payload=None) -> None
subscribe_event(name, callback) -> Callable[[], None]
```

- A lightweight global event bus. Publish a named event (which can be used as a
  branch trigger); `subscribe_event` returns an unsubscribe callable.

## State

```python
build_uid(outer_id, j, k, cust_id) -> str
```

- Build a stable, namespace-qualified id for a customer across the outer
  simulation and its branches.

## Trace

```python
attach_trace(env_or_sim, sink, branch_meta) -> None
detach_trace(env_or_sim, stop_reason=None) -> None
trace_emit(env_or_sim, type, **payload) -> None   # module-level emit alias
```

- **`attach_trace`** / **`detach_trace`** — bind a trace sink to a run and close
  it (recording the stop reason).
- **`trace_emit`** — emit one event to the run's attached sink.

### `JsonlTrace`

A persistent JSON Lines trace sink backed by the filesystem.

```python
emit(t, type, **payload) -> None
flush() -> None       # fork-safe manual flush
close() -> None
```

## Types

- **`BoundarySpec`** — a `TypedDict` describing how and when to trigger
  branching (the value passed to `set_nesting_conditions`).
- **`StartStopSpec`** — a declarative composition of inner stop rules
  (`time_ge`, `queue_ge`, `system_empty`, a `custom` predicate, `any_of`,
  `all_of`); passed as the `event=` of `set_inner_stopping_condition`.
