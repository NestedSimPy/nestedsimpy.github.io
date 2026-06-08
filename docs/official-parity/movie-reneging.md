# Movie Renege

## Scenario

Customers line up at a single ticket counter for different movies. Once a movie
is sold out, customers waiting for that title leave the queue.

## Files

- Plain SimPy: `simpy_examples/movie_reneging_plain.py`
- PyNestedSim: `simpy_examples/movie_reneging_nested.py`

## Parity Goal

The nested version preserves the sold-out and reneging logic of the original
example, while also producing real branch points tied to customer arrivals.

## What PyNestedSim Adds

- explicit branch outputs per arrival boundary,
- manifests and stop reasons for each branch,
- traces that make sold-out state transitions inspectable after the run.

## Code

The point of this parity pair is that the nested adaptation is still very close
to the original SimPy example. The easiest way to inspect that is to read the
actual source files directly.

````{dropdown} Plain SimPy source
```{literalinclude} ../../simpy_examples/movie_reneging_plain.py
:language: python
:caption: simpy_examples/movie_reneging_plain.py
```
````

````{dropdown} PyNestedSim source
```{literalinclude} ../../simpy_examples/movie_reneging_nested.py
:language: python
:caption: simpy_examples/movie_reneging_nested.py
```
````

## Run

```bash
python simpy_examples/movie_reneging_plain.py
python simpy_examples/movie_reneging_nested.py
```
