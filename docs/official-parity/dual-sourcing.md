---
orphan: true
---

# Dual Sourcing with Lookahead Expediting

## Scenario

An example for using NestedSimPy for optimization (not from the SimPy
documentation). We simulate the dual-sourcing inventory model of Song,
Xiao, Zhang and Zipkin (2017), "Optimal Policies for a Dual-Sourcing
Inventory Problem with Endogenous Stochastic Leadtimes", *Operations
Research* 65(2):379–395: a single product faces unit Poisson demand
with full backlogging; normal orders ride a two-stage tandem production
line, so lead times are endogenous (ordering more congests the line),
and an expedited order — the paper's emergency source — skips stage 1
at a higher per-unit cost. At each
decision epoch the decision-maker decides whether to place a normal or
an expedited order. The example illustrates how NestedSimPy applies
rollout (policy lookahead) of an existing baseline policy: both files
run the paper's Table 5 instance (h=1, b=60, h2=2) under its best
Dual-Index policy (s1=30, s2=12), whose exact cost rate the paper
reports as 99.89. The plain version follows that policy as written; the
nested version hands each decision to `env.decide`, trying each
candidate order in inner simulations launched from the live production
line.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_dual_sourcing.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: [`simpy_examples/dual_sourcing_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/dual_sourcing_plain.py)
- NestedSimPy: [`simpy_examples/dual_sourcing_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/dual_sourcing_nested.py)

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/dual_sourcing_plain.py
:language: python
:caption: simpy_examples/dual_sourcing_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/dual_sourcing_plain.py ../../simpy_examples/dual_sourcing_nested.py
:title: simpy_examples/dual_sourcing_nested.py
:context: 3
```

## Discussion

The baseline policy is the paper's `DualIndexPolicy`, the same object in both
files, and it goes into the decision line as is:

```python
ACTIONS = [None, (0, 1), (1, 1)]

normal, emergency = yield from env.decide(policy, state)
```

Each action is a complete `(normal, emergency)` order, in the shape
the policy returns, and a branch executes its candidate exactly as
written: `None` is the baseline policy's own decision — here `(0, 0)` or
`(1, 0)` at almost every review, since reviews follow each demand and
each delivery — and the other two expedite a unit instead of, or on
top of, a normal order. After that one order, every branch follows the
baseline policy, so the comparison isolates the decision at hand. Everything
else is the standard rollout setup:
`set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")`,
one `env.record("cost", ...)` stream that scores the branches, and no
triggering configuration, since NestedSimPy branches on the event
`decide` publishes.

Endogenous lead times are why this model needs nested simulation at
all: an order's delay depends on the queue it joins, so there is no
lead-time distribution to write down — but a launched branch carries the
whole production line with it, units in service included. The three
exponential sleeps are declared as `nested_timeout` distributions, so
at a branch point every pending sleep is resampled.

See {doc}`Implementing lookahead policies
<../topical-guides/lookahead-actions>` for the full contract, including
a two-argument decision form for models whose decision variables are
coupled.

