# Stopping conditions

NestedSimPy controls both:

- when the outer trajectory stops, and
- when each inner simulation stops after a fork.

## Outer Stop Rules

Use `set_outer_stopping_condition(...)` to bound the outer simulation by time or by an
arrival count.

```python
env.set_outer_stopping_condition(timeout=10.0, max_arrivals=8)
```

The outer trajectory ends when one of the configured conditions fires.

## Inner Stop Rules

Use `set_inner_stopping_condition(...)` to control how long child branches keep
running after a boundary.

Typical options include:

- `relative_time=...`
- `absolute_time=...`
- `triggering_customer_departs=True`

Example:

```python
env.set_inner_stopping_condition(
    relative_time=5.0,
    triggering_customer_departs=True,
)
```

That configuration says:

- keep each branch alive for up to five simulated time units,
- but also stop as soon as the anchor customer finishes, if that happens first.

## User-Level Postprocessing

After `nested_run()`, packaged outputs can be postprocessed automatically.

You can:

- set general output behavior with `set_post_processing_options(...)`,
- register a custom metric hook with `set_postprocessor(...)`.

## Replay

To re-run a specific branch deterministically, use `run_single_path(...)`.

```python
env.run_single_path(trigger_index=2, branch_index=0, seed=1234)
```

This is useful when a full branching run has already identified a path you want
to inspect in isolation.

## Practical Rule

Keep the outer stop rules simple, then make the inner stop rules express the
counterfactual horizon you actually care about.
