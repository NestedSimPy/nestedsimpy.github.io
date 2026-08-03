"""
Periodic-review inventory with lookahead order decisions.

Covers:

- Lookahead actions: env.decide, set_inner_actions, outer_run_mode
- Scoring branches with recorded values (metric="cost")

Scenario:
  A stock faces Poisson demand each period. After demand, an order
  decision: the engine tries each candidate quantity in inner
  simulations (candidate first, the order-up-to rule afterwards) and
  executes the one with the lowest average cost. None is the
  order-up-to rule running as its own candidate.
"""

from _imports import *

import numpy as np

RANDOM_SEED = 42
PERIODS = 8                # review periods in the real run
MEAN_DEMAND = 5.0          # Poisson demand per period
HOLD_COST = 1.0            # per unit on hand per period
SHORTAGE_COST = 9.0        # per unit short per period (lost sales)
ORDER_UP_TO = 10           # the base rule's target position
ACTIONS = [None, 0, 5, 10]  # None = the base rule's own decision
LOOKAHEAD = 4              # periods each inner branch runs
REPS = 4                   # inner branches per candidate

NESTED_OUTPUT_FOLDER = set_nested_output_folder("simpy_examples",
                                                "inventory_lookahead")


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
        env.record("cost", period_cost)             # scores the branches
        state["cost"] += period_cost

        # The decision: publishes a "review" event (the branch trigger),
        # the engine forks one inner simulation per (action, replication)
        # and this line returns the winning quantity -- or the branch's
        # own candidate inside a branch, or base_policy(state) where
        # nothing applies.
        order = yield from env.decide(base_policy, state)
        if order > 0:
            state["pipeline"].put(order)            # arrives next period


def run():
    np.random.seed(RANDOM_SEED)
    env = NestedEnvironment()
    state = {
        "net_inventory": 10,
        "pipeline": NestedContainer(env, capacity=float("inf"), init=0,
                                    nested_id="pipeline"),
        "cost": 0.0,
    }
    env.process(periods(env, state))

    # No triggering configuration: with actions declared, the engine
    # branches on the event decide publishes.
    env.set_outer_stopping_condition(timeout=PERIODS + 0.5)
    env.set_inner_stopping_condition(relative_time=float(LOOKAHEAD))
    env.set_inner_repetitions(REPS)
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")
    env.set_output_options(out_dir=NESTED_OUTPUT_FOLDER, gzip_trace=False)
    env.nested_run()
    return state["cost"], env


if __name__ == "__main__":
    total, env = run()
    by_action = env.get_inner_results_by_action(metric="cost")
    print(f"total cost {total:.1f} over {PERIODS} periods "
          f"({len(by_action)} decisions)")
    first = min(by_action)
    for action, values in sorted(by_action[first].items(), key=lambda i: str(i[0])):
        valid = [v for v in values if v is not None]
        mean = sum(valid) / len(valid) if valid else float("nan")
        pick = " <- executed" if action == env.best_inner_action(
            trigger=first, metric="cost") else ""
        print(f"  first decision, action {action!r:6}: mean {mean:6.1f}{pick}")
