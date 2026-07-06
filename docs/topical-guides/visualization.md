# Visualization

Once a nested run has finished, an `OutputManager` reads its output folder and
plots the trajectories — the single **outer** simulation and the **inner**
simulations forked at each **triggering event**. It works post-hoc, so the same
run can be revisited in a fresh session.

## Loading a run

```python
from nestedsimpy import OutputManager

om = OutputManager("nested_output/mm1")
```

The argument can be the run directory, its `exports`/`raw` directory, or a
parent directory containing several runs (the most recent is chosen). If the run
has not been packaged yet, the manager packages it on first use.

The triggering events are discovered automatically:

```python
om.trigger_ids          # e.g. [0, 1, 2, ...]  (anchor customer ids)
om.triggers()           # TriggerInfo(trigger_id, boundary, branch_time, inner_ids)
```

`trigger_ids` are the **anchor customer ids**, so they are not necessarily
consecutive — a run that forks at every third arrival has ids `[2, 5, 8, ...]`.
Every `trigger_id=` argument below expects one of these ids. `triggers()`
returns one `TriggerInfo` per triggering event, carrying:

| Field | Meaning |
| --- | --- |
| `trigger_id` | The anchor customer id (the same id space as `trigger_ids`). |
| `boundary` | Which boundary fired (e.g. `"arrival"`). |
| `branch_time` | The simulation time of the fork. |
| `inner_ids` | The ids of the inner simulations forked there, `[0, 1, ..., K-1]` — what `inner_id=` expects. |

The plotting methods rely on optional dependencies: the `*_interactive`
methods (and `visualize_inner`) need **plotly**, and `visualize_outer_static`
needs **matplotlib**. A clear `RuntimeError` names the missing package if it
is not installed.

## The outer trajectory

`visualize_outer_static` (matplotlib image) and `visualize_outer_interactive`
(Plotly) plot a chosen metric along the outer path, with a marker at each
triggering event:

```python
om.visualize_outer_static("outer.png")                        # whole run, saved to disk
om.visualize_outer_interactive()                              # whole run, interactive
om.visualize_outer_interactive(start=2.0, end=6.0)            # a time window
om.visualize_outer_interactive(show_triggering_events=False)  # hide the markers
```

The interactive variant returns a Plotly figure; pass `path="outer.html"` to
also write it to disk. (`visualize_outer` remains as an alias for the
interactive variant.)

Both methods take the same arguments — `path` positionally, the rest as
keywords:

| Argument | Type | Default | Meaning |
| --- | --- | --- | --- |
| `path` | `str` / `Path` | `None` | Also write the figure to disk: an HTML file for the interactive variant, an image (`.png`, `.svg`, ...) for the static one. Without it the figure is only returned. |
| `start`, `end` | `float` | `None` | Clip the time axis to `[start, end]` (simulation time). Either may be omitted. |
| `show_triggering_events` | `bool` | `True` | Draw a dotted vertical marker at each triggering event inside the window. |
| `metric` | `str` or callable | number in system | *What* to plot — see {ref}`choosing-object-metric` below. |
| `nested_id` | `str` | auto-detected | *Which* object to plot — see {ref}`choosing-object-metric` below. |

## The inner branches

`visualize_inner` plots the branches forked at one triggering event. The time
axis is **relative to the fork** (the checkpoint is at 0), so the branches line
up regardless of when the trigger fired:

```python
om.visualize_inner(trigger_id=0)                      # every branch at trigger 0
om.visualize_inner(trigger_id=0, inner_id=1)          # a single branch
om.visualize_inner(trigger_id=0, relative_start=0.0)  # only the forked future
```

The preceding outer segment is drawn as grey context unless you pass
`show_outer_context=False`.

`visualize_inner` returns a Plotly figure (pass `path="inner.html"` to also
write it to disk). Its arguments:

| Argument | Type | Default | Meaning |
| --- | --- | --- | --- |
| `trigger_id` | `int` | — (required) | Which triggering event to plot (one of `om.trigger_ids`). |
| `inner_id` | `int` | `None` | A single branch to plot; `None` overlays every branch at that trigger. |
| `path` | `str` / `Path` | `None` | Also write the figure to disk as HTML. |
| `relative_start`, `relative_end` | `float` | `None` | Clip the *relative* time axis (fork = 0); `relative_start=0.0` hides the outer lead-in, negative values show that much history before the fork. |
| `show_outer_context` | `bool` | `True` | Draw the outer segment before the fork as grey context. It meets the inner traces exactly at time 0, where the inner state equals the outer state. |
| `metric`, `nested_id` | as above | | Same meaning as for the outer plots — next section. |

(choosing-object-metric)=
## Choosing the object and the metric

By default the manager plots the number in system for the run's (single)
resource. Two arguments, accepted by `visualize_outer_static`,
`visualize_outer_interactive` and `visualize_inner`, control what is plotted:

- **`nested_id`** selects *which* nesting object to plot. In a model with
  several resources, containers or stores, pass the object's `nested_id` and
  the count is generated from that particular object.
- **`metric`** selects *what* to show for that object. For a resource the
  three built-in options are `"in_queue"` (number waiting), `"in_service"`
  (number being served), and `"in_system"` (the total: in queue plus in
  service); for a container, `"level"`.

```python
om.visualize_outer_static("srv_queue.png", nested_id="srv", metric="in_queue")
om.visualize_outer_interactive(nested_id="tank", metric="level")
om.visualize_inner(trigger_id=0, nested_id="srv", metric="in_system")
```

Any recorded state field can also be named in full (e.g.
`metric="state_num_customers_in_queue"`), and user-defined custom metrics are
supported by passing a callable that derives a quantity from each row:

```python
om.visualize_outer_interactive(
    metric=lambda row: float(row["(srv)state_num_customers_in_service"])
)
```

How the naming fits together: the exported tables carry one group of state
columns per nesting object, prefixed with its id —
`(<nested_id>)state_<field>`, e.g. `(srv)state_num_customers_in_queue` (see
{doc}`Exporting data <traces-and-outputs>`). The `metric` aliases expand to
those field names (`"in_queue"` is `state_num_customers_in_queue`, and so on)
and `nested_id` picks the prefix. A callable metric receives each exported row
as a dict whose values are **strings** (the tables are CSVs) — convert with
`float(...)` as in the example — and may return `None` to skip a row. You can
also set a default for the whole session when constructing the manager:
`OutputManager("nested_output/mm1", metric="in_queue")`.
