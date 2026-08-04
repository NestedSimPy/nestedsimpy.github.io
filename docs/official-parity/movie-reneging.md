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

The ticket counter becomes a `NestedResource` with `nested_id="counter"` (constructed with `snapshot=False`), and the `Theater` `NamedTuple` annotation changes accordingly. The exponential moviegoer interarrival time becomes an `env.nested_timeout` carrying its rate, so it is resampled inside branches, while the fixed argue-and-leave and ticket-purchase delays are wrapped as deterministic values. Each moviegoer gets a `cust_id` from an `itertools.count` and passes it as `job_id` on the counter request. The general conversion steps are in {doc}`From SimPy to NestedSimPy <../topical-guides/branching-model>`.

