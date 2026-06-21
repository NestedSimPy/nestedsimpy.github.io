"""A plain M/M/1 queue in SimPy."""

import random

import simpy

ARRIVAL_RATE = 3.0  # mean arrivals per unit time
SERVICE_RATE = 4.0  # mean services per unit time
SIM_TIME = 10.0
SEED = 42


def customer(env, server):
    """Wait for the server, then hold it for an exponential service time."""
    with server.request() as request:
        yield request
        yield env.timeout(random.expovariate(SERVICE_RATE))


def arrivals(env, server):
    """Generate customers with exponential interarrival times."""
    while True:
        yield env.timeout(random.expovariate(ARRIVAL_RATE))
        env.process(customer(env, server))


random.seed(SEED)
env = simpy.Environment()
server = simpy.Resource(env, capacity=1)
env.process(arrivals(env, server))
env.run(until=SIM_TIME)
