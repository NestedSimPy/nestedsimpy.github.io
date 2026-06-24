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
- `triggering_customer_departs=True` — stop once the anchor (triggering) customer finishes.

```python
env.set_inner_stopping_condition(
    relative_time=5.0,
    triggering_customer_departs=True,
)
```

That configuration keeps each branch alive for up to five simulated time units,
but also stops as soon as the anchor customer finishes — whichever comes first.

### Custom and composed conditions

The stop rule is not limited to those flags. Pass `event=` a `StartStopSpec` to
stop on the system state or on your own predicate — and compose several with
`any_of` / `all_of`:

```python
from nestedsimpy import StartStopSpec

env.set_inner_stopping_condition(
    event=StartStopSpec(
        any_of=[
            StartStopSpec(queue_ge=10),         # the queue reaches 10, or
            StartStopSpec(system_empty=True),   # the system empties, or
            StartStopSpec(custom=my_predicate),  # a custom predicate returns True
        ]
    ),
)
```

A `StartStopSpec` can set `time_ge`, `queue_ge`, `system_empty`, a `custom`
predicate (any callable returning a bool, evaluated after each event), or nest
child specs with `any_of` / `all_of`. You can also hand `event=` a raw SimPy
event (or a callable returning one) to stop the branch when that event fires.

## Practical rule

Keep the outer stop rules simple, then make the inner stop rules express the
counterfactual horizon you actually care about.
