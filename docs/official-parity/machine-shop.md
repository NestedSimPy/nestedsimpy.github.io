# Machine Shop

## Scenario

The machine-shop example combines interrupts with a `PreemptiveResource`. A
repairman handles both routine work and urgent breakdowns, and machine failures
can preempt lower-priority tasks.

## Files

- Plain SimPy: `simpy_examples/machine_shop_plain.py`
- NestedSimPy: `simpy_examples/machine_shop_nested.py`

## Parity Goal

The nested adaptation keeps the workshop production summary on the outer simulation
aligned with the plain baseline while tracing interruptions and preemptions in a
branch-aware way.

## What NestedSimPy Adds

- `NestedPreemptiveResource` instrumentation,
- trace records for preemption-related transitions,
- packaged branch outputs for downstream inspection.

## Code

The plain and nested sources are included below because this parity pair is
primarily about preserving the original logic while instrumenting a more complex
resource discipline.

### Plain SimPy

```{literalinclude} ../../simpy_examples/machine_shop_plain.py
:language: python
:caption: simpy_examples/machine_shop_plain.py
```

### NestedSimPy

The same model under NestedSimPy. **New lines are highlighted green and modified
lines amber**, relative to the plain baseline above; long unchanged runs are
folded — click to expand them.

```{codeannotate} ../../simpy_examples/machine_shop_plain.py ../../simpy_examples/machine_shop_nested.py
:title: simpy_examples/machine_shop_nested.py
:context: 3
```

## Run

```bash
python simpy_examples/machine_shop_plain.py
python simpy_examples/machine_shop_nested.py
```
