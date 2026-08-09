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
```

## Discussion

The washing machines become a `NestedResource` with `nested_id="wash"`; because it is created inside the `Carwash` class, it is wrapped in `env.register` so the environment can find it by id during branching. Both delays become deterministic `env.nested_timeout` calls — the wash time is the constant `WASHTIME`, and the interarrival time is still drawn with `random.randint` and then passed as a fixed value. The `Carwash` is now constructed in `main` rather than inside `setup`, so the resource exists when the triggering configuration names it. The general conversion steps are in {doc}`From SimPy to NestedSimPy <../topical-guides/branching-model>`.

