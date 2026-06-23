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

## On disk: raw and exports

Where the run is written is set on the environment:

```python
env.set_output_options(out_dir="nested_output/mm1", gzip_trace=False)
```

A packaged run has this shape:

```text
nested_output/mm1/<outer_id>/
  raw/            # one trace.jsonl + manifest.json per outer run and per branch
    outer/
    j=0001/k=00/
  exports/        # CSVs packaged from the raw traces (what OutputManager reads)
```

Inspect `raw/` when debugging behavior and `exports/` when comparing results
across runs or branches. The raw event format is described under
{doc}`Implementation <../architecture>`.

## Next

- {doc}`visualization` — plot the same trajectories instead of exporting them.
