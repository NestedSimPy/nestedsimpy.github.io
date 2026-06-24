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

- Plain SimPy: [`simpy_examples/machine_shop_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/machine_shop_plain.py)
- NestedSimPy: [`simpy_examples/machine_shop_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/machine_shop_nested.py)

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

Going from an existing SimPy code to NestedSimPy only requires importing the NestedSimPy package, replacing SimPy objects with NestedSimPy objects, modifying timeout commands, and configuring the nested simulation parameters.

