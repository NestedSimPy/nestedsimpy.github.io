# Replay

Replay deterministically re-runs a single branch that a full run already
surfaced — for example, to inspect one interesting path more closely without
repeating the whole experiment.

To re-run a single branch deterministically — for example, to inspect a path a
full run already surfaced — use `run_single_path(...)`:

```python
env.run_single_path(trigger_index=2, branch_index=0, outer_seed=1234)
```

The arguments are keyword-only:

| Argument | Type | Meaning |
| --- | --- | --- |
| `trigger_index` | `int` | Which trigger event to branch at: `0` is the first trigger on the outer path, `1` the second, and so on (the `j` index in the raw output layout). |
| `branch_index` | `int` | Which branch at that trigger to execute (the `k` index, `0`-based). |
| `outer_seed` | `int`, optional | Seed for the outer path. When omitted, the seed stored by `set_outer_seed` is reused. |

Call it *instead of* `nested_run()`, on an environment built and configured
exactly like the original run (same model code, same `set_*` calls, same
seeds). Because the outer path is driven by the outer seed, the replay
re-executes the identical outer trajectory from time 0, skips every trigger
except `trigger_index`, launches only `branch_index` there, and stops once that
branch completes. If the requested trigger never occurs on the outer path, a
`KeyError` is raised.
