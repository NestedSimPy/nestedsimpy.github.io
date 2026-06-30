"""
Carwash example (nested-sim adaptation).

Covers:

- Waiting for other processes
- Resources: Resource

Scenario:
  A carwash has a limited number of washing machines and defines
  a washing processes that takes some (random) time.

  Car processes arrive at the carwash at a random time. If one washing
  machine is available, they start the washing process and wait for it
  to finish. If not, they wait until they can use one.
"""

import itertools

from _imports import *

# fmt: off
RANDOM_SEED = 42
NUM_MACHINES = 2  # Number of machines in the carwash
WASHTIME = 5      # Minutes it takes to clean a car
T_INTER = 7       # Create a car every ~7 minutes
SIM_TIME = 20     # Simulation time in minutes
# fmt: on

# Base output root; nested_run post-processing will create
# run_id/raw and run_id/exports.
NESTED_OUTPUT_FOLDER = set_nested_output_folder("simpy_examples", "carwash")


class Carwash:
    """A carwash has a limited number of machines (``NUM_MACHINES``) to
    clean cars in parallel.

    Cars have to request one of the machines. When they got one, they
    can start the washing processes and wait for it to finish (which
    takes ``washtime`` minutes).

    """

    def __init__(self, env, num_machines, washtime):
        self.env = env
        # Register so nested env can find it by nested_id during branching.
        self.machine = env.register(NestedResource(env, num_machines, nested_id="wash"))
        self.washtime = washtime

    def wash(self, car):
        """The washing processes. It takes a ``car`` processes and tries
        to clean it."""
        yield self.env.nested_timeout(
            {"distribution": "deterministic", "value": self.washtime}, label="wash_time"
        )
        pct_dirt = random.randint(50, 99)
        print(f"Carwash removed {pct_dirt}% of {car}'s dirt.")


def car(env, name, cw):
    """The car process (each car has a ``name``) arrives at the carwash
    (``cw``) and requests a cleaning machine.

    It then starts the washing process, waits for it to finish and
    leaves to never come back ...

    """
    print(f"{name} arrives at the carwash at {env.now:.2f}.")
    with cw.machine.request() as request:
        yield request

        print(f"{name} enters the carwash at {env.now:.2f}.")
        yield env.process(cw.wash(name))

        print(f"{name} leaves the carwash at {env.now:.2f}.")


def setup(env, carwash, t_inter):
    """Create initial cars and keep creating cars approx. every ``t_inter`` minutes."""
    car_count = itertools.count()

    # Create 4 initial cars
    for _ in range(4):
        env.process(car(env, f"Car {next(car_count)}", carwash))

    # Create more cars while the simulation is running
    while True:
        delay = random.randint(t_inter - 2, t_inter + 2)
        yield env.nested_timeout(
            {"distribution": "deterministic", "value": delay}, label="interarrival"
        )
        env.process(car(env, f"Car {next(car_count)}", carwash))


def main():
    """Run the nested-sim variant and package the outputs."""

    random.seed(RANDOM_SEED)
    env = NestedEnvironment()
    env._ns_print_branch_summary = False
    carwash = Carwash(env, NUM_MACHINES, WASHTIME)
    # Output options first.
    env.set_output_options(out_dir=str(NESTED_OUTPUT_FOLDER), gzip_trace=False)
    env.set_post_processing_options(
        gzip_trace=False,
        package_latest=True,
        print_outputs=False,
        autoplot=DEFAULT_AUTOPLOT,
        autoplot_example="carwash",
    )
    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_triggering_objects(nested_id="wash")
    env.set_triggering_conditions({"on": "arrival", "frequency": 1})
    env.set_outer_stopping_condition(timeout=SIM_TIME)
    # Inner settings.
    env.set_inner_repetitions(2)
    env.set_inner_stopping_condition(
        relative_time=20.0, triggering_customer_departs=True
    )

    env.process(setup(env, carwash, T_INTER))

    env.nested_run()


if __name__ == "__main__":
    main()
