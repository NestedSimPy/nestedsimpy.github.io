# Replay

Replay is NestedSimPy's debug mode: after a full run has surfaced an
interesting branch, deterministically re-run just that branch to analyze its
behaviour — without repeating the whole experiment. Use
`run_single_path(...)`:

```python
env.run_single_path(trigger_index=2, branch_index=0, outer_seed=1234)
```

The arguments are keyword-only:

| Argument | Type | Meaning |
| --- | --- | --- |
| `trigger_index` | `int` | Which trigger event to branch at: `0` is the first trigger on the outer path, `1` the second, and so on — the same sequential numbering as `trigger_id` in the exported tables (the `j` index in the raw output layout). |
| `branch_index` | `int` | Which of that trigger's inner simulations to execute: the replication number `k` (`0` to `K-1`) — the same numbering as `inner_id` in the exported tables. |
| `outer_seed` | `int`, optional | Seed for the outer path. When omitted, the seed stored by `set_outer_seed` is reused. |

Call it *instead of* `nested_run()`, on an environment built and configured
exactly like the original run (same model code, same `set_*` calls, same
seeds). Because the outer path is driven by the outer seed, the replay
re-executes the identical outer trajectory from time 0, skips every trigger
except `trigger_index`, launches only `branch_index` there, and stops once that
branch completes. If the requested trigger never occurs on the outer path, a
`KeyError` is raised.
