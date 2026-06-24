"""The same M/M/1 queue under NestedSimPy.

At each arrival the outer simulation pauses and forks three independent inner
simulations that each explore a possible future from that state.
"""

import nestedsimpy

ARRIVAL_RATE = 3.0  # mean arrivals per unit time
SERVICE_RATE = 4.0  # mean services per unit time
SIM_TIME = 10.0
SEED = 42


def customer(env, server):
    """Wait for the server, then hold it for an exponential service time."""
    with server.request() as request:
        yield request
        yield env.nested_timeout({"distribution": "exponential", "lambda": SERVICE_RATE})


def arrivals(env, server):
    """Generate customers with exponential interarrival times."""
    while True:
        yield env.nested_timeout({"distribution": "exponential", "lambda": ARRIVAL_RATE})
        env.process(customer(env, server))


env = nestedsimpy.NestedEnvironment()
server = nestedsimpy.NestedResource(env, capacity=1, nested_id="srv")
env.process(arrivals(env, server))
env.set_output_options(out_dir="nested_output/mm1", gzip_trace=False)
env.set_rng("independent")  # each branch draws its own future
env.set_outer_seed(SEED)
env.set_triggering_objects(nested_id="srv")
env.set_triggering_conditions({"on": "arrival", "frequency": 1})
env.set_inner_repetitions(3)
env.set_inner_stopping_condition(relative_time=5.0)
env.set_outer_stopping_condition(timeout=SIM_TIME)
env.nested_run()
