# SimPy Core API

This page documents the SimPy-facing public surface of NestedSimPy:
the environment, instrumented primitives, sleep helpers, the branch driver,
the event bus, state and trace utilities, and the typed configuration structs.

```{note}
Signatures below describe the **public interface**. Implementation details are
intentionally omitted.
```

## Environment

### `NestedEnvironment`

> SimPy environment wrapper exposing nested-sim convenience methods. It keeps
> track of registered resources, encapsulates branching configuration, and
> drives nested runs.

**Resources & timeouts**

```python
nested_timeout(specification, *, label=None, metadata=None) -> simpy.events.Event
register_resource(resource, name=None)
register(resource, name=None)            # fluent mirror of nestedsimpy.register
get_resource(name)
iter_resources() -> Iterable[tuple[str, Any]]
```

**Branching configuration**

```python
configure_branching(*, inner_repetitions, nesting_triggers='srv', outer_time=None,
                    outer_arrivals_ge=None, nesting_conditions={'on': 'arrival', 'nth': 1},
                    rng='CRN', outer_seed=2025, inner_seed=None, policy_fn=None,
                    out_dir='./out/simpy', gzip_trace=True) -> None
set_inner_repetitions(count)
set_rng(mode='CRN', *, policy_fn=None)
set_outer_seed(seed)
set_inner_seed(seed)
set_nesting_triggers(*names, nested_id=None)
set_nested_triggering_objects(*names, nested_id=None)   # preferred alias
set_outer_stopping_condition(*, timeout=None, max_arrivals=None)
set_outer_timeout(*, time=None, arrivals=None)          # back-compat wrapper
set_nesting_conditions(spec)
set_output_options(*, out_dir='./out/simpy', gzip_trace=True,
                   branch_record_mode='per_branch', branch_detail='anchor',
                   detail_anchors=None, full_include_state=False, write_outer_trace=True)
set_inner_stopping_condition(*, relative_time=None, absolute_time=None,
                            triggering_customer_departs=False,
                            requesting_customer_departs=None, anchor_done=None, event=None)
clear_branching()
```

**Post-processing hooks**

```python
set_post_processing_options(**options)
get_post_processing_options() -> dict
set_postprocessor(fn, *, output_name='user_metrics.json', **options)
clear_postprocessor()
set_user_output_enabled(enabled)
should_emit_user_output() -> bool
```

**Run**

```python
nested_run(**overrides) -> None
run_single_path(*, trigger_index, branch_index, seed=None, **overrides) -> None
```

## SimPy Hooks

Instrumented drop-in replacements for SimPy primitives. Each logs queue
transitions, emits structured trace events, and notifies deterministic
boundary watchers.

### `NestedResource` / `NestedPreemptiveResource`

```python
watch(cb) -> Callable[[], None]      # observe every boundary event
queue_length() -> int                # waiting jobs (excludes in-service)
describe_state() -> dict             # exported state schema
request(*args, job_id=None, tags=None, **kwargs) -> simpy.events.Event
release(req) -> simpy.events.Event
set_capacity(new_capacity) -> None   # emits 'capacity_changed'
```

### `NestedStore`

```python
watch(cb) -> Callable[[], None]
describe_state() -> dict
put(item) -> simpy.events.Event
get() -> simpy.events.Event
```

### `NestedContainer`

```python
watch(cb) -> Callable[[], None]
describe_state() -> dict
put(amount) -> simpy.events.Event
get(amount) -> simpy.events.Event
```

### `register`

```python
register(resource, nested_id=None, *, name=None)
```
> Register `resource` under `nested_id` and return it for fluent usage.

## Sleep Helpers

```python
safe_sleep(env, distribution, *, label=None, metadata=None, ...) -> simpy.events.Event
resolve_distribution(spec) -> SleepDistribution
```

- **`safe_sleep`** — return a branch-friendly event that sleeps according to
  `distribution`. When an inner simulation resumes a sleep already in progress, the
  remaining duration is drawn from the *conditional* distribution `S | S > elapsed`.
- **`resolve_distribution`** — coerce `spec` into a {class}`SleepDistribution`.
- **`SleepDistribution`** — encapsulates sampling logic for safe sleeps.

## Branch Driver

```python
branch_after_simpy(env, *, K, primary='srv', outer_time=None, outer_arrivals_ge=None,
                   branch_on={'on': 'arrival', 'nth': 1}, inner_time_horizon=None,
                   inner_absolute_time=None, inner_anchor_done=False, inner_state_spec=None,
                   rng='CRN', seed=2025, inner_seed=None, policy_fn=None,
                   out_dir='./out/simpy', gzip_trace=True, select_branch=None,
                   skip_fork_if_anchor_in_service=False, branch_record_mode='per_branch',
                   branch_detail='anchor', detail_anchors=None, full_include_state=False,
                   write_outer_trace=True) -> None
```
> Explore nested branches from a SimPy environment at configurable boundaries.

```python
branch_after(env_or_sim, backend='auto', **kwargs) -> None
```
> Dispatch to the appropriate backend-specific branching API.

## Events

```python
publish_event(name, payload=None) -> None
subscribe_event(name, callback) -> Callable[[], None]
```
> A lightweight global event bus. `subscribe_event` returns an unsubscribe
> callable.

## State

```python
build_uid(outer_id, j, k, cust_id) -> str
```
> Construct a stable, namespace-qualified identifier for a customer across the
> outer simulation and its nested branches.

## Trace

```python
attach_trace(env_or_sim, sink, branch_meta) -> None
detach_trace(env_or_sim, stop_reason=None) -> None
trace_emit(t, type, **payload) -> None          # module-level emit alias
```

### `JsonlTrace`

> Persistent JSON Lines trace sink backed by the filesystem.

```python
emit(t, type, **payload) -> None
flush() -> None       # fork-safe manual flush
close() -> None
```

## Types

### `BoundarySpec`

> Configuration describing how and when to trigger branching operations.

### `StartStopSpec`

> Declarative composition of stop rules for inner simulations.
