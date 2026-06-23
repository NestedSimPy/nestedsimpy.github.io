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

The point of this parity pair is that the nested adaptation is still very close
to the original SimPy example. The easiest way to inspect that is to read the
actual source files directly.

### Plain SimPy

```{literalinclude} ../../simpy_examples/movie_reneging_plain.py
:language: python
:caption: simpy_examples/movie_reneging_plain.py
```

### NestedSimPy

The same model under NestedSimPy. **New lines are highlighted green and modified
lines amber**, relative to the plain baseline above; long unchanged runs are
folded — click to expand them.

```{codeannotate} ../../simpy_examples/movie_reneging_plain.py ../../simpy_examples/movie_reneging_nested.py
:title: simpy_examples/movie_reneging_nested.py
:context: 3
```

## Discussion

The ticket counter `simpy.Resource` becomes `NestedResource`; the shared sold-out `Event`s and the reneging logic are kept as-is. Branching forks on each arrival, and the sold-out summary on the outer run matches plain SimPy.

## Run

```bash
python simpy_examples/movie_reneging_plain.py
python simpy_examples/movie_reneging_nested.py
```
