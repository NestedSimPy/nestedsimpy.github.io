# Dual Sourcing with Lookahead Expediting

## Scenario

A NestedSimPy-specific example (not from the SimPy documentation): the
dual-sourcing inventory model of Song, Xiao, Zhang and Zipkin (2017),
"Optimal Policies for a Dual-Sourcing Inventory Problem with Endogenous
Stochastic Leadtimes", *Operations Research* 65(2):379–395. A single
product faces unit Poisson demand with full backlogging; regular orders
ride a two-stage tandem production line, so lead times are endogenous
(ordering more congests the line), and an expedited order skips stage 1
for a premium per unit. The plain version follows the single-sourcing
base rule — top the inventory position up to `S_REG` with regular
orders, never expedite. The nested version decides at each demand
epoch whether to expedite, by trying each candidate order in inner
simulations launched from the live production line.

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

The policy function is the plain file's `base_policy`, unchanged, and
it goes into the decision line as is:

```python
ACTIONS = [None, (0, 1), (1, 1)]

regular, expedited = yield from env.decide(base_policy, state)
```

Each action is a complete `(regular, expedited)` order, in the shape
the policy returns, and a branch executes its candidate exactly as
written: `(0, 1)` expedites a unit instead of ordering it normally,
`(1, 1)` expedites one on top of a regular order, and `None` is the
base rule running as its own candidate. After that one order, every
branch follows the base rule, so the comparison isolates the decision
at hand. Everything else is the standard rollout setup:
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

See {doc}`Choosing actions by lookahead
<../topical-guides/lookahead-actions>` for the full contract, including
a two-argument decision form for models whose decision variables are
coupled.

Measured over ten paired seeds at the file's horizon, single sourcing
averages 501.0 (standard error 216.6 — heavy-tailed, one congestion
spiral reached 2373) against 390.5 (89.9) for the lookahead run, which
wins pointwise on only three seeds of ten. The comparison reads as
insurance: on a typical seed the expedite premiums cost a little, and
on the spiral seeds expediting breaks the congestion before it
compounds, cutting the worst run from 2373 to 1163 — and with it the
mean and the variance.
