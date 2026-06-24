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

- Plain SimPy: [`simpy_examples/movie_reneging_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/movie_reneging_plain.py)
- NestedSimPy: [`simpy_examples/movie_reneging_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/movie_reneging_nested.py)

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

Going from an existing SimPy code to NestedSimPy only requires importing the NestedSimPy package, replacing SimPy objects with NestedSimPy objects, modifying timeout commands, and configuring the nested simulation parameters.

