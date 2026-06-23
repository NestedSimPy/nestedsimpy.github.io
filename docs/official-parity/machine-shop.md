# Machine Shop

## Scenario

Adapted from SimPy's official [Machine Shop example](https://simpy.readthedocs.io/en/latest/examples/machine_shop.html).

The machine-shop example combines interrupts with a `PreemptiveResource`. A
repairman handles both routine work and urgent breakdowns, and machine failures
can preempt lower-priority tasks.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_machine_shop.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: `simpy_examples/machine_shop_plain.py`
- NestedSimPy: `simpy_examples/machine_shop_nested.py`

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/machine_shop_plain.py
:language: python
:caption: simpy_examples/machine_shop_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/machine_shop_plain.py ../../simpy_examples/machine_shop_nested.py
:title: simpy_examples/machine_shop_nested.py
:context: 3
```

## Discussion

`simpy.PreemptiveResource` becomes `NestedPreemptiveResource` (`nested_id="repairman"`) and `env.run()` becomes `env.nested_run()`. Branching is triggered on **every 10th arrival** to the repairman, forking **2 inner simulations** that each run for **120 time units, or until the triggering job departs**. The preempt-on-breakdown discipline is preserved, so the outer production summary matches plain SimPy.

## Run

```bash
python simpy_examples/machine_shop_plain.py
python simpy_examples/machine_shop_nested.py
```
