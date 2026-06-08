# Traces and Outputs

NestedSimPy records raw execution traces first, then packages those traces into
more convenient exports.

## Output Roots

At the environment level, the main output knob is:

```python
env.set_output_options(out_dir="out/mm1_simpy", gzip_trace=False)
```

That controls where branch runs are written and whether traces are compressed.

## Raw Layout

A typical packaged run has this shape:

```text
out/<experiment>/<outer_id>/
  raw/
    outer/
      trace.jsonl
      manifest.json
    j=0001/
      k=00/
        trace.jsonl
        manifest.json
  exports/
    state_wide.csv
    state_long.csv
    events.csv
```

The exact files can vary by example and reporting hook, but this is the main
structure.

## What The Files Mean

`trace.jsonl`
: Raw event stream written during execution.

`manifest.json`
: Summary metadata for the outer simulation or a specific branch.

`state_wide.csv`, `state_long.csv`, `events.csv`
: Packaged exports generated from the raw traces for easier analysis.

## Reporting Helpers

The reporting layer provides higher-level utilities such as:

- `package_run_outputs(...)`
- `write_static_plot(...)`
- `write_dynamic_plot(...)`

These are the functions used by the example wrappers to turn raw runs into CSV
and HTML artifacts.

## Recommended Workflow

1. run the example,
2. package the outputs,
3. inspect `raw/` when debugging behavior,
4. inspect `exports/` when comparing results across runs or branches.
