# Triggering events

NestedSimPy branches when the configured nesting condition fires.

The main configuration calls are:

- `env.set_triggering_objects(...)`
- `env.set_triggering_conditions(...)`

## Triggering objects

Triggering objects tell the runtime which resource, store, or container should
be watched for branch boundaries.

Typical examples:

```python
env.set_triggering_objects(nested_id="srv")
env.set_triggering_objects(nested_id=["srv_a", "srv_b"])
```

The `nested_id` is the identifier you gave the object when constructing it —
`NestedResource(env, capacity=1, nested_id="srv")` — and it is how the object
is referred to everywhere else: in this call, in trigger specs, and in the
output columns (see {doc}`From SimPy to NestedSimPy <branching-model>`). If
you never call `set_triggering_objects`, the default is a single object named
`"srv"`; a run whose objects use other ids must set this explicitly.

With **several** triggering objects, the configured condition is armed on each
of them independently. Whichever object fires first causes the fork, and that
object becomes the *triggering object of that fork* — the one the anchor
customer and the state-based inner stop rules refer to (see
{doc}`Stopping conditions <stop-rules-replay>`). The fork snapshot itself
always captures the state of *all* the triggering objects, so the branches
resume the full system consistently.

## Arrival triggers

Arrival-based branching is the simplest mode and the most common starting point.

```python
env.set_triggering_conditions({"on": "arrival", "frequency": 1})
```

That means branch on every arrival at the primary triggering object.

You can also use `nth` instead of `frequency`.

The condition is a plain dict with these keys:

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `on` | `str` | — (required) | Which built-in boundary to watch — see the table below. An `"arrival"` is the moment a request is submitted to the object (the customer joins). |
| `frequency` / `nth` | `int` | `1` | Fire on every *n*-th matching occurrence. The two names are aliases; `frequency` is the preferred spelling. |
| `resource` | `str` or list | `None` | Optional filter: only occurrences at this triggering object (by `nested_id`) count. Useful when several triggering objects are configured but only one should fork. |

The counter behind `frequency` restarts after each fork: `{"on": "arrival",
"frequency": 3}` forks at every third arrival *since the previous fork* (for a
pure arrival trigger that is the same as every third arrival overall).

`"arrival"` is one of several built-in boundaries; the same dict shape works
for all of them:

| `on` value | Applies to | Fires when |
| --- | --- | --- |
| `"arrival"` | resource | a request is submitted (a customer joins the queue or grabs a free server) |
| `"service_start"` | resource | a request is granted (a customer enters service) |
| `"service_end"` | resource | a request is released (a customer's service completes) |
| `"capacity_change"` | resource | the object's capacity changes |
| `"store_put"` / `"store_get"` | store | a put / get on the store completes |
| `"container_put"` / `"container_get"` | container | a put / get on the container completes |

A complete minimal example — the M/M/1 model from the
{doc}`Simple example <../simple-example>`, branching on every second arrival:

```python
import nestedsimpy


def customer(env, server):
    with server.request() as request:
        yield request
        yield env.nested_timeout({"distribution": "exponential", "lambda": 4.0})


def arrivals(env, server):
    while True:
        yield env.nested_timeout({"distribution": "exponential", "lambda": 3.0})
        env.process(customer(env, server))


env = nestedsimpy.NestedEnvironment()
server = nestedsimpy.NestedResource(env, capacity=1, nested_id="srv")
env.process(arrivals(env, server))

env.set_output_options(out_dir="nested_output/mm1_every2nd", gzip_trace=False)
env.set_rng("independent")
env.set_outer_seed(42)
env.set_triggering_objects(nested_id="srv")
env.set_triggering_conditions({"on": "arrival", "frequency": 2})
env.set_inner_repetitions(3)
env.set_inner_stopping_condition(relative_time=5.0)
env.set_outer_stopping_condition(timeout=10.0)
env.nested_run()
```

## State-predicate triggers

State-triggered branching lets the model fork when the latest observed state of
an instrumented object satisfies a predicate.

```python
env.set_triggering_conditions(
    {
        "on": "state_predicate",
        "resource": "srv",
        "predicate": lambda state: state["queue_len"] >= 2,
    }
)
```

This is useful when the boundary of interest is not “the nth arrival” but
something like “the queue first becomes nontrivial.”

For `on="state_predicate"` the dict takes `predicate` (required) in addition to
the shared keys above: here `resource` names which triggering object the
predicate watches, and `frequency`/`nth` counts *rising edges* — with
`"frequency": 2`, every second time the predicate flips from false to true.

### What the predicate receives

Every time the watched object goes through a state transition, NestedSimPy
evaluates the predicate with one argument — here called `state`. It is a plain
Python dict: a snapshot of the triggering object's state at that event moment
(the object's `describe_state()` output). Read whatever fields you need and
return `True` to branch; the trigger fires on the *rising edge*, i.e. the
moment the predicate flips from false to true, so a queue that stays long does
not re-trigger on every subsequent event.

(The predicate may also accept `(state, resource)` or `(state, resource, env)`
when it needs the object or the environment as extra context; the
one-argument form is the common case.)

For a `NestedResource` (and `NestedPreemptiveResource`) the snapshot contains:

| Key | Meaning |
| --- | --- |
| `current_time` | Simulation time at which the snapshot was taken. |
| `queue_len` | Number of customers waiting (excluding those in service). |
| `customers_in_queue` | The waiting customers, as `[cust_id, arrival_time]` pairs. |
| `in_service_customer_id` | Id of the customer at the head of service, or `None` when idle. |
| `in_service_arrival_time` | That customer's arrival time (or `None`). |
| `in_service_start_time` | When that customer's service started (or `None`). |
| `in_service_customers` | Every customer in service, as dicts with `cust_id`, `arrival_time`, `service_start_time` (plus `priority` on a preemptive resource). |

A `NestedStore` snapshot instead carries `current_time`, `items`,
`item_count`, `put_queue_len`, `get_queue_len`, `queue_len` (an alias for
`get_queue_len`) and `capacity`; a `NestedContainer` snapshot carries
`current_time`, `level`, `capacity`, `get_queue_len`, `put_queue_len` and
`queue_len`.

A second worked example — branch at the moment the system empties out (no one
waiting and no one in service):

```python
env.set_triggering_conditions(
    {
        "on": "state_predicate",
        "resource": "srv",
        "predicate": lambda state: state["queue_len"] == 0
        and state["in_service_customer_id"] is None,
    }
)
```

Note that the predicate is also evaluated once when the trigger is armed, so if
the system *starts* empty this example fires immediately at time 0. If that is
not intended, include a condition that cannot hold initially (for example,
require `state["current_time"] > 0`).

## Event triggers

Event-based branching uses the lightweight event bus exposed by `publish_event`
(importable from `nestedsimpy`). The model *publishes* a named event wherever a
decision point occurs in its own logic; the trigger *subscribes* to that name
and forks the inner simulations when a matching event arrives:

```python
from nestedsimpy import publish_event

def controller(env):
    while True:
        yield env.timeout(1.0)
        # Anywhere in your model code: announce a decision point by name.
        publish_event("control_signal", {"kind": "go", "time": env.now})

env.set_triggering_conditions(
    {
        "on": "event",
        "name": "control_signal",
        "predicate": lambda payload: payload["kind"] == "go",
    }
)
```

How it works:

- **`publish_event(name, payload)`** takes an event name and an optional
  `payload` -- a plain dict that you, the publisher, fill with whatever
  describes the moment (there are no required keys; `payload` defaults to an
  empty dict).
- **`name`** filters which published events the trigger listens to; other
  event names are ignored.
- **`predicate`** receives that same payload dict and returns `True` to fire.
  Omit it to fire on every published event with that name. (The predicate may
  optionally accept `(payload, resource)` or `(payload, resource, env)` if it
  needs more context.)
- **`nth`** (optional, like the other trigger kinds) fires only on every
  n-th matching event.

Each firing forks the configured inner simulations at the moment of
publication, exactly as an arrival trigger would. This is useful when the
boundary is model-defined -- a control decision, a review epoch, a batch
completing -- rather than directly tied to a single queue primitive. After the
run, each firing appears as one row in `OutputManager.export_triggers` (next
section).

## Collecting the triggering events

After the run, `OutputManager.export_triggers` collects the triggering events
into one compact table — one row per trigger, with the fork time, the state at
that moment, the number of inner simulations and their averaged outcomes:

```python
om = OutputManager("nested_output/mm1")
rows = om.export_triggers()            # list of dicts, one per triggering event
om.export_triggers("triggers.csv")     # ... and write a CSV
```

See {doc}`Exporting data <traces-and-outputs>` for the full column list.

## Choosing a first trigger

If you are introducing NestedSimPy to an existing SimPy model:

- start with arrival triggers,
- switch to state predicates when queue conditions matter more than counts,
- use event triggers when the natural decision point is already explicit in your
  model logic.
