"""
Process communication example (nested-sim adaptation).

Covers:

- Resources: Store

Scenario:
  This example shows how to interconnect simulation model elements
  together using :class:`~simpy.resources.store.Store` for one-to-one,
  and many-to-one asynchronous processes. For one-to-many a simple
  BroadCastPipe class is constructed from Store.

When Useful:
  When a consumer process does not always wait on a generating process
  and these processes run asynchronously. This example shows how to
  create a buffer and also tell is the consumer process was late
  yielding to the event from a generating process.

  This is also useful when some information needs to be broadcast to
  many receiving processes

  Finally, using pipes can simplify how processes are interconnected to
  each other in a simulation model.

Example By:
  Keith Smith
"""

import random

import simpy.core
from _imports import *

from tools.postprocess_helpers import wait_time_hook

RANDOM_SEED = 42
SIM_TIME = 100
NESTED_OUTPUT_FOLDER = set_nested_output_folder(
    "simpy_examples", "process_communication"
)


def _latest_run_dir(out_root: Path) -> Path:
    run_dirs = [path for path in out_root.iterdir() if path.is_dir()]
    if not run_dirs:
        raise FileNotFoundError(f"No runs found under {out_root}")
    return max(run_dirs, key=lambda path: path.stat().st_mtime)


class BroadcastPipe:
    """A Broadcast pipe that allows one process to send messages to many."""

    def __init__(
        self, env, nested_id: str = "bc_pipe", capacity: float = simpy.core.Infinity
    ):
        self.env = env
        self.nested_id = nested_id
        self.capacity = capacity
        self.pipes: list[NestedStore] = []

    def put(self, value):
        """Broadcast a *value* to all receivers."""
        if not self.pipes:
            raise RuntimeError("There are no output pipes.")
        events = [store.put(value) for store in self.pipes]
        return self.env.all_of(events)

    def get_output_conn(self):
        """Get a new output connection for this broadcast pipe."""
        idx = len(self.pipes)
        nested_id = f"{self.nested_id}_out{idx}"
        pipe = self.env.register(
            NestedStore(self.env, capacity=self.capacity, nested_id=nested_id)
        )
        self.pipes.append(pipe)
        return pipe


def message_generator(name, env, out_pipe):
    """A process which randomly generates messages."""
    msg_id = 0
    while True:
        yield env.nested_timeout(
            {"distribution": "deterministic", "value": random.randint(6, 10)},
            label="tx_delay",
        )
        msg = {
            "item_id": msg_id,
            "sent_time": env.now,
            "msg": f"{name} says hello at {env.now:g}",
        }
        msg_id += 1
        out_pipe.put(msg)


def message_consumer(name, env, in_pipe):
    """A process which consumes messages."""
    while True:
        msg = yield in_pipe.get()
        sent_time = msg.get("sent_time") if isinstance(msg, dict) else msg[0]
        text = msg.get("msg") if isinstance(msg, dict) else msg[1]
        if sent_time < env.now:
            user_print(
                f"LATE Getting Message: at time {env.now:g}: "
                f"{name} received message: {text}",
                env=env,
            )
        else:
            user_print(
                f"at time {env.now:g}: {name} received message: {text}.", env=env
            )
        yield env.nested_timeout(
            {"distribution": "deterministic", "value": random.randint(4, 8)},
            label="consumer_work",
        )


def run_one_to_one():
    """Run the one-to-one pipe communication scenario."""

    env = NestedEnvironment()
    env._ns_print_branch_summary = False
    pipe = env.register(
        NestedStore(env, capacity=simpy.core.Infinity, nested_id="pipe")
    )

    # Output options first.
    env.set_output_options(out_dir=str(NESTED_OUTPUT_FOLDER), gzip_trace=False)
    env.set_post_processing_options(
        gzip_trace=False,
        package_latest=True,
        print_outputs=False,
        autoplot=DEFAULT_AUTOPLOT,
        autoplot_example="process_communication",
        autoplot_skip_no_branch=True,
    )
    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_triggering_objects(nested_id="pipe")
    env.set_triggering_conditions({"on": "store_put", "frequency": 1})
    env.set_outer_stopping_condition(timeout=SIM_TIME)
    # Inner settings.
    env.set_inner_repetitions(1)
    env.set_inner_stopping_condition(
        relative_time=20.0, triggering_customer_departs=True
    )
    env.set_postprocessor(wait_time_hook)

    env.process(message_generator("Generator A", env, pipe))
    env.process(message_consumer("Consumer A", env, pipe))

    env.nested_run()
    return {"outer_dir": _latest_run_dir(NESTED_OUTPUT_FOLDER)}


def run_one_to_many():
    """Run the one-to-many broadcast pipe communication scenario."""

    env = NestedEnvironment()
    env._ns_print_branch_summary = False
    bc_pipe = BroadcastPipe(env, nested_id="bc_pipe")

    # Output options first.
    env.set_output_options(out_dir=str(NESTED_OUTPUT_FOLDER), gzip_trace=False)
    env.set_post_processing_options(
        gzip_trace=False,
        package_latest=True,
        print_outputs=False,
        autoplot=DEFAULT_AUTOPLOT,
        autoplot_example="process_communication",
        autoplot_skip_no_branch=True,
    )
    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_triggering_objects(nested_id=["bc_pipe_out0", "bc_pipe_out1"])
    env.set_triggering_conditions({"on": "store_put", "frequency": 1})
    env.set_outer_stopping_condition(timeout=SIM_TIME)
    # Inner settings.
    env.set_inner_repetitions(1)
    env.set_inner_stopping_condition(
        relative_time=20.0, triggering_customer_departs=True
    )
    env.set_postprocessor(wait_time_hook)

    env.process(message_generator("Generator A", env, bc_pipe))
    env.process(message_consumer("Consumer A", env, bc_pipe.get_output_conn()))
    env.process(message_consumer("Consumer B", env, bc_pipe.get_output_conn()))

    env.nested_run()
    return {"outer_dir": _latest_run_dir(NESTED_OUTPUT_FOLDER)}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments selecting the communication scenario."""

    parser = argparse.ArgumentParser(
        description="Run the process communication example."
    )
    parser.add_argument(
        "--mode",
        choices=["one-to-one", "one-to-many"],
        default="one-to-many",
        help="Which scenario to run (default: one-to-many).",
    )
    return parser.parse_args()


def main():
    """Entry point to run the selected process communication scenario."""

    print("Process communication (nested)")
    random.seed(RANDOM_SEED)
    args = parse_args()

    if args.mode == "one-to-one":
        pkg = run_one_to_one()
        print(f"One-to-one run directory: {pkg['outer_dir']}")
    else:
        pkg = run_one_to_many()
        print(f"One-to-many run directory: {pkg['outer_dir']}")


if __name__ == "__main__":
    main()
