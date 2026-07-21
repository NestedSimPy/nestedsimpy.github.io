# Replay

Replay is NestedSimPy's debug mode: after a full run has surfaced an
interesting inner simulation, re-run just that one — deterministically — and
analyze its behaviour without repeating the whole experiment:

```python
env.run_single_path(trigger_id=2, inner_id=0)
```

`trigger_id` and `inner_id` are the same ids the exported tables use: the
trigger event, and which of its inner simulations. `outer_seed=` (optional)
overrides the stored seed.

Call it *instead of* `nested_run()`, on an environment built and configured
exactly like the original run (same model code, same `set_*` calls, same
seeds). The replay re-executes the identical outer trajectory from time 0,
forks only the requested inner simulation, and stops once it completes. If
the requested trigger never occurs on the outer path, a `KeyError` is
raised.
