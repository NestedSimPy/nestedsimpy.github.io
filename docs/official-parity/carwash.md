# Carwash

## Scenario

Adapted from SimPy's official [Carwash example](https://simpy.readthedocs.io/en/latest/examples/carwash.html).

Cars arrive at a carwash with a limited number of washing machines. If a machine
is busy, they wait in queue; once a machine is free, they start washing and
leave when finished.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_carwash.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: [`simpy_examples/carwash_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/carwash_plain.py)
- NestedSimPy: [`simpy_examples/carwash_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/carwash_nested.py)

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/carwash_plain.py
:language: python
:caption: simpy_examples/carwash_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/carwash_plain.py ../../simpy_examples/carwash_nested.py
:title: simpy_examples/carwash_nested.py
:context: 3
```

## Discussion

Going from an existing SimPy code to NestedSimPy only requires importing the NestedSimPy package, replacing SimPy objects with NestedSimPy objects, modifying timeout commands, and configuring the nested simulation parameters.

