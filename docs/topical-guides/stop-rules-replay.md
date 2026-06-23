# Stopping conditions

NestedSimPy controls both when the outer trajectory stops and when each inner
simulation stops after a fork.

## Outer stop rules

Use `set_outer_stopping_condition(...)` to bound the outer simulation by time or
by an arrival count:

```python
env.set_outer_stopping_condition(timeout=10.0, max_arrivals=8)
```

The outer trajectory ends when one of the configured conditions fires.

## Inner stop rules

Use `set_inner_stopping_condition(...)` to control how long each branch keeps
running after a triggering event. Typical options:

- `relative_time=...` — run for this many time units past the fork,
- `absolute_time=...` — run until this absolute simulation time,
- `triggering_customer_departs=True` — stop once the anchor customer finishes.

```python
env.set_inner_stopping_condition(
    relative_time=5.0,
    triggering_customer_departs=True,
)
```

That configuration keeps each branch alive for up to five simulated time units,
but also stops as soon as the anchor customer finishes — whichever comes first.

## Practical rule

Keep the outer stop rules simple, then make the inner stop rules express the
counterfactual horizon you actually care about.

## Next

- {doc}`visualization` — plot the outer trajectory and inner branches.
- {doc}`traces-and-outputs` — export them as datasets.
