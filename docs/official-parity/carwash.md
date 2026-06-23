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

- Plain SimPy: `simpy_examples/carwash_plain.py`
- NestedSimPy: `simpy_examples/carwash_nested.py`

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

The plain SimPy model is unchanged except for the nesting setup: the washing machines are a `NestedResource`, the run is `env.nested_run()`, and branching fires on **every car arrival**, forking **2 inner simulations** that each run for **20 time units, or until the triggering car departs**. The wash process is otherwise identical to plain SimPy.

## Run

```bash
python simpy_examples/carwash_plain.py
python simpy_examples/carwash_nested.py
```
