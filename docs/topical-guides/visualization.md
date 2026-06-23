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

## The outer trajectory

`visualize_outer` plots a chosen metric along the outer path, with a marker at
each triggering event:

```python
om.visualize_outer()                              # whole run
om.visualize_outer(start=2.0, end=6.0)            # a time window
om.visualize_outer(show_triggering_events=False)  # hide the markers
```

It returns a Plotly figure; pass `path="outer.html"` to also write it to disk.

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

## Choosing a metric

By default the manager plots the number in system, inferred from the recorded
state. Any recorded state field can be named instead, or you can pass a callable
that derives a quantity from each row:

```python
om.visualize_outer(metric="state_num_customers_in_queue")

om.visualize_outer(metric=lambda row: float(row["(srv)state_num_customers_in_service"]))
```

The same `metric` argument is accepted by `visualize_inner`.
