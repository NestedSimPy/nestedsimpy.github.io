# Implementing lookahead policies

*Executing and evaluating a rollout of a baseline policy.*

NestedSimPy can also use its inner simulations to *choose* between
actions: it executes and evaluates a **one-step lookahead** of a
**baseline policy**, which can serve as a building block for iterative
policy optimization.

At user-defined decision points, NestedSimPy can
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
   policy; in rollout mode it returns the best candidate found by the
   inner simulations (modification 3). The function `base_policy()`
   returns an action for a given system state (`base_policy` is a
   Python function and `state` is a user-defined object that represents
   the system state, maintained by the user). The policy should not
   return the value `None`, which NestedSimPy reserves to stand for the
   baseline policy's own decision. Note that each `decide` call marks a
   decision epoch.
2. **Registering the actions.** `set_inner_actions(ACTIONS, metric="cost", ...)`
   declares the alternatives to the baseline policy. These are the
   values that `env.decide` returns in the inner simulations: each
   inner simulation executes its assigned value once instead of the
   baseline policy's choice. At each decision epoch NestedSimPy creates
   copies of the outer simulation — one per action and inner
   replication — and each copy evaluates the policy that first applies
   its assigned action and thereafter follows the baseline policy. The
   parameter `metric` names the user-defined key under which the model
   records values; each inner simulation's recorded total is its score,
   and the scores determine the best action.
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
simplicity, we assume orders arrive one period later: each period
opens with the arrival of the previous period's order, then demand
realizes, holding and shortage costs are incurred, and the period
ends with the new order decision. The code below implements this
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
env.set_outer_stopping_condition(timeout=PERIODS + 0.5)
env.set_inner_stopping_condition(relative_time=float(INNER_HORIZON))
env.set_inner_repetitions(INNER_REPS)
env.set_rng("independent")
env.set_outer_seed(RANDOM_SEED)
env.set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")
env.set_output_options(out_dir=NESTED_OUTPUT_FOLDER, gzip_trace=False)
env.nested_run()
```

### The output

Running the nested file prints the total cost (39.0 for this seed) and
writes four CSV tables to the run directory. `picks.csv` is the story
of the run — what each decision chose (`base_policy` means no
override: the rule's own order was best):

| `trigger` (decision epoch) | `time` | `picked_action` | `mean` (the pick's score) |
|---|---|---|---|
| 0 | 1.0 | `base_policy` | 10.75 |
| 1 | 2.0 | `base_policy` | 17.00 |
| 2 | 3.0 | `base_policy` | 16.50 |
| 3 | 4.0 | 0 | 11.50 |
| 4 | 5.0 | 10 | 14.25 |
| 5 | 6.0 | 0 | 14.25 |
| 6 | 7.0 | 10 | 16.75 |
| 7 | 8.0 | 0 | 15.25 |

The other three tables go one level finer — `actions.csv` keeps every
candidate's score at every decision, `branches.csv` one row per inner
simulation, `decisions.csv` every decision inside each branch;
{doc}`Raw data files <../api/raw-data>` lists all columns. In code,
`env.print_rollout_summary()` shows the same numbers, one line per
decision with the pick starred:

```text
rollout summary (metric 'cost', 8 triggers, 4 actions)
  trigger  0 (t=1): 0:11.8  5:13.2  10:17.8  base_policy:10.8*
  trigger  1 (t=2): 0:17.2  5:17.8  10:22.8  base_policy:17.0*
  ...
```

`env.get_inner_results_by_action(metric="cost")` returns the scores as
a dict; plot and load helpers live in `nestedsimpy.reporting`.

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
metric of the same name with `env.register_metric`
({doc}`API reference <../api/simpy-core>`) before the run.

```{tip}
Expect gains where the baseline has mistakes to correct: this
example's simple rule is overridden at 5 of 8 decisions, while a
well-tuned rule keeps most of its picks. When tuning, keep the lookahead
window short and raise the replications first — a longer window sees
more of each action's consequences but is noisier; more replications
are steadier but cost compute.
```

## A larger example

For a larger model —
the dual-sourcing inventory model of Song, Xiao, Zhang and Zipkin
(2017), with endogenous lead times and the paper's own Dual-Index
policy as the baseline — see {doc}`Dual Sourcing with Lookahead
Expediting <../official-parity/dual-sourcing>`.
