# Movie Renege

## Scenario

Customers line up at a single ticket counter for different movies. Once a movie
is sold out, customers waiting for that title leave the queue.

## Files

- Plain SimPy: `simpy_examples/movie_reneging_plain.py`
- NestedSimPy: `simpy_examples/movie_reneging_nested.py`

## Parity Goal

The nested version preserves the sold-out and reneging logic of the original
example, while also producing real branch points tied to customer arrivals.

## What NestedSimPy Adds

- explicit branch outputs per arrival boundary,
- manifests and stop reasons for each branch,
- traces that make sold-out state transitions inspectable after the run.

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

## Run

```bash
python simpy_examples/movie_reneging_plain.py
python simpy_examples/movie_reneging_nested.py
```
