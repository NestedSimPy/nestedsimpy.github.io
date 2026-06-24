"""
Bank renege example (nested-sim adaptation).

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege. Based on the
  program bank08.py from TheBank tutorial of SimPy 2. (KGM)
"""

from _imports import *

RANDOM_SEED = 42
NEW_CUSTOMERS = 5  # Total number of customers
INTERVAL_CUSTOMERS = 10.0  # Generate new customers roughly every x seconds
MIN_PATIENCE = 1  # Min. customer patience
MAX_PATIENCE = 3  # Max. customer patience

NESTED_OUTPUT_FOLDER = set_nested_output_folder("simpy_examples", "bank_reneging")


def source(env, number, interval, counter):
    """Source generates customers randomly"""

    for i in range(number):
        c = customer(env, f"Customer{i:02d}", counter, time_in_bank=12.0)
        env.process(c)
        # Interarrival time: exponential with mean `interval`.
        yield env.nested_timeout(
            {"distribution": "exponential", "lambda": 1.0 / interval},
            label="interarrival",
        )


def customer(env, name, counter, time_in_bank):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    user_print(f"{arrive:7.4f} {name}: Here I am", env=env)

    with counter.request() as req:
        patience = env.nested_timeout(
            {"distribution": "uniform", "low": MIN_PATIENCE, "high": MAX_PATIENCE},
            label="patience",
        )
        # Wait for the counter or abort at the end of our tether
        results = yield req | patience

        wait = env.now - arrive

        if req in results:
            # We got to the counter
            user_print(f"{env.now:7.4f} {name}: Waited {wait:6.3f}", env=env)
            yield env.nested_timeout(
                {"distribution": "exponential", "lambda": 1.0 / time_in_bank},
                label="service_time",
            )
            user_print(f"{env.now:7.4f} {name}: Finished", env=env)
        else:
            # We reneged
            user_print(f"{env.now:7.4f} {name}: RENEGED after {wait:6.3f}", env=env)


def main():
    """Run the bank reneging example in nested simulation and store the output files."""

    random.seed(RANDOM_SEED)
    env = NestedEnvironment()
    env._ns_print_branch_summary = False
    counter = NestedResource(env, capacity=1, nested_id="counter")

    env.process(source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS, counter))

    # Output options first.
    env.set_output_options(out_dir=str(NESTED_OUTPUT_FOLDER), gzip_trace=False)
    env.set_post_processing_options(
        gzip_trace=False,
        package_latest=True,
        print_outputs=False,
        autoplot=DEFAULT_AUTOPLOT,
        autoplot_example="bank_reneging",
    )
    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_triggering_objects(nested_id="counter")
    env.set_triggering_conditions({"on": "arrival", "frequency": 1})
    env.set_outer_stopping_condition(timeout=None, max_arrivals=None)
    # Inner settings.
    env.set_inner_repetitions(2)
    env.set_inner_stopping_condition(
        relative_time=None, triggering_customer_departs=True
    )

    env.nested_run()


if __name__ == "__main__":
    main()
