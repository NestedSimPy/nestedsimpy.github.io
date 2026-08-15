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
   baseline policy's choice. The baseline's own decision always
   competes as one more candidate — pass `include_baseline=False` to
   turn that off; a `None` entry in `ACTIONS` is the same declaration
   made explicit. At each decision epoch NestedSimPy creates copies of
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

The nested file has each order chosen by lookahead instead. The full
file first, with every change against the plain version highlighted;
the three modifications are discussed below it:

```{codeannotate} ../../simpy_examples/inventory_lookahead_plain.py ../../simpy_examples/inventory_lookahead_nested.py
:title: simpy_examples/inventory_lookahead_nested.py
```

**The decision.** The policy function is identical in both files:

```python
def base_policy(state):
    """Order up to ORDER_UP_TO on the inventory position."""
    position = int(state["stock"].level) + int(state["pipeline"].level)
    return max(0, ORDER_UP_TO - position)
```

A policy that decides several variables returns them as one tuple, for
example `return normal, emergency` — still one complete decision. A
callable object works the same way, so a policy class with parameters
of its own can go straight in. What changes between the files is the
decision line: the plain version calls `base_policy(state)`, the nested
version writes

```python
order = yield from env.decide(base_policy, state)
```

`env.decide` publishes a `"review"` event and NestedSimPy branches on
it, so no triggering configuration is needed. Pass `event="my_name"`
to use another name, and then configure that name explicitly with
`set_triggering_conditions({"on": "event", "name": "my_name"})`.

```{tip}
Two different mistakes look similar here. Forgetting `yield from` on
`env.decide` itself is caught: using the result raises a `TypeError`.
Forgetting it on one of *your own* functions that contains a decision
is not: a bare call raises no error — Python builds a generator object,
discards it, and the body silently never runs, so the model makes no
decisions at all. Every caller on the path to a decision needs
`yield from`. If the decision sits directly in your process loop, as in
this example, nothing extra is needed.
```

**The actions.** One entry per candidate, in the shape the policy
returns. The baseline's own decision competes automatically; this file
lists `None` explicitly, which is the same declaration made visible:

```python
ACTIONS = [None, 0, 5, 10]
```

A policy that decides several variables makes each action `None` or a
full tuple of the same shape, for example `[None, (0, 1), (1, 1)]`. A
half-specified tuple such as `(None, 1)` is rejected: either the
baseline policy decides everything, or the action spells out every
variable. Scoring the branches needs one more line, wherever cost
arises:

```python
env.record("cost", period_cost)
```

`metric="cost"` in the configuration below names this stream of
recorded values; a branch's score is their sum over its window.

**The running mode**, set on `set_inner_actions` inside the
configuration block:

```python
env.set_outer_stopping_condition(timeout=8.5)  # half a period past the
#                                   last review, so the 8th completes
env.set_inner_stopping_condition(relative_time=4.0)
env.set_inner_repetitions(4)
env.set_rng("independent")
env.set_outer_seed(42)
env.set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")
env.nested_run()
```

`outer_run_mode="rollout"` executes each pick; switch it to
`"base_policy"` to score every decision while the trajectory stays on
the baseline rule.

### The output

Running the nested file prints the total (31.0 over eight periods for
this seed) and writes the rollout tables under the run directory.
`picks.csv` answers "what did each period choose" — one row per
decision epoch. A `base_policy` pick means no override: that period
executes whatever quantity the order-up-to rule itself computes.

| decision epoch | time | picked action | score of the pick |
|---|---|---|---|
| 0 | 1.0 | 5 | 12.00 |
| 1 | 2.0 | `base_policy` | 16.25 |
| 2 | 3.0 | 0 | 12.50 |
| 3 | 4.0 | 5 | 11.75 |
| 4 | 5.0 | `base_policy` | 10.75 |
| 5 | 6.0 | 0 | 15.00 |
| 6 | 7.0 | 5 | 11.75 |
| 7 | 8.0 | `base_policy` | 14.75 |

`actions.csv` keeps every candidate's score at every epoch — at the
first decision the board was `base_policy`: 16.8, `0`: 15.8, `5`: 12.0
(picked), `10`: 16.2 — and `branches.csv` / `decisions.csv` go one
level finer (one row per inner simulation, one row per decision inside
each inner simulation). {doc}`Raw data files <../api/raw-data>` documents all four.

## The configuration calls

| Call or argument | What it does |
| --- | --- |
| `set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")` | declare the candidates, score branches by their summed `"cost"` records, execute the best at each decision |
| `set_inner_actions(..., outer_run_mode="base_policy")` | score every decision but keep the outer run on its baseline policy — collect per-action data without changing the trajectory |
| `set_inner_actions(..., include_baseline=False)` | evaluate only the listed actions; by default the baseline's own decision competes as one more candidate |
| `set_inner_stopping_condition(relative_time=H)` | each branch runs `H` time units past the trigger point — the lookahead window |
| `set_inner_repetitions(K)` | `K` branches per action; the score is their mean |
| `set_inner_actions(..., minimize=False)` | pick the highest-scoring action instead — for reward metrics |

To score branches by something other than a recorded sum, register your
own metric of the same name with `env.register_metric` before
`set_inner_actions`; the registered one wins.

(coupled-decision-variables)=
## Coupled decision variables

Sometimes one variable of a decision can only be computed after
another is chosen. Take a dual-sourcing stock whose regular order tops
the inventory position up to `S_REG` — the right regular quantity
depends on how many units are expedited in the same decision, and on
the state at that moment, so a complete `(regular, expedited)` tuple
cannot be written into a static list.

For this case `env.decide` also accepts a policy with a second
parameter. Declare only the free variable as the actions, and let the
policy complete the decision:

```python
ACTIONS = [None, 1, 2]      # units to expedite now

def lookahead_policy(state, action):
    if action is None:
        return base_policy(state)
    expedited = int(action)
    regular = max(0, S_REG - state.position - expedited)
    return regular, expedited

regular, expedited = yield from env.decide(lookahead_policy, state)
```

Each branch calls the policy with its assigned action, and the outer
run executes what the policy returned for the winning one. `None`
keeps its meaning — the baseline rule's own decision — and everything
else on this page applies unchanged.

## Reading the results

```python
by_action = env.get_inner_results_by_action(metric="cost")
best = env.best_inner_action(trigger=0, metric="cost")
```

`get_inner_results_by_action` returns a dict keyed by decision index
(0, 1, ...); each value maps an action to its list of branch scores
(a branch that recorded nothing scores `0.0`; `None` marks a metric
that could not be evaluated). `best_inner_action` is the
lowest-scoring action at that decision (the highest with
`minimize=False`); in rollout mode, the decision executed in the outer
run always equals it.

Every run with declared actions also writes a `rollout/` folder in
the run directory — a `manifest.json` recording what produced the
files (including whether the picks were executed) and four CSV
files: `actions.csv` (per decision and
action: mean, standard deviation, replications, picked), `picks.csv`
(the pick per decision, executed in rollout mode; a `base_policy`
cell in `picked_action` is the baseline policy), `branches.csv` (one row
per inner simulation, with its seed and stop reason), and
`decisions.csv` (every decision inside every branch) — column details
in {doc}`Raw data <../api/raw-data>`.
`env.print_rollout_summary()` prints the per-decision summary, and
`nestedsimpy.reporting.write_rollout_plot(env)` draws the per-action
means with the executed picks starred. To read the folder back,
`nestedsimpy.reporting.load_rollout(run_dir)` (or
`OutputManager.rollout()`) returns the manifest and the four tables;
to compare the baseline policy against the lookahead run on the same
seeds, use `nestedsimpy.reporting.paired_runs`.

## What to expect

The picks start from your baseline policy and change only where the
estimates disagree with it. The gain depends on the baseline: a
mistuned rule leaves mistakes to correct, while against a well-tuned
one the noisy per-action estimates rarely change the pick. Two settings control the
trade-off: a longer window covers more of each action's consequences
but adds noise, and more replications per action steady the comparison
at the price of computation. When in doubt, keep the window short and
raise the replications first.

## How this is validated

The test suite pins the lookahead machinery against results computed by
hand, not against stored outputs of earlier runs.

**Single decision.** The classical newsvendor model -- one ordering
decision under uncertain demand, overage cost 1 and underage cost 3 per
unit, demand 0 or 4 with probabilities 0.25/0.75 -- has a closed-form
optimum: the critical-ratio formula gives order-up-to y\* = 4, and the
expected cost of every candidate is an exact finite sum (see any
inventory text, e.g. Porteus, *Foundations of Stochastic Inventory
Theory*, 2002). One seeded run of the test, 64 replications per action:

| order-up-to y | 0 | 1 | 2 | 3 | **4** | 5 | 6 |
|---|---|---|---|---|---|---|---|
| exact Q(y), by hand | 9 | 7 | 5 | 3 | **1** | 2 | 3 |
| simulated score | 9.19 | 7.13 | 5.06 | 3.00 | **0.94** | 1.94 | 2.94 |

NestedSimPy executed y = 4, the theoretical optimum; every score sits
within its analytic confidence bound, and sweep variants place the
optimum at the top, bottom and middle of the grid (y\* = 4, 0, 2) with
the executed pick matching each time.

**Five consecutive decisions.** A multi-period companion runs the same
kind of shop for five periods with backlogged demand and free, instant
replenishment. Under those conditions the provably optimal policy
orders up to the same critical level every period (Veinott,
"Optimal Policy for a Multi-Product, Dynamic, Nonstationary Inventory
Problem", *Management Science* 12(3):206-222,
[1965](https://pubsonline.informs.org/doi/10.1287/mnsc.12.3.206));
with zero ordering cost that level is again the critical-ratio y\*.
The executed pick must equal it at every decision, in two mirrored
cost settings:

| setting | theoretical y\* | executed picks (5 decisions) |
|---|---|---|
| shortage expensive | 4 | `[4, 4, 4, 4, 4]` |
| holding expensive | 1 | `[1, 1, 1, 1, 1]` |

The suite also asserts finer identities -- under common random numbers
some score comparisons are exact to float precision rather than
statistical -- but the headline is the row above: the executed decision
equals the provable optimum, every time.

## A larger example

For a larger model —
the dual-sourcing inventory model of Song, Xiao, Zhang and Zipkin
(2017), with endogenous lead times and the paper's own Dual-Index
policy as the baseline — see {doc}`Dual Sourcing with Lookahead
Expediting <../official-parity/dual-sourcing>`.
