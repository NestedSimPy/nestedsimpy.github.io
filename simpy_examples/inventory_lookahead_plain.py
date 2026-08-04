"""
Periodic-review inventory example.

Covers:

- A periodic process with an order decision each period
- Containers: Container

Scenario:
  A stock faces Poisson demand each period. After demand, an order
  decision: the order-up-to rule looks at the inventory position (on
  hand plus in the pipeline) and orders the shortfall. Orders arrive
  one period later. Holding and shortage costs accrue per period.
"""

import numpy as np
import simpy

RANDOM_SEED = 42
PERIODS = 8                # review periods
MEAN_DEMAND = 5.0          # Poisson demand per period
HOLD_COST = 1.0            # per unit on hand per period
SHORTAGE_COST = 9.0        # per unit short per period (lost sales)
ORDER_UP_TO = 10           # the rule's target position


def base_policy(state):
    """Order up to ORDER_UP_TO on the inventory position."""
    position = state["net_inventory"] + int(state["pipeline"].level)
    return max(0, ORDER_UP_TO - position)


def periods(env, state):
    while True:
        yield env.timeout(1.0)
        landing = int(state["pipeline"].level)      # last period's order
        if landing:
            state["pipeline"].get(landing)
            state["net_inventory"] += landing
        state["net_inventory"] -= int(np.random.poisson(MEAN_DEMAND))
        on_hand = max(state["net_inventory"], 0)
        short = max(-state["net_inventory"], 0)
        state["net_inventory"] = on_hand            # lost sales

        period_cost = HOLD_COST * on_hand + SHORTAGE_COST * short
        state["cost"] += period_cost

        order = base_policy(state)
        if order > 0:
            state["pipeline"].put(order)            # arrives next period


def run():
    np.random.seed(RANDOM_SEED)
    env = simpy.Environment()
    state = {
        "net_inventory": 10,
        "pipeline": simpy.Container(env, capacity=float("inf"), init=0),
        "cost": 0.0,
    }
    env.process(periods(env, state))
    env.run(until=PERIODS + 0.5)
    return state["cost"]


if __name__ == "__main__":
    total = run()
    print(f"total cost {total:.1f} over {PERIODS} periods")
