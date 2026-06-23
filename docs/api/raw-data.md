# Raw data

Every run records raw **JSONL traces** and **manifests** first, then packages
them into the `exports/` CSVs that {doc}`OutputManager <../topical-guides/visualization>`
reads. This page documents that raw layer — useful when debugging behavior or
building a custom reader.

```text
nested_output/<experiment>/<outer_id>/
  raw/
    outer/
      trace.jsonl      # the outer event stream
      manifest.json
    j=0001/            # one directory per triggering event (j = anchor id)
      k=00/            # one directory per branch
        trace.jsonl    # an inner event stream
        manifest.json
  exports/             # CSVs packaged from raw/
```

## Trace events

Each line of `trace.jsonl` is one JSON event. Common keys:

`t`
: Simulation time of the event.

`type`
: Event type — e.g. `branch_started`, `request_submitted`, `request_granted`,
  `request_released`, `snapshot`, `checkpoint_reached`, `queue_length`.

`run_kind`, `j`, `k`, `anchor_cust_id`
: `run_kind` is `"outer"` or `"inner"`; `j`/`k` identify the triggering event and
  branch (both `null` on the outer path); `anchor_cust_id` is the triggering
  customer.

`state`
: The recorded state at the event — `current_time`, `queue_len`,
  `in_service_customers`, `customers_in_queue` (a list of `[cust_id, arrival_time]`),
  and the in-service customer's ids and times.

Derived quantities such as the number in system are **not** stored on the raw
event; they are computed during export (number in system = queue length +
in-service count), which is why the packaged CSVs carry extra `state_*` columns.

## Manifests

`manifest.json` summarizes a run. The outer manifest records `outer_id`, `seed`,
`end_time`, `stop_reason`, and `event_count`. A branch manifest adds
`checkpoint_time`, `boundary_event`, `anchor_arrival_time`, `anchor_cust_id`, and
the branch's own seed.

## Per-branch metrics

Packaging also writes a metrics JSON per branch, with the anchor customer's
outcome in that branch — `anchor_cust_id`, `k`, `anchor_arrival_time`,
`service_start_time`, `service_end_time`, `waiting_time`, and
`service_completion_time` — plus an `[all]` file per triggering event holding the
means and standard deviations across its branches (the source of
`OutputManager.export_outer(inner_aggregate="mean")`).

## Reading it back

You rarely need to parse `raw/` by hand: `package_run_outputs(...)` builds the
`exports/` CSVs, and {doc}`OutputManager <../topical-guides/traces-and-outputs>`
reads those. Reach for the raw traces mainly when debugging a single branch's
behavior.
