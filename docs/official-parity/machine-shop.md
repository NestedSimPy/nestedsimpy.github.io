# Machine Shop

## Scenario

The machine-shop example combines interrupts with a `PreemptiveResource`. A
repairman handles both routine work and urgent breakdowns, and machine failures
can preempt lower-priority tasks.

## Files

- Plain SimPy: `simpy_examples/machine_shop_plain.py`
- PyNestedSim: `simpy_examples/machine_shop_nested.py`

## Parity Goal

The nested adaptation keeps the workshop production summary on the outer path
aligned with the plain baseline while tracing interruptions and preemptions in a
branch-aware way.

## What PyNestedSim Adds

- `NestedPreemptiveResource` instrumentation,
- trace records for preemption-related transitions,
- packaged branch outputs for downstream inspection.

## Code

The plain and nested sources are included below because this parity pair is
primarily about preserving the original logic while instrumenting a more complex
resource discipline.

````{dropdown} Plain SimPy source
```{literalinclude} ../../simpy_examples/machine_shop_plain.py
:language: python
:caption: simpy_examples/machine_shop_plain.py
```
````

````{dropdown} PyNestedSim source
```{literalinclude} ../../simpy_examples/machine_shop_nested.py
:language: python
:caption: simpy_examples/machine_shop_nested.py
```
````

## Run

```bash
python simpy_examples/machine_shop_plain.py
python simpy_examples/machine_shop_nested.py
```
