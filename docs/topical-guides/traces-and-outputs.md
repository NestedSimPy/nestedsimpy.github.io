# Exporting data

A finished run is turned into datasets with an `OutputManager`, which reads the
run's output folder and returns plain rows (and writes CSVs on request):

```python
from nestedsimpy import OutputManager

om = OutputManager("nested_output/mm1")
```

The argument is the run's output directory (or a parent of several runs — the
most recent is chosen; see {doc}`Visualization <visualization>` for the
loading rules). Each export method returns a list of plain dicts — one dict
per row, ready for `pandas.DataFrame(rows)` — and writes the same table as a
CSV when a `path` is given. Values read back from the run's CSVs are strings;
convert (e.g. `float(row["t"])`) before computing with them.

## The outer sample path

`export_outer_event_log` returns the outer trajectory — one row per recorded
outer event. Pass a path to also write it as CSV:

```python
rows = om.export_outer_event_log()              # list of dicts
om.export_outer_event_log("outer.csv")          # ... and write a CSV
```

The most useful columns of each row:

| Column | Meaning |
| --- | --- |
| `t` | Simulation time of the event. |
| `queue_event` | What happened — `arrival`, `service_start`, `service_departure`, ... |
| `cust_id` | The customer the event belongs to. |
| `nesting_object_id` | Which object emitted the event (its `nested_id`). |
| `(<id>)state_*` | The state of each nesting object after the event — one column group per object, prefixed with its `nested_id`. A resource contributes, among others, `(<id>)state_num_customers_in_queue`, `..._in_service` and `..._in_system` (the total: in queue plus in service). |

## A single inner branch

`export_inner_event_log` returns one inner simulation, including the outer
lead-in up to the trigger point (the `simulation_source` column is `outer`,
then `inner`):

```python
om.export_inner_event_log(trigger_id=0, inner_id=0)                  # rows
om.export_inner_event_log(trigger_id=0, inner_id=0, path="inner.csv")
```

`trigger_id` is the id of the trigger event — one of `om.trigger_ids`, the
sequential indices along the outer path (`0` for the first trigger event, `1`
for the second, ...) — and `inner_id` selects the branch (`0` to `K-1`; each
trigger's valid ids are listed by `om.triggers()`). The rows have
the same columns as `export_outer_event_log`, plus `simulation_source` as the first
column: `outer` marks the shared history recorded before the trigger point, `inner` the
branch itself.

## Aggregated features and labels

For prediction tasks, `export_outer_case_table` augments each **triggering**
row of the outer path with that trigger's averaged inner outcomes (the mean
waiting time and service-completion time over its branches). The result is the
feature/label table used to benchmark waiting-time predictions:

```python
om.export_outer_case_table("features.csv")
```

Six columns are appended to every row: `inner_num_branches`,
`inner_anchor_arrival_time_mean`, `inner_waiting_time_mean`,
`inner_waiting_time_std`, `inner_service_completion_time_mean` and
`inner_service_completion_time_std`. They are filled on exactly one row per
trigger event (the triggering customer's row at the trigger time; for a
trigger without one, the last row recorded before the trigger moment) and
left empty everywhere else — so filtering the table to non-empty `inner_waiting_time_mean`
yields one feature/label pair per trigger. (The mean is currently the only
supported aggregate; the older spelling `export_outer(inner_aggregate="mean")`
still works as an alias.)

## The trigger events

`export_triggers` keeps only the trigger events themselves — one row per
trigger. Each row carries `trigger_id` (the sequential trigger index) and
`anchor_cust_id` (the triggering customer, blank for triggers without one —
e.g. a state predicate firing on an empty system), the trigger time `t`, the `boundary_event` that fired, the object's
`state_*` columns at the trigger moment, `num_branches` (how many inner
simulations were launched there) and the averaged inner outcomes
(`inner_waiting_time_mean`, `inner_service_completion_time_mean`, ...):

```python
om.export_triggers()                   # list of dicts, one per trigger event
om.export_triggers("triggers.csv")     # ... and write a CSV
```

The full column list, in order: `trigger_id`, `t`, `boundary_event`,
`anchor_cust_id`, the `(<id>)state_*` columns copied from the outer row at (or, for
anchor-less triggers, immediately before) the trigger moment — blank when
nothing had been recorded yet, e.g. a trigger at time 0 — `num_branches`, then `inner_anchor_arrival_time_mean`,
`inner_waiting_time_mean`, `inner_waiting_time_std`,
`inner_service_completion_time_mean` and `inner_service_completion_time_std`.

It is the compact companion to `export_outer_case_table`: the same tagged
information, without the non-triggering rows of the outer path.

## On disk

A run is written under the directory you set (`set_output_options(out_dir=...)`)
as a raw layer and a packaged layer; the {doc}`directory layout <../api/index>`
shows both. Packaging writes the packaged `exports/` in **three forms**, for
three different needs:

1. **Per-realization files** — one CSV *per inner simulation*,
   `[seed][j=trigger][customer,boundary][k=inner][inner seed].csv` (the outer
   lead-in, then that inner's own path), alongside the outer path
   `[seed]-outer.csv` and the per-trigger metric JSONs. These are what `export_outer_event_log` /
   `export_inner_event_log` above read.
2. **Consolidated tables** — the outer and *all* inners flattened into single
   files: `state_wide.csv` (one row per recorded state), `state_long.csv` (the
   queue contents at each of those states), and `events.csv` (every non-snapshot
   event). Use these to analyse the whole run at once.
3. **Your own metric** — whatever a postprocessor writes (see below); the
   bundled wait-time hook produces `user_waits.csv`, one waiting time per inner.

Reading a per-realization name such as `[42][j=1][2,arrival][k=0][7].csv`:
the outer seed was `42`, this is trigger event `1` (the second trigger on the
outer path), its triggering customer is `2` (`-` for triggers without one),
the boundary that fired was an `arrival`, the branch is inner `0`, and the
last bracket is that branch's seed. Prefer `om.trigger_ids` / `om.triggers()`
over parsing file names.

Inspect `raw/` when debugging a single branch; the raw event format is described
under {doc}`Raw data <../api/raw-data>`.

(user-defined-metrics)=
## User-defined metrics

`env.register_metric(name, fn)` — called before `nested_run()` — registers a
per-branch metric computed from the event log. For every inner branch, `fn` is
evaluated once during post-processing, in the same phase that computes the
built-in `waiting_time` / `service_completion_time`, and its value is
aggregated exactly like the built-ins. The {doc}`Simple example
<../simple-example>` shows a worked metric (`user_wait`) that reproduces the
built-in waiting time from the event-log rows.

**The metric function.** `fn(rows, ctx)` must return a number (anything
`float()` accepts) or `float("nan")`.

`rows` is the branch's full event log as a list of dicts — the outer lead-in
up to the trigger point followed by the inner branch — with the same columns
as `export_inner_event_log`. Unlike CSVs read back from disk, the values are
native Python objects (numbers, `None`), not strings.

What `rows` contains:

| Column | Meaning |
| --- | --- |
| `simulation_source` | `outer` for the lead-in rows recorded before the trigger point, `inner` for the branch itself. |
| `t` | Simulation time of the event. |
| `type` | Raw event name as recorded by the engine (e.g. `request_granted`). |
| `queue_event` | The friendly event label — `arrival`, `service_start`, `service_departure`, ... |
| `cust_id` | The customer the event belongs to. |
| `nesting_object_id` | Which object emitted the event (its `nested_id`). |
| `(<id>)state_*` | The state of each nesting object after the event — one column group per object, prefixed with its `nested_id`. |
| `run_kind`, `outer_id`, `j`, `k`, `anchor_cust_id`, ... | Bookkeeping columns identifying the run and branch each row belongs to (the same columns as in the exported CSVs). |

`ctx` describes the branch. What `ctx` contains:

| Key | Meaning |
| --- | --- |
| `trigger_id` | Id of the trigger event — the sequential index along the outer path (0, 1, 2, ...). |
| `trigger_time` | Simulation time at which the trigger event fired. |
| `triggering_customer_id` | The triggering customer's id (`None` for triggers without one). |
| `anchor_arrival_time` | Arrival time of the triggering customer (the trigger time itself when there is none). |
| `boundary_event` | The event type that fired the trigger (e.g. `arrival`). With several conditions configured, this identifies which one fired. |
| `j` | Alias of `trigger_id` (the order in which triggers fired). |
| `replication_k` | The branch's replication number `k` — the same value as `inner_id`. |
| `inner_seed` | Random seed used by this inner branch. |
| `outer_seed` | Random seed of the outer simulation. |
| `outer_id` | Identifier of the outer run. |

**Missing values.** Returning `float("nan")` (or `None`) marks the branch's
value as missing — it is stored as JSON `null` and skipped by the mean/std
aggregation, exactly like a missing built-in `waiting_time`. If `fn` raises,
or returns something `float()` cannot convert, or returns a non-finite
`float("inf")` / `float("-inf")`, a warning is emitted (once per metric name
per packaging pass) and the value is likewise recorded as missing; the run
still completes.

**Where the results appear.** Each registered metric shows up in all three
metric outputs: the per-branch `...-metrics.json` gains a `<name>` entry, the
per-trigger `[all]-metrics.json` gains `<name>_mean` / `<name>_std`, and
`export_outer_case_table` / `export_triggers` automatically gain
`inner_<name>_mean` / `inner_<name>_std` columns next to the built-in six.

**Writing your own metric: a recipe.**

1. Decide the quantity, and make sure it is *observable*: it must be
   computable from the event-log columns above. Queue counts and waits
   already are; a model-specific quantity (a cost, a score) becomes
   observable by tracking it in a `NestedContainer` -- its
   `(<id>)state_level` column then appears in every row.
2. Scan `rows` for the events or state values you need, using `ctx` for the
   branch's identity (which customer triggered it, when, which replication).
3. Return one number -- or `float("nan")` whenever the quantity is undefined
   for this branch.
4. Register it before the run: `env.register_metric("my_metric", fn)`.

A second example -- the branch's time-average number in system, computed by
integrating the piecewise-constant state over the inner segment:

```python
def avg_in_system(rows, ctx):
    area, last_t, last_n = 0.0, None, None
    for row in rows:
        if row["simulation_source"] != "inner":
            continue                                # inner segment only
        n = row.get("(srv)state_num_customers_in_system")
        if n is None:
            continue                                # row of another object
        if last_t is not None:
            area += (row["t"] - last_t) * last_n    # exact for DES state
        last_t, last_n = row["t"], n
    if last_t is None:
        return float("nan")                         # no inner activity
    return area / (last_t - ctx["trigger_time"]) if last_t > ctx["trigger_time"] else float("nan")

env.register_metric("avg_in_system", avg_in_system)
```

`name` must be a non-empty string that collides neither with a built-in metric
key (`waiting_time`, `service_completion_time`, ...) nor with an
already-registered metric. Registering a metric implies packaging (like
`set_postprocessor` below, `package_latest` is not needed); metrics only take
effect for runs packaged through `nested_run()`'s own pipeline, not when an
output folder is packaged standalone.

## Custom postprocessing

Beyond the built-in exports, a run can produce its own outputs: set general
behavior with `set_post_processing_options(...)`, or register a custom
metric/output hook with `set_postprocessor(...)`, which runs after
`nested_run()` over the packaged artefacts.

`set_post_processing_options` takes free keyword options; the ones
`nested_run()` reads are:

| Option | Type | Default | Meaning |
| --- | --- | --- | --- |
| `package_latest` | `bool` | `False` | Package the run (build `exports/` from `raw/`) immediately at the end of `nested_run()`. Without it, packaging happens lazily the first time an `OutputManager` opens the run — either way the exports come out the same. |
| `raw_dir_name`, `export_dir_name` | `str` | `"raw"`, `"exports"` | Rename the two layers of the run directory. |
| `print_outputs` | `bool` | same as `package_latest` | Print the run, raw and exports directories when packaging completes. |
| `verify_outputs` | `bool` | same as `package_latest` | Sanity-check that the packaged directories exist where expected. |

A postprocessor is a callable with the fixed signature
`fn(outer_dir, exports_dir, manifest, **options)` — the run directory, its
packaged `exports/` directory, and the outer manifest dict. It runs once,
inside `nested_run()`, right after packaging (registering one implies
packaging, so `package_latest` is not needed). If it returns a dict, the dict
is written as JSON to `exports/<output_name>` (`output_name` defaults to
`"user_metrics.json"`); any extra keyword arguments passed to
`set_postprocessor` are forwarded to the callable. The bundled
`wait_time_hook` is a ready-made example — it scans the per-realization CSVs
and writes `user_waits.csv`:

```python
from nestedsimpy import wait_time_hook

env.set_postprocessor(wait_time_hook, output_name="wait_summary.json")
env.nested_run()   # ... afterwards: exports/wait_summary.json + exports/user_waits.csv
```

A minimal hand-written hook follows the same pattern:

```python
def count_branches(outer_dir, exports_dir, manifest, **options):
    n = len(list(exports_dir.glob("*[[]*,*[]]*.csv")))   # per-realization CSVs
    return {"num_branch_csvs": n}                        # -> exports/user_metrics.json

env.set_postprocessor(count_branches)
```
