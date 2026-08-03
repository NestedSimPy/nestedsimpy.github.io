# Choosing actions by lookahead

NestedSimPy can use its inner simulations to *choose* between actions,
not only to evaluate the future. At a decision point, the engine forks
one inner simulation per candidate action, lets each branch take its
candidate once and then follow your base policy, scores every branch
over a lookahead window, and executes the action with the best average.
The real run continues, and the same happens at the next decision.

## The two contracts

Everything on this page follows from two rules:

- **The policy** is your plain model's policy, unchanged: state in, one
  complete decision out. It never sees an action and never returns
  `None` — the lookahead machinery is invisible from inside it.
- **An action** is either `None` ("the base policy decides") or a
  complete decision, executed exactly as written. A half-specified
  action such as `(None, 1)` is rejected.

## What you write

Four things. The model below is a periodic-review stock: demand each
period, then an order decision.

**The actions.** One entry per candidate, in the shape the policy
returns. Keep `None` in the list so "change nothing" always competes:

```python
ACTIONS = [None, 0, 5, 10]
```

A policy that decides several variables returns a tuple, and each
action is then `None` or a full tuple of the same shape, for example
`[None, (0, 1), (1, 1)]`.

**The decision line**, wherever the model consulted its policy. The
policy object itself goes in, and `yield from` is required — using the
result without it raises an error that says so:

```python
order = yield from env.decide(base_policy, state)
```

`env.decide` publishes a `"review"` event and the engine branches on
it, so no triggering configuration is needed. Pass `event="my_name"`
to use another name, and then configure that name explicitly with
`set_triggering_conditions`.

**The cost line**, wherever cost arises. By default the scoring metric
sums the branch's own recorded values over its window:

```python
env.record("cost", period_cost)
```

**The configuration block:**

```python
env.set_outer_stopping_condition(timeout=PERIODS + 0.5)
env.set_inner_stopping_condition(relative_time=LOOKAHEAD)
env.set_inner_repetitions(REPS)
env.set_rng("independent")
env.set_outer_seed(seed)
env.set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")
env.nested_run()
```

## One rule about `yield from`

Because a function containing `env.decide` is a generator, every caller
on the path to a decision must call it with `yield from`. A bare call
raises no error — the body silently never runs, and the model makes no
decisions at all. If the decision sits directly in your process loop,
as above, nothing extra is needed.

## The configuration calls

| Call | What it does |
| --- | --- |
| `set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")` | declare the candidates, score branches by their summed `"cost"` records, execute the best at each decision |
| `outer_run_mode="base_policy"` | score every decision but keep the real run on its base policy — collect per-action data without changing the trajectory |
| `set_inner_stopping_condition(relative_time=H)` | each branch runs `H` time units past its fork — the lookahead window |
| `set_inner_repetitions(K)` | `K` branches per action; the score is their mean |
| `minimize=False` | pick the argmax instead — for reward metrics |

To score branches by something other than a recorded sum, register your
own metric of the same name with `register_metric` before
`set_inner_actions`; the registered one wins.

## Reading the results

```python
by_action = env.get_inner_results_by_action(metric="cost")
best = env.best_inner_action(trigger=0, metric="cost")
```

`get_inner_results_by_action` returns, per decision, one list of branch
scores per action; `best_inner_action` is the per-decision argmin (or
argmax). The decision executed in the real run always equals it.

## What to expect

Lookahead selection inherits your base policy and repairs its
weaknesses. Against a mistuned base rule it can help substantially;
against a well-tuned one it roughly ties, because the argmin of noisy
estimates has nothing left to find. Two settings control the trade-off:
a longer window sees further but adds noise, and more replications per
action steady the comparison at the price of computation. When in
doubt, keep the window short and raise the replications first.
