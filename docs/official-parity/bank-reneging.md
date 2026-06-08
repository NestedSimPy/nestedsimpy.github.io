# Bank Renege

## Scenario

The bank example combines a standard `Resource` queue with condition events and
reneging. Customers wait for service, but they may abandon the queue if their
patience runs out first.

## Files

- Plain SimPy: `simpy_examples/bank_reneging_plain.py`
- PyNestedSim: `simpy_examples/bank_reneging_nested.py`

## Parity Goal

The nested adaptation keeps the original reneging behavior intact while still
producing branch manifests and trace outputs. In the test suite, the outer
stdout lines for customers are compared directly against the plain baseline.

## What PyNestedSim Adds

- branch generation on arrival boundaries,
- structured stop reasons for branch completions,
- trace files for queue transitions and reneging events.

## Code

The nested version is easiest to evaluate by reading the actual source side by
side with the original-style baseline.

````{dropdown} Plain SimPy source
```{literalinclude} ../../simpy_examples/bank_reneging_plain.py
:language: python
:caption: simpy_examples/bank_reneging_plain.py
```
````

````{dropdown} PyNestedSim source
```{literalinclude} ../../simpy_examples/bank_reneging_nested.py
:language: python
:caption: simpy_examples/bank_reneging_nested.py
```
````

## Run

```bash
python simpy_examples/bank_reneging_plain.py
python simpy_examples/bank_reneging_nested.py
```
