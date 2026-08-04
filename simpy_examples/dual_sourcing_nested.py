"""
Dual-sourcing inventory with lookahead expediting.

Covers:

- The two-argument decision form: env.decide(lookahead_policy, state)
  for coupled decision variables
- Lookahead actions: set_inner_actions, outer_run_mode="rollout"
- Redrawable delays: nested_timeout

Scenario:
  The dual-sourcing model of Song, Xiao, Zhang and Zipkin (2017),
  "Optimal Policies for a Dual-Sourcing Inventory Problem with
  Endogenous Stochastic Leadtimes", Operations Research 65(2):379-395.
  Same model as the plain version; the base rule is still single
  sourcing. The question "how many units to expedite right now" is
  answered by lookahead: at each demand epoch (and once at t=0),
  NestedSimPy tries each expedite count in inner simulations launched
  from the live production line and executes the best-scoring one.
  Deliveries replenish under the base rule, which keeps the decision
  count linear in demand.

  The two decision variables are coupled -- the regular order tops the
  position up to S_REG only AFTER the expedite count is known -- so an
  action cannot be a fixed (regular, expedited) tuple. The policy
  keeps the two-argument form lookahead_policy(state, action) and
  completes the decision itself; None stays in ACTIONS as the base
  rule's own candidate.

  Endogenous lead times are the point: an order's delay depends on the
  queue it joins, so there is no lead-time distribution to write down
  -- but a launched branch carries the whole production line with it,
  units in service included. The three exponential sleeps (demand
  interarrivals, both service times) are declared nested_timeout
  distributions, so at a fork every pending sleep is resampled.
"""

from _imports import *  # NestedSimPy names + shared example helpers

from dataclasses import dataclass

import numpy as np

RANDOM_SEED = 2024
DEMAND_RATE = 5.0        # Poisson demand (units per unit time)
STAGE1_RATE = 6.0        # exponential production rate, stage 1
STAGE2_RATE = 7.0        # exponential production rate, stage 2
HOLD_COST = 1.0          # per unit on hand per unit time
BACKLOG_COST = 9.0       # per unit backlogged per unit time
EXPEDITE_PREMIUM = 15.0  # extra cost per expedited unit
HORIZON = 30.0           # length of one run
INIT_NET = 10            # on-hand stock at time 0, empty pipeline
S_REG = 10               # order up to S_REG on the position (regular)

ACTIONS = [None, 1, 2]   # units to expedite now; None = the base rule
INNER_HORIZON = 4.0      # lookahead window, in time units
INNER_REPS = 12          # replications per action

DEMAND_DIST = {"distribution": "exponential", "rate": DEMAND_RATE}
STAGE1_DIST = {"distribution": "exponential", "rate": STAGE1_RATE}
STAGE2_DIST = {"distribution": "exponential", "rate": STAGE2_RATE}

NESTED_OUTPUT_FOLDER = set_nested_output_folder("simpy_examples",
                                                "dual_sourcing")


@dataclass
class State:
    net: int      # on-hand minus backlog (negative = backlogged)
    stage1: int   # units waiting at or in service at stage 1
    stage2: int   # units waiting at or in service at stage 2

    @property
    def position(self) -> int:
        return self.net + self.stage1 + self.stage2


def base_policy(state):
    """Single sourcing: top the position up to S_REG, never expedite."""
    return max(0, S_REG - state.position), 0


def lookahead_policy(state, action):
    """Complete the assigned action with the model's own coupling rule.

    The two decision variables are coupled (regular tops up to S_REG
    AFTER the expedite count is known), so a bare action cannot say
    both -- this policy takes the two-argument form and completes the
    decision itself. The action is the number of units to expedite
    now; None is the base rule's own decision."""
    if action is None:
        return base_policy(state)
    expedited = int(action)
    regular = max(0, S_REG - state.position - expedited)
    return regular, expedited


def accrue(env, state, costs, last_accrual):
    """Charge holding/backlog cost since the last change of net."""
    dt = env.now - last_accrual[0]
    increment = (HOLD_COST * max(state.net, 0)
                 + BACKLOG_COST * max(-state.net, 0)) * dt
    costs["holding"] += HOLD_COST * max(state.net, 0) * dt
    costs["backorder"] += BACKLOG_COST * max(-state.net, 0) * dt
    if increment:
        env.record("cost", increment)               # scores the branches
    last_accrual[0] = env.now


def produced_unit(env, sim, expedited):
    """One ordered unit's life until it reaches inventory."""
    state = sim["state"]
    if not expedited:
        with sim["stage1"].request() as turn:
            yield turn
            yield env.nested_timeout(STAGE1_DIST)   # redrawable service
        state.stage1 -= 1
        state.stage2 += 1
    with sim["stage2"].request() as turn:
        yield turn
        yield env.nested_timeout(STAGE2_DIST)       # redrawable service
    state.stage2 -= 1
    accrue(env, state, sim["costs"], sim["last_accrual"])
    state.net += 1                                  # delivery
    yield from review(env, sim, decide=False)


def review(env, sim, decide):
    """One review: decide (demand epochs) or follow the base rule."""
    state = sim["state"]
    if decide:
        regular, expedited = yield from env.decide(lookahead_policy, state)
    else:
        regular, expedited = base_policy(state)
    sim["counts"]["regular"] += regular
    sim["counts"]["expedited"] += expedited
    if expedited:
        premium = expedited * EXPEDITE_PREMIUM
        sim["costs"]["ordering"] += premium
        env.record("cost", premium)
    # Pipeline counts are updated at order time, so any later review at
    # the same instant already sees these orders.
    for _ in range(expedited):
        state.stage2 += 1
        env.process(produced_unit(env, sim, expedited=True))
    for _ in range(regular):
        state.stage1 += 1
        env.process(produced_unit(env, sim, expedited=False))


def demand_process(env, sim):
    while True:
        yield env.nested_timeout(DEMAND_DIST)       # redrawable interarrival
        state = sim["state"]
        accrue(env, state, sim["costs"], sim["last_accrual"])
        state.net -= 1                              # backlog if negative
        yield from review(env, sim, decide=True)


def run():
    np.random.seed(RANDOM_SEED)
    env = NestedEnvironment()
    sim = {
        "state": State(net=INIT_NET, stage1=0, stage2=0),
        "stage1": NestedResource(env, capacity=1, nested_id="stage1"),
        "stage2": NestedResource(env, capacity=1, nested_id="stage2"),
        "costs": {"holding": 0.0, "backorder": 0.0, "ordering": 0.0},
        "counts": {"regular": 0, "expedited": 0},
        "last_accrual": [0.0],
    }
    env.process(demand_process(env, sim))
    env.process(review(env, sim, decide=True))   # initial decision at t=0

    # No triggering configuration: with actions declared, NestedSimPy
    # branches on the event decide publishes.
    env.set_outer_stopping_condition(timeout=HORIZON)
    env.set_inner_stopping_condition(relative_time=INNER_HORIZON)
    env.set_inner_repetitions(INNER_REPS)
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")
    env.set_output_options(out_dir=NESTED_OUTPUT_FOLDER, gzip_trace=False)
    env.nested_run()
    accrue(env, sim["state"], sim["costs"], sim["last_accrual"])
    total = sum(sim["costs"].values())
    return total, sim, env


if __name__ == "__main__":
    total, sim, env = run()
    print(f"rollout over {len(ACTIONS)} expedite levels: "
          f"total cost {total:.1f} over {HORIZON:.0f} "
          f"({total / HORIZON:.2f} per unit time)")
    print(f"  ordered {sim['counts']['regular']} regular, "
          f"{sim['counts']['expedited']} expedited; ending net "
          f"{sim['state'].net}, in line {sim['state'].stage1}+"
          f"{sim['state'].stage2}")
