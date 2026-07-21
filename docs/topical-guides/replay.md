# Replay

Replay is NestedSimPy's debug mode: after a full run has surfaced an
interesting inner simulation, re-run just that one — deterministically — and
analyze its behaviour without repeating the whole experiment.

```text
full nested run                        replay
---------------                        ------
outer ──●────●────●──▶                 outer ──────●────────▶
        │    │    │                                │
      k=0  k=0  k=0                              only
      k=1  k=1  k=1                        (trigger_id=1,
      k=2  k=2  k=2                          inner_id=0)
```

## When you need it

A row of the prediction table looks wrong, or one curve in the interactive
plot fans out strangely — you want to step through exactly that inner
simulation, event by event.

## How

1. Find the two ids in any exported table (or by clicking the trigger point
   in the interactive plot): the trigger event's `trigger_id` and the inner
   simulation's `inner_id`.
2. Rebuild the environment exactly like the original run — same model code,
   same `set_*` calls, same seeds.
3. Call `run_single_path` *instead of* `nested_run()`:

```python
env.run_single_path(trigger_id=1, inner_id=0)
```

`trigger_id` and `inner_id` are the same ids the exported tables use.
`outer_seed=` (optional) overrides the stored seed.

## What you get

Because the outer path is driven by the outer seed, the replay re-executes
the identical outer trajectory from time 0, skips every other trigger, forks
only the requested inner simulation, and stops once it completes. The run
directory then contains just that one branch — the usual
`raw/j=0001/k=00/` trace and manifest — so you can read it with
`export_inner_event_log(1, 0)`, plot it, or inspect the raw events directly.
If the requested trigger never occurs on the outer path, a `KeyError` is
raised.
