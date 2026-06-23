# Triggering events

NestedSimPy branches when the configured nesting condition fires.

The main configuration calls are:

- `env.set_nested_triggering_objects(...)`
- `env.set_nesting_conditions(...)`

## Triggering Objects

Triggering objects tell the runtime which resource, store, or container should
be watched for branch boundaries.

Typical examples:

```python
env.set_nested_triggering_objects(nested_id="srv")
env.set_nested_triggering_objects(nested_id=["srv_a", "srv_b"])
```

## Arrival Triggers

Arrival-based branching is the simplest mode and the most common starting point.

```python
env.set_nesting_conditions({"on": "arrival", "frequency": 1})
```

That means branch on every arrival at the primary triggering object.

You can also use `nth` instead of `frequency`.

## State-Predicate Triggers

State-triggered branching lets the model fork when the latest observed state of
an instrumented object satisfies a predicate.

```python
env.set_nesting_conditions(
    {
        "on": "state",
        "resource": "srv",
        "predicate": lambda snap: snap["queue_len"] >= 2,
    }
)
```

This is useful when the boundary of interest is not “the nth arrival” but
something like “the queue first becomes nontrivial.”

## Event Triggers

Event-based branching uses the lightweight event bus exposed by `publish_event`.

```python
publish_event("control_signal", {"kind": "go", "time": env.now})

env.set_nesting_conditions(
    {
        "on": "event",
        "name": "control_signal",
        "predicate": lambda payload: payload["kind"] == "go",
    }
)
```

This is useful when the boundary is model-defined rather than directly tied to a
single queue primitive.

## Choosing A First Trigger

If you are introducing NestedSimPy to an existing SimPy model:

- start with arrival triggers,
- switch to state predicates when queue conditions matter more than counts,
- use event triggers when the natural decision point is already explicit in your
  model logic.
