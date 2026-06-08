"""
Event Latency example (nested-sim adaptation).

Covers:

- Resources: Store

Scenario:
  This example shows how to separate the time delay of events between
  processes from the processes themselves.

When Useful:
  When modeling physical things such as cables, RF propagation, etc.  it
  better encapsulation to keep this propagation mechanism outside of the
  sending and receiving processes.

  Can also be used to interconnect processes sending messages

Example by:
  Keith Smith
"""

import itertools

from _imports import *

SIM_DURATION = 100
NESTED_OUTPUT_FOLDER = set_nested_output_folder("simpy_examples", "event_latency")


class Cable:
    """This class represents the propagation through a cable."""

    def __init__(self, env, delay):
        self.env = env
        self.delay = delay
        self.store = env.register(
            NestedStore(env, capacity=float("inf"), nested_id="cable_store")
        )

    def latency(self, value):
        """Delay ``value`` before placing it into the downstream store."""

        yield self.env.nested_timeout(
            {"distribution": "deterministic", "value": self.delay}, label="cable_delay"
        )
        yield self.store.put(value)

    def put(self, value):
        """Public API: schedule a value to traverse the cable."""
        self.env.process(self.latency(value))

    def get(self):
        """Public API: retrieve the next delivered value."""
        return self.store.get()


def sender(env, cable):
    """A process which randomly generates messages."""
    msg_id = itertools.count()
    while True:
        yield env.nested_timeout(
            {"distribution": "deterministic", "value": 5}, label="send_interval"
        )
        cid = next(msg_id)
        cable.put({"item_id": cid, "msg": f"Sender sent this at {env.now:g}"})


def receiver(env, cable):
    """A process which consumes messages."""
    while True:
        msg = yield cable.get()
        text = msg.get("msg") if isinstance(msg, dict) else msg
        user_print(f"Received this at {env.now:g} while {text}", env=env)


def main():
    """Run the nested-sim event latency example and package the outputs.

    Returns:
        None. Writes nested outputs under the configured folder.
    """

    print("Event Latency (nested)")
    env = NestedEnvironment()
    env._ns_print_branch_summary = False
    cable = Cable(env, 10)
    # Output options first.
    env.set_output_options(out_dir=str(NESTED_OUTPUT_FOLDER), gzip_trace=False)
    env.set_post_processing_options(
        gzip_trace=False,
        package_latest=True,
        print_outputs=False,
        autoplot=DEFAULT_AUTOPLOT,
        autoplot_example="event_latency",
        autoplot_state_field="state_item_count",
        autoplot_skip_no_branch=True,
    )
    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(42)
    env.set_nested_triggering_objects(nested_id="cable_store")
    env.set_nesting_conditions({"on": "store_put", "frequency": 1})
    env.set_outer_stopping_condition(timeout=SIM_DURATION)
    # Inner settings.
    env.set_inner_repetitions(1)
    env.set_inner_stopping_condition(
        relative_time=20.0, triggering_customer_departs=True
    )
    env.process(sender(env, cable))
    env.process(receiver(env, cable))
    env.nested_run()


if __name__ == "__main__":
    main()
