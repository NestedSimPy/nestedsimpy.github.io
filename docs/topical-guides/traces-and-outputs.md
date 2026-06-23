# Exporting data

A finished run is turned into datasets with an `OutputManager`, which reads the
run's output folder and returns plain rows (and writes CSVs on request):

```python
from nestedsimpy import OutputManager

om = OutputManager("nested_output/mm1")
```

## The outer sample path

`export_outer` returns the outer trajectory — one row per recorded outer event.
Pass a path to also write it as CSV:

```python
rows = om.export_outer()              # list of dicts
om.export_outer("outer.csv")          # ... and write a CSV
```

## A single inner branch

`export_inner` returns one inner simulation, including the outer lead-in up to
the fork (the `segment` column is `outer_before`, then `inner`):

```python
om.export_inner(trigger_id=0, inner_id=0)                  # rows
om.export_inner(trigger_id=0, inner_id=0, path="inner.csv")
```

## Aggregated features and labels

For prediction tasks, `inner_aggregate="mean"` augments each **triggering** row
of the outer path with that trigger's averaged inner outcomes (the mean waiting
time and service-completion time over its branches). The result is the
feature/label table used to benchmark waiting-time predictions:

```python
om.export_outer("features.csv", inner_aggregate="mean")
```

## On disk

A run is written under the directory you set:

```python
env.set_output_options(out_dir="nested_output/mm1", gzip_trace=False)
```

```text
nested_output/mm1/<outer_id>/
  raw/        # raw JSONL traces + manifests — see Implementation › Raw data
  exports/    # the packaged datasets (below)
```

Packaging writes `exports/` in **three forms**, for three different needs:

1. **Per-realization files** — one CSV *per inner simulation*,
   `[seed][trigger,boundary][inner].csv` (the outer lead-in, then that inner's
   own path), alongside the outer path `[seed]-outer.csv` and the per-trigger
   metric JSONs. These are what `export_outer` / `export_inner` above read.
2. **Consolidated tables** — the outer and *all* inners flattened into single
   files: `state_wide.csv` (one row per recorded state), `state_long.csv` (the
   queue contents at each of those states), and `events.csv` (every non-snapshot
   event). Use these to analyse the whole run at once.
3. **Your own metric** — whatever a postprocessor writes (see below); the
   bundled wait-time hook produces `user_waits.csv`, one waiting time per inner.

Inspect `raw/` when debugging a single branch; the raw event format is described
under {doc}`Raw data <../api/raw-data>`.

## Custom postprocessing

Beyond the built-in exports, a run can produce its own outputs: set general
behavior with `set_post_processing_options(...)`, or register a custom
metric/output hook with `set_postprocessor(...)`, which runs after
`nested_run()` over the packaged artefacts.

## Next

- {doc}`visualization` — plot the same trajectories instead of exporting them.
