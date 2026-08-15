# Implementing lookahead policies

*Executing and evaluating a rollout of a baseline policy.*

NestedSimPy can also use its inner simulations to *choose* between
actions: it executes and evaluates a **one-step lookahead** of a
**baseline policy**, which can serve as a building block for iterative
policy optimization. At user-defined decision points, NestedSimPy can
launch multiple inner simulations per candidate action, with each inner
simulation applying one of the candidate actions (exactly once) and
then following the user-provided baseline policy. The actions are
evaluated and the best action can be executed by the outer simulation
(alternatively, the outer simulation may follow the baseline policy and
simply report on the performance of candidate actions at decision
epochs).

Implementing rollout requires three modifications to the simulation
code:

1. **Defining the decision.** The command
   `yield from env.decide(base_policy, state)` executes the baseline
   policy. The function `base_policy()` returns an action for a given
   system state (`base_policy` is a Python function and `state` is a
   user-defined object that represents the system state, maintained by
   the user). The policy should not return the value `None`, which
   NestedSimPy reserves to stand for the baseline policy's own
   decision. Note that each `decide` call marks a decision epoch.
2. **Registering the actions.** `set_inner_actions(ACTIONS, metric="cost", ...)`
   declares the alternatives to the baseline policy. These are the
   values that `env.decide` returns in the inner simulations: each
   inner simulation executes its assigned value once instead of the
   baseline policy's choice. By default NestedSimPy also evaluates the baseline
   policy's own decision alongside these candidates, so every
   comparison includes "keep the baseline's choice". At each decision epoch NestedSimPy creates copies of
   the outer simulation — one per action and inner replication — and
   each copy evaluates the policy that first applies its assigned
   action and thereafter follows the baseline policy. The parameter
   `metric` names the user-defined key under which the model records
   values; each inner simulation's recorded total is its score, and
   the scores determine the best action.
3. **Setting the running mode.** The parameter `outer_run_mode`
   determines whether the outer simulation acts on the best action
   (`outer_run_mode="rollout"`) or follows the baseline policy
   (`outer_run_mode="base_policy"`), in which case NestedSimPy only
   collects the evaluation of the lookahead policy at each decision
   epoch.

## An example

The example below illustrates a rollout implementation in the context
of a periodic-review inventory model. In each period the sequence of
events is: the previous period's order arrives, demand realizes,
holding and shortage costs are incurred, and an order decision is
made.

- Plain SimPy: [`simpy_examples/inventory_lookahead_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/inventory_lookahead_plain.py)
- NestedSimPy: [`simpy_examples/inventory_lookahead_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/inventory_lookahead_nested.py)

### No rollout

Assume that in each period random demand, modeled with a Poisson
distribution, is realized. The user then makes a decision about the
order quantity. The baseline policy we wish to improve is the
order-up-to rule that considers the inventory position (on hand plus
in the pipeline) and orders up to a prespecified level. For
simplicity, we assume orders arrive one period later. Holding and
shortage costs accrue per period. The code below implements this
model and runs it for eight periods:

```{literalinclude} ../../simpy_examples/inventory_lookahead_plain.py
:language: python
:caption: simpy_examples/inventory_lookahead_plain.py
```

### Rollout

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_inventory_lookahead.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

The nested file has each order chosen by lookahead instead. Every
change against the plain version is highlighted:

```{codeannotate} ../../simpy_examples/inventory_lookahead_plain.py ../../simpy_examples/inventory_lookahead_nested.py
:title: simpy_examples/inventory_lookahead_nested.py
```

The three modifications, as they appear in the code:

**1. The decision.** `base_policy` itself is unchanged; the call to it
becomes the decision line:

```python
order = yield from env.decide(base_policy, state)
```

```{tip}
`yield from` is required — on `env.decide` and on any of your own
functions on the way to a decision. A bare call raises no error and
silently makes no decisions.
```

**2. The actions and the score.** Declare the candidate order
quantities, and record the cost wherever it arises — `metric="cost"`
in the configuration sums these records into each branch's score:

```python
ACTIONS = [0, 5, 10]
```

```python
env.record("cost", period_cost)
```

NestedSimPy adds the baseline policy's own decision to the comparison
automatically; the output tables show it as `base_policy`.

**3. The running mode.** The configuration block at the end of the
file:

```python
env.set_outer_stopping_condition(timeout=8.5)
env.set_inner_stopping_condition(relative_time=4.0)  # lookahead window
env.set_inner_repetitions(4)                         # branches per action
env.set_rng("independent")
env.set_outer_seed(42)
env.set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")
env.nested_run()
```

`outer_run_mode="rollout"` executes the best candidate at every
decision; `"base_policy"` follows the baseline and only collects the
scores.

### The output

Running the nested file prints the total cost (39.0 for this seed) and
writes four CSV tables to the run directory. `picks.csv` is the story
of the run — what each decision chose (`base_policy` means no
override: the rule's own order was best):

| decision epoch | time | picked action | score of the pick |
|---|---|---|---|
| 0 | 1.0 | `base_policy` | 10.75 |
| 1 | 2.0 | `base_policy` | 17.00 |
| 2 | 3.0 | `base_policy` | 16.50 |
| 3 | 4.0 | 0 | 11.50 |
| 4 | 5.0 | 10 | 14.25 |
| 5 | 6.0 | 0 | 14.25 |
| 6 | 7.0 | 10 | 16.75 |
| 7 | 8.0 | 0 | 15.25 |

`actions.csv` holds every candidate's score at every decision — at the
first one: `base_policy`: 10.8 (picked), `0`: 11.8, `5`: 13.2, `10`:
17.8. `branches.csv` and `decisions.csv` go one level finer;
{doc}`Raw data files <../api/raw-data>` lists all columns. In code,
`env.get_inner_results_by_action(metric="cost")` returns the same
scores keyed by decision and action, `env.best_inner_action(...)` the
winner, and `env.print_rollout_summary()` prints the per-decision
boards; `nestedsimpy.reporting` adds plot and load helpers
(`write_rollout_plot`, `load_rollout`, `paired_runs`).

## The configuration calls

| Call or argument | What it does |
| --- | --- |
| `set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")` | declare the candidates, score branches by their summed `"cost"` records, execute the best at each decision |
| `set_inner_actions(..., outer_run_mode="base_policy")` | score every decision but keep the outer run on its baseline policy |
| `set_inner_actions(..., include_baseline=False)` | evaluate only the listed actions; by default the baseline's own decision competes as one more candidate |
| `set_inner_stopping_condition(relative_time=H)` | each branch runs `H` time units past the trigger point — the lookahead window |
| `set_inner_repetitions(K)` | `K` branches per action; the score is their mean |
| `set_inner_actions(..., minimize=False)` | pick the highest-scoring action instead — for reward metrics |

To score branches by something other than a recorded sum, register a
metric of the same name with `env.register_metric` before the run.

## What to expect

The picks start from your baseline policy and change only where the
estimates disagree with it. The gain depends on the baseline: a
mistuned rule leaves mistakes to correct, while against a well-tuned
one the noisy per-action estimates rarely change the pick. A longer
window sees more of each action's consequences but adds noise; more
replications steady the comparison at the price of computation. When
in doubt, keep the window short and raise the replications first.

## How this is validated

The test suite checks the machinery against textbook problems whose
answers are known exactly — not against stored outputs of earlier
runs. In the classical newsvendor problem (overage cost 1, underage
cost 3, demand 0 or 4 with probabilities 0.25/0.75) the optimal
order-up-to level is y\* = 4 and every candidate's expected cost is
computable by hand. One seeded test run, 64 replications per action:

| order-up-to y | 0 | 1 | 2 | 3 | **4** | 5 | 6 |
|---|---|---|---|---|---|---|---|
| exact Q(y), by hand | 9 | 7 | 5 | 3 | **1** | 2 | 3 |
| simulated score | 9.19 | 7.13 | 5.06 | 3.00 | **0.94** | 1.94 | 2.94 |

The executed pick was 4, and sweep variants with the optimum at the
top, bottom and middle of the grid (y\* = 4, 0, 2) match theory the
same way. A five-period companion uses the base-stock result of
inventory theory (Veinott, *Management Science* 12(3):206-222,
[1965](https://pubsonline.informs.org/doi/10.1287/mnsc.12.3.206)):
under its conditions the provably optimal policy orders up to the same
level every period, and the executed picks came out `[4, 4, 4, 4, 4]`
— and `[1, 1, 1, 1, 1]` in a mirrored cost setting. Under common
random numbers some score comparisons are exact to float precision,
and the suite asserts them as exact.

## A larger example

For a larger model —
the dual-sourcing inventory model of Song, Xiao, Zhang and Zipkin
(2017), with endogenous lead times and the paper's own Dual-Index
policy as the baseline — see {doc}`Dual Sourcing with Lookahead
Expediting <../official-parity/dual-sourcing>`.
