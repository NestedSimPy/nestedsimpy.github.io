# Reporting API

Helpers for turning raw run output into CSV exports, consolidated per-branch
results, packaged artefacts, and interactive/static plots.

```{note}
Signatures below describe the **public interface**. Implementation details are
intentionally omitted.
```

## Low-Level Postprocess

```python
build_events(out_dir, out_csv='events.csv') -> Path
build_state_long(out_dir, out_csv='state_long.csv') -> Path
build_state_wide(out_dir, out_csv='state_wide.csv') -> Path
export_realizations(out_dir, export_dir_name='exports') -> Path
```

- **`build_events`** — export non-snapshot events for audit purposes.
- **`build_state_long`** — export snapshot queue contents to a long-format CSV.
- **`build_state_wide`** — export snapshot records to a wide-format CSV.
- **`export_realizations`** — export per-realisation CSV/JSON bundles for the
  outer run and its inner branches.

## Result Access

```python
has_consolidated_output(run_dir) -> bool
iter_branch_results(run_dir) -> Iterator[dict]
load_snapshots(run_dir) -> dict[int, dict]
extract_anchor_wait(events, anchor_cust_id, anchor_arrival,
                    checkpoint_in_service, served_only=False) -> float | None
extract_anchor_outcome(events, anchor_cust_id, anchor_arrival,
                       checkpoint_in_service) -> tuple[float | None, str]
```

- **`has_consolidated_output`** — `True` if a consolidated `branch_results`
  file exists for the run.
- **`iter_branch_results`** — yield consolidated per-branch records (empty if
  none).
- **`load_snapshots`** — return a `{j: snapshot_record}` map for the run.
- **`extract_anchor_wait`** — the anchor customer's realised wait in hours, or
  `None`.
- **`extract_anchor_outcome`** — `(realised_wait, outcome)` for the anchor in
  one branch.

## Packaged Reporting

```python
package_run_outputs(out_root, *, export_dir_name='exports',
                    raw_dir_name='raw') -> PackagedRunArtifacts
resolve_run_dir(source, *, outer_id=None) -> Path
resolve_exports_dir(source, *, outer_id=None) -> Path
has_branch_csv(exports_dir) -> bool
```

- **`package_run_outputs`** — package a run and return typed paths to the
  resulting artefacts.
- **`PackagedRunArtifacts`** — typed view of the standard artefacts produced by
  packaging.
- **`DEFAULT_EXAMPLE_OUTPUT_ROOT`** — default output root used by the bundled
  examples.
- **`resolve_run_dir` / `resolve_exports_dir`** — resolve a `source` to a
  packaged run directory / its `exports` directory.
- **`has_branch_csv`** — whether `exports_dir` contains at least one branch CSV.

## Waiting-Time Hook

```python
wait_time_hook(outer_dir, exports_dir, manifest, *,
               arrival_col='state_in_service_arrival_time',
               start_col='state_in_service_start_time',
               cust_col='cust_id', resource_id=None,
               output_csv='user_waits.csv', **opts) -> dict
```
> Compute per-branch waiting-time summaries from the exported CSVs.

## Plots

```python
build_static_figure(groups, *, state_field, resource_id) -> go.Figure
build_dynamic_figure(groups, *, state_field, resource_id) -> tuple[go.Figure, dict, tuple]
write_static_plot(source, *, outer_id=None, output_path=None,
                  state_field='state_num_customers_in_system', resource_id=None) -> Path
write_dynamic_plot(source, *, outer_id=None, output_path=None,
                   state_field='state_num_customers_in_system', resource_id=None) -> Path
```

- **`build_static_figure`** — build the multi-panel static branch comparison plot.
- **`build_dynamic_figure`** — build the interactive branch-toggle plot and its
  metadata payloads.
- **`write_static_plot` / `write_dynamic_plot`** — render and write the static /
  interactive branch plot HTML, returning the output path.
