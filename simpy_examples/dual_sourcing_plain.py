"""
Dual-sourcing inventory example -- single-sourcing base rule.

Covers:

- Continuous review with endogenous lead times (orders queue in a
  production line, so ordering more lengthens the lead times)
- Resources: Resource (two single-server production stages in tandem)

Scenario:
  The dual-sourcing model of Song, Xiao, Zhang and Zipkin (2017),
  "Optimal Policies for a Dual-Sourcing Inventory Problem with
  Endogenous Stochastic Leadtimes", Operations Research 65(2):379-395.
  A single product faces unit Poisson demand with full backlogging.
  The regular supply channel is a two-stage tandem production line
  (one unit at a time, exponential service at each stage), so lead
  times are endogenous: ordering more congests the line and lengthens
  them, and orders never cross. An expedited order skips stage 1 and
  joins stage 2 directly, for a premium per unit. The policy here is
  single sourcing: after every demand and every delivery, top the
  inventory position up to S_REG with regular orders, never expedite
  -- so every unit rides the congested two-stage line.
"""

from dataclasses import dataclass

import numpy as np
import simpy

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


def accrue(env, state, costs, last_accrual):
    """Charge holding/backlog cost since the last change of net."""
    dt = env.now - last_accrual[0]
    costs["holding"] += HOLD_COST * max(state.net, 0) * dt
    costs["backorder"] += BACKLOG_COST * max(-state.net, 0) * dt
    last_accrual[0] = env.now


def produced_unit(env, sim, expedited):
    """One ordered unit's life until it reaches inventory."""
    state = sim["state"]
    if not expedited:
        with sim["stage1"].request() as turn:
            yield turn
            yield env.timeout(np.random.exponential(1 / STAGE1_RATE))
        state.stage1 -= 1
        state.stage2 += 1
    with sim["stage2"].request() as turn:
        yield turn
        yield env.timeout(np.random.exponential(1 / STAGE2_RATE))
    state.stage2 -= 1
    accrue(env, state, sim["costs"], sim["last_accrual"])
    state.net += 1                                  # delivery
    review(env, sim)


def review(env, sim):
    """Consult the policy and launch its orders into the supply system."""
    state = sim["state"]
    regular, expedited = base_policy(state)
    sim["counts"]["regular"] += regular
    sim["counts"]["expedited"] += expedited
    sim["costs"]["ordering"] += expedited * EXPEDITE_PREMIUM
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
        yield env.timeout(np.random.exponential(1 / DEMAND_RATE))
        state = sim["state"]
        accrue(env, state, sim["costs"], sim["last_accrual"])
        state.net -= 1                              # backlog if negative
        review(env, sim)


def run():
    np.random.seed(RANDOM_SEED)
    env = simpy.Environment()
    sim = {
        "state": State(net=INIT_NET, stage1=0, stage2=0),
        "stage1": simpy.Resource(env, capacity=1),
        "stage2": simpy.Resource(env, capacity=1),
        "costs": {"holding": 0.0, "backorder": 0.0, "ordering": 0.0},
        "counts": {"regular": 0, "expedited": 0},
        "last_accrual": [0.0],
    }
    env.process(demand_process(env, sim))
    review(env, sim)                    # initial ordering decision at t=0
    env.run(until=HORIZON)
    accrue(env, sim["state"], sim["costs"], sim["last_accrual"])
    total = sum(sim["costs"].values())
    return total, sim


if __name__ == "__main__":
    total, sim = run()
    print(f"single sourcing (order up to {S_REG}): "
          f"total cost {total:.1f} over {HORIZON:.0f} "
          f"({total / HORIZON:.2f} per unit time)")
    print(f"  ordered {sim['counts']['regular']} regular, "
          f"{sim['counts']['expedited']} expedited; ending net "
          f"{sim['state'].net}, in line {sim['state'].stage1}+"
          f"{sim['state'].stage2}")
