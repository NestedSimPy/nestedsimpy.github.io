# Machine Shop

## Scenario

Adapted from SimPy's official [Machine Shop example](https://simpy.readthedocs.io/en/latest/examples/machine_shop.html).

The machine-shop example combines interrupts with a `PreemptiveResource`. A
repairman handles both routine work and urgent breakdowns, and machine failures
can preempt lower-priority tasks.

## Files

- Plain SimPy: `simpy_examples/machine_shop_plain.py`
- NestedSimPy: `simpy_examples/machine_shop_nested.py`

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

## Discussion

The repairman `simpy.PreemptiveResource` becomes `NestedPreemptiveResource`, so machine breakdowns still preempt routine maintenance and that preemption is captured inside each branch. The per-machine production summary on the outer run matches plain SimPy.

## Run

```bash
python simpy_examples/machine_shop_plain.py
python simpy_examples/machine_shop_nested.py
```
