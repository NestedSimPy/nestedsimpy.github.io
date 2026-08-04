# Machine Shop

## Scenario

Adapted from SimPy's official [Machine Shop example](https://simpy.readthedocs.io/en/latest/examples/machine_shop.html).

The machine-shop example combines interrupts with a `PreemptiveResource`. A
repairman handles both routine work and urgent breakdowns, and machine failures
can preempt lower-priority tasks.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_machine_shop.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: [`simpy_examples/machine_shop_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/machine_shop_plain.py)
- NestedSimPy: [`simpy_examples/machine_shop_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/machine_shop_nested.py)

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/machine_shop_plain.py
:language: python
:caption: simpy_examples/machine_shop_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/machine_shop_plain.py ../../simpy_examples/machine_shop_nested.py
:title: simpy_examples/machine_shop_nested.py
:context: 3
```

## Discussion

The repairman — a `simpy.PreemptiveResource` — becomes a `NestedPreemptiveResource` with `nested_id="repairman"`. Both the machines and the other-jobs process pass a `job_id` on their priority requests (the machine index, or ids counted from 10000), so competing jobs stay distinguishable in the trace. The exponential time to failure becomes an `env.nested_timeout` carrying its rate, so breakdowns are resampled inside branches. The part-processing delay keeps its explicit `done_in` bookkeeping, which is needed to resume after preemption, and is wrapped as a deterministic value like the repair and other-job delays. The general conversion steps are in {doc}`From SimPy to NestedSimPy <../topical-guides/branching-model>`.

