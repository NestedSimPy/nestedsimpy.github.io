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
orders, never expedite. The nested version decides at each review how
many units to expedite, by trying each expedite count in inner
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

This pair is the worked example of the **two-argument decision form**.
The decision here has two variables — how many units to order regular
and how many to expedite — and they are coupled: the regular order tops
the position up to `S_REG` only *after* the expedite count is known. A
fixed tuple like `(3, 1)` cannot express the candidate "expedite 1",
because the right regular quantity depends on the state at the moment
of the decision. So instead of passing the base policy and letting
NestedSimPy execute the action as given, the model keeps a policy with
a second parameter and completes the decision itself:

```python
def lookahead_policy(state, action):
    if action is None:
        return base_policy(state)
    expedited = int(action)
    regular = max(0, S_REG - state.position - expedited)
    return regular, expedited

regular, expedited = yield from env.decide(lookahead_policy, state)
```

An action is now just the expedite count, and `None` stays in `ACTIONS`
as usual — the base rule running as its own candidate; the policy maps
it to `base_policy(state)`. Everything else is the standard rollout
setup: `set_inner_actions(ACTIONS, metric="cost",
outer_run_mode="rollout")`, one `env.record("cost", ...)` stream that
scores the branches, and no triggering configuration, since
NestedSimPy branches on the event `decide` publishes.

Endogenous lead times are why this model needs nested simulation at
all: an order's delay depends on the queue it joins, so there is no
lead-time distribution to write down — but a launched branch carries the
whole production line with it, units in service included. The three
exponential sleeps are declared as `nested_timeout` distributions, so
at a branch point every pending sleep is resampled.

See {doc}`Choosing actions by lookahead
<../topical-guides/lookahead-actions>` for the full contract, including
when the plain one-argument form is enough.

Measured over ten paired seeds at the file's horizon, single sourcing
averages 501.0 (standard error 216.6 — heavy-tailed, one congestion
spiral reached 2372) against 355.8 (51.8) for the lookahead run, which
wins pointwise on only two seeds of ten. The comparison reads as
insurance: on a typical seed the expedite premiums cost a little, and
on the spiral seeds expediting breaks the congestion before it
compounds, collapsing the tail and with it the mean and the variance.
