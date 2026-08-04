# Bank Renege

## Scenario

Adapted from SimPy's official [Bank Renege example](https://simpy.readthedocs.io/en/latest/examples/bank_renege.html).

The bank example combines a standard `Resource` queue with condition events and
reneging. Customers wait for service, but they may abandon the queue if their
patience runs out first.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_bank_reneging.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: [`simpy_examples/bank_reneging_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/bank_reneging_plain.py)
- NestedSimPy: [`simpy_examples/bank_reneging_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/bank_reneging_nested.py)

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/bank_reneging_plain.py
:language: python
:caption: simpy_examples/bank_reneging_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/bank_reneging_plain.py ../../simpy_examples/bank_reneging_nested.py
:title: simpy_examples/bank_reneging_nested.py
:context: 3
```

## Discussion

The `simpy.Environment` becomes a `NestedEnvironment`, and the counter becomes a `NestedResource` with `nested_id="counter"` — the id that `set_triggering_objects` refers to. Branching fires on every arrival. All three delays — the exponential interarrival time, the uniform patience, and the exponential service time — become `env.nested_timeout` calls that carry their distribution parameters, so inner simulations resample the remaining delay instead of reusing a fixed draw. The patience event returned by `nested_timeout` is yielded directly in the reneging condition `req | patience`. The general conversion steps are in {doc}`From SimPy to NestedSimPy <../topical-guides/branching-model>`.

