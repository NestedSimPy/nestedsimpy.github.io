"""
Machine shop example (nested-sim adaptation).

Covers:

- Interrupts
- Resources: PreemptiveResource

Scenario:
  A workshop has *n* identical machines. A stream of jobs (enough to
  keep the machines busy) arrives. Each machine breaks down
  periodically. Repairs are carried out by one repairman. The repairman
  has other, less important tasks to perform, too. Broken machines
  preempt these tasks. The repairman continues them when he is done
  with the machine repair. The workshop works continuously.
"""

import itertools

from _imports import *

# fmt: off
RANDOM_SEED = 42
PT_MEAN = 10.0         # Avg. processing time in minutes
PT_SIGMA = 2.0         # Sigma of processing time
MTTF = 300.0           # Mean time to failure in minutes
BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
REPAIR_TIME = 30.0     # Time it takes to repair a machine in minutes
JOB_DURATION = 30.0    # Duration of other jobs in minutes
NUM_MACHINES = 10      # Number of machines in the machine shop
WEEKS = 4              # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60  # Simulation time in minutes
# fmt: on

NESTED_OUTPUT_FOLDER = set_nested_output_folder("simpy_examples", "machine_shop")


def time_per_part():
    """Return actual processing time for a concrete part."""
    t = random.normalvariate(PT_MEAN, PT_SIGMA)
    while t <= 0:
        t = random.normalvariate(PT_MEAN, PT_SIGMA)
    return t


def time_to_failure():
    """Return time until next failure for a machine."""
    return random.expovariate(BREAK_MEAN)


class Machine:
    """A machine produces parts and may get broken every now and then.

    If it breaks, it requests a *repairman* and continues the production
    after the it is repaired.

    A machine has a *name* and a number of *parts_made* thus far.

    """

    def __init__(self, env, machine_id, name, repairman):
        self.env = env
        self.machine_id = machine_id
        self.name = name
        self.parts_made = 0
        self.broken = False
        self.process = env.process(self.working(repairman))
        env.process(self.break_machine())

    def working(self, repairman):
        """Produce parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        Request a repairman when this happens.

        """
        while True:
            # Start making a new part
            done_in = time_per_part()
            while done_in:
                start = self.env.now
                try:
                    # Working on the part
                    yield self.env.nested_timeout(
                        {"distribution": "deterministic", "value": done_in},
                        label="processing",
                    )
                    done_in = 0  # Set to 0 to exit while loop.
                except simpy.Interrupt:
                    self.broken = True
                    done_in -= self.env.now - start  # How much time left?

                    # Request a repairman. This will preempt its "other_job".
                    with repairman.request(priority=1, job_id=self.machine_id) as req:
                        yield req
                        yield self.env.nested_timeout(
                            {"distribution": "deterministic", "value": REPAIR_TIME},
                            label="repair",
                        )

                    self.broken = False

            self.parts_made += 1

    def break_machine(self):
        """Break the machine every now and then."""
        while True:
            yield self.env.nested_timeout(
                {"distribution": "exponential", "lambda": BREAK_MEAN},
                label="time_to_failure",
            )
            if not self.broken:
                # Only break the machine if it is currently working.
                self.process.interrupt()


def other_jobs(env, repairman):
    """The repairman's other (unimportant) job."""
    other_job_ids = itertools.count(start=10_000)
    while True:
        # Start a new job
        done_in = JOB_DURATION
        while done_in:
            # Retry the job until it is done.
            # Its priority is lower than that of machine repairs.
            with repairman.request(priority=2, job_id=next(other_job_ids)) as req:
                yield req
                start = env.now
                try:
                    yield env.nested_timeout(
                        {"distribution": "deterministic", "value": done_in},
                        label="other_job",
                    )
                    done_in = 0
                except simpy.Interrupt:
                    done_in -= env.now - start


def main():
    """Run the nested-sim machine shop example and package the outputs."""

    random.seed(RANDOM_SEED)
    env = NestedEnvironment()
    env._ns_print_branch_summary = False

    # Output options first.
    env.set_output_options(out_dir=str(NESTED_OUTPUT_FOLDER), gzip_trace=False)
    env.set_post_processing_options(
        gzip_trace=False,
        package_latest=True,
        print_outputs=False,
        autoplot=DEFAULT_AUTOPLOT,
        autoplot_example="machine_shop",
    )
    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_triggering_objects(nested_id="repairman")
    env.set_triggering_conditions({"on": "arrival", "frequency": 10})
    env.set_outer_stopping_condition(timeout=SIM_TIME)
    # Inner settings.
    env.set_inner_repetitions(2)
    env.set_inner_stopping_condition(
        relative_time=120.0, triggering_customer_departs=True
    )

    repairman = NestedPreemptiveResource(env, capacity=1, nested_id="repairman")
    machines = [Machine(env, i, f"Machine {i}", repairman) for i in range(NUM_MACHINES)]
    env.process(other_jobs(env, repairman))
    env.nested_run()

    # Analysis/results
    print(f"Machine shop results after {WEEKS} weeks")
    for machine in machines:
        print(f"{machine.name} made {machine.parts_made} parts.")


if __name__ == "__main__":
    main()
