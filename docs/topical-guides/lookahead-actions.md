# Implementing lookahead policies

*Executing and evaluating a rollout of a baseline policy.*

NestedSimPy can also use its inner simulations to *choose* between
actions: it executes and evaluates a **one-step lookahead** of a
**baseline policy**, a building block of iterative policy optimization.
At a decision point, NestedSimPy launches one inner simulation per
candidate action, lets each branch take its candidate once and then
follow the baseline policy (your plain model's rule), scores every
branch over a lookahead window, and executes the action with the best
average. The outer run continues, and the same happens at the next
decision. In dynamic optimization this is known as a **rollout
policy** — hence `outer_run_mode="rollout"` below.

Implementing a rollout takes three elements:

1. **Define the decision.** The decision line
   `yield from env.decide(base_policy, state)` executes the baseline
   policy: any function that returns one complete decision for a given
   system state (the state object is the user's own). The policy never
   sees an action and never returns `None` — the lookahead machinery is
   invisible from inside it. Each `decide` call marks a decision moment.
2. **Register the actions.** `set_inner_actions(ACTIONS, metric="cost")`
   declares the alternatives to the baseline policy. An action is either
   `None` ("the baseline policy decides") or a complete decision,
   executed exactly as written. At each decision moment NestedSimPy
   creates copies of the outer simulation — one per action and
   replication — and each copy evaluates the policy that first applies
   its assigned action and thereafter follows the baseline policy; a
   copy's score is the sum of its recorded metric values over the
   lookahead window.
3. **Set the running mode.** `outer_run_mode="rollout"` executes the
   best-scoring action at each decision of the outer run;
   `outer_run_mode="base_policy"` keeps the outer run on the baseline
   policy and only collects the scores.

One situation bends the rule in the first element — a decision whose
variables can only be computed together; see
{ref}`coupled-decision-variables` below.

## An example

The example is a periodic-review stock: demand each period, then an
order decision.

- Plain SimPy: [`simpy_examples/inventory_lookahead_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/inventory_lookahead_plain.py)
- NestedSimPy: [`simpy_examples/inventory_lookahead_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/inventory_lookahead_nested.py)

### No rollout

A stock faces Poisson demand each period. After demand, an order
decision: the order-up-to rule looks at the inventory position (on
hand plus in the pipeline) and orders the shortfall. Orders arrive
one period later. Holding and shortage costs accrue per period. The
plain file runs eight periods of exactly that:

```{literalinclude} ../../simpy_examples/inventory_lookahead_plain.py
:language: python
:caption: simpy_examples/inventory_lookahead_plain.py
```

### Rollout

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_inventory_lookahead.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

The nested file has each order chosen by lookahead instead. The three
elements, in the order they appear in the code:

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

**The actions.** One entry per candidate, in the shape the policy
returns. Keep `None` in the list so "let the baseline rule decide"
always competes:

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

The full file, with every change against the plain version highlighted:

```{codeannotate} ../../simpy_examples/inventory_lookahead_plain.py ../../simpy_examples/inventory_lookahead_nested.py
:title: simpy_examples/inventory_lookahead_nested.py
:context: 3
```

## One rule about `yield from`

Two different mistakes look similar here. Forgetting `yield from` on
`env.decide` itself is caught: using the result raises a `TypeError`.
Forgetting it on one of *your own* functions that contains a decision
is not: a bare call raises no error — Python builds a generator object,
discards it, and the body silently never runs, so the model makes no
decisions at all. Every caller on the path to a decision needs
`yield from`. If the decision sits directly in your process loop, as in
the example above, nothing extra is needed.

## The configuration calls

| Call or argument | What it does |
| --- | --- |
| `set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")` | declare the candidates, score branches by their summed `"cost"` records, execute the best at each decision |
| `set_inner_actions(..., outer_run_mode="base_policy")` | score every decision but keep the outer run on its baseline policy — collect per-action data without changing the trajectory |
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
(the pick per decision, executed in rollout mode; an empty
`picked_action` cell is the baseline policy), `branches.csv` (one row
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

## A larger example

For a model with more at stake —
the dual-sourcing inventory model of Song, Xiao, Zhang and Zipkin
(2017), with endogenous lead times and the paper's own Dual-Index
policy as the baseline — see {doc}`Dual Sourcing with Lookahead
Expediting <../official-parity/dual-sourcing>`.
