"""Plain SimPy M/M/1 queue used to contrast with the nested-sim example.

Usage:
    python examples/run_mm1_simpy_plain.py
"""

from __future__ import annotations

import argparse
import random
from typing import Iterator

import simpy


def make_exponential(rate: float) -> float:
    """Sample from an exponential distribution guarding against zero rate."""

    return random.expovariate(rate if rate > 0 else 1e-9)


def customer(
    env: simpy.Environment,
    resource: simpy.Resource,
    service_rate: float,
) -> Iterator[simpy.events.Event]:
    """Basic service process without any instrumentation."""

    with resource.request() as req:
        yield req
        yield env.timeout(make_exponential(service_rate))


def arrival_process(
    env: simpy.Environment,
    resource: simpy.Resource,
    arrival_rate: float,
    service_rate: float,
) -> Iterator[simpy.events.Event]:
    """Infinite-source arrival process for the M/M/1 queue."""

    while True:
        yield env.timeout(make_exponential(arrival_rate))
        env.process(customer(env, resource, service_rate))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the plain M/M/1 baseline."""

    parser = argparse.ArgumentParser(description="Run the plain SimPy M/M/1 baseline.")
    parser.add_argument(
        "--arrival-rate",
        type=float,
        default=3.0,
        help="Exponential arrival rate λ.",
    )
    parser.add_argument(
        "--service-rate",
        type=float,
        default=4.0,
        help="Exponential service rate μ.",
    )
    parser.add_argument(
        "--runtime",
        type=float,
        default=10.0,
        help="Simulation horizon.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1234,
        help="Random seed for the baseline run.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the plain SimPy model up to a fixed horizon."""

    args = parse_args()
    random.seed(args.seed)
    env = simpy.Environment()
    resource = simpy.Resource(env, capacity=1)
    env.process(
        arrival_process(
            env,
            resource,
            arrival_rate=args.arrival_rate,
            service_rate=args.service_rate,
        )
    )
    # Advance the clock without any branching or additional instrumentation.
    env.run(until=args.runtime)
    print(f"Simulation completed at t={env.now:.3f}")
    print("in_service:", len(resource.users))
    print("queue_len:", len(resource.queue))
    print("in_system:", len(resource.users) + len(resource.queue))


if __name__ == "__main__":
    main()
