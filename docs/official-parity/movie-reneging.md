# Movie Renege

## Scenario

Adapted from SimPy's official [Movie Renege example](https://simpy.readthedocs.io/en/latest/examples/movie_renege.html).

Customers line up at a single ticket counter for different movies. Once a movie
is sold out, customers waiting for that title leave the queue.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_movie_reneging.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: `simpy_examples/movie_reneging_plain.py`
- NestedSimPy: `simpy_examples/movie_reneging_nested.py`

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/movie_reneging_plain.py
:language: python
:caption: simpy_examples/movie_reneging_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/movie_reneging_plain.py ../../simpy_examples/movie_reneging_nested.py
:title: simpy_examples/movie_reneging_nested.py
:context: 3
```

## Discussion

`simpy.Resource` becomes `NestedResource` (`nested_id="counter"`, the ticket counter) and `env.run()` becomes `env.nested_run()`. Branching is triggered on **every moviegoer arrival**, forking **1 inner simulation** that runs for **10 time units, or until the triggering customer departs**. The shared sold-out event and reneging logic are unchanged.

## Run

```bash
python simpy_examples/movie_reneging_plain.py
python simpy_examples/movie_reneging_nested.py
```
