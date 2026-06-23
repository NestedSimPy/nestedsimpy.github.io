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

- Plain SimPy: `simpy_examples/bank_reneging_plain.py`
- NestedSimPy: `simpy_examples/bank_reneging_nested.py`

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

`simpy.Resource` becomes `NestedResource` (`nested_id="counter"`) and `env.run()` becomes `env.nested_run()`. Branching is triggered on **every customer arrival** at the counter, forking **2 inner simulations** that each run **until the triggering customer departs**. The reneging logic (the `request | patience-timeout` condition event) is unchanged, so the outer customer sequence is identical to plain SimPy.

## Run

```bash
python simpy_examples/bank_reneging_plain.py
python simpy_examples/bank_reneging_nested.py
```
