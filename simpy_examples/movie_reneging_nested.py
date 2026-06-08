"""
Movie renege example (nested-sim adaptation).

Covers:

- Resources: Resource
- Condition events
- Shared events

Scenario:
  A movie theatre has one ticket counter selling tickets for three
  movies (next show only). When a movie is sold out, all people waiting
  to buy tickets for that movie renege (leave queue).
"""

from __future__ import annotations

import itertools
import random
from typing import Dict, List, NamedTuple, Optional

from _imports import *

# fmt: off
RANDOM_SEED = 42
TICKETS = 50          # Number of tickets per movie (matches plain example)
SELLOUT_THRESHOLD = 2  # Fewer tickets than this is a sellout
SIM_TIME = 40        # Simulate until
# fmt: on

NESTED_OUTPUT_FOLDER = set_nested_output_folder("simpy_examples", "movie_reneging")


def moviegoer(env, cust_id, movie, num_tickets, theater):
    """A moviegoer tries to by a number of tickets (*num_tickets*) for
    a certain *movie* in a *theater*.

    If the movie becomes sold out, she leaves the theater. If she gets
    to the counter, she tries to buy a number of tickets. If not enough
    tickets are left, she argues with the teller and leaves.

    If at most one ticket is left after the moviegoer bought her
    tickets, the *sold out* event for this movie is triggered causing
    all remaining moviegoers to leave.

    """

    with theater.counter.request(job_id=cust_id) as my_turn:
        result = yield my_turn | theater.sold_out[movie]
        if my_turn not in result:
            theater.num_renegers[movie] += 1
            return

        if theater.available[movie] < num_tickets:
            yield env.nested_timeout(
                {"distribution": "deterministic", "value": 0.5},
                label="argue_then_leave",
            )
            return

        theater.available[movie] -= num_tickets
        if theater.available[movie] < SELLOUT_THRESHOLD:
            theater.sold_out[movie].succeed()
            theater.when_sold_out[movie] = env.now
            theater.available[movie] = 0
        yield env.nested_timeout(
            {"distribution": "deterministic", "value": 1.0}, label="purchase"
        )


def customer_arrivals(env, theater):
    """Create new *moviegoers* until the sim time reaches 120."""

    cust_seq = itertools.count()
    while True:
        yield env.nested_timeout(
            {"distribution": "exponential", "lambda": 1 / 0.5}, label="interarrival"
        )
        cust_id = next(cust_seq)
        movie = random.choice(theater.movies)
        num_tickets = random.randint(1, 6)
        if theater.available[movie]:
            env.process(moviegoer(env, cust_id, movie, num_tickets, theater))


class Theater(NamedTuple):
    """Container bundling the shared state for the movie-theater example."""

    counter: NestedResource
    movies: List[str]
    available: Dict[str, int]
    sold_out: Dict[str, simpy.Event]
    when_sold_out: Dict[str, Optional[float]]
    num_renegers: Dict[str, int]


def main():
    """Run the nested-sim movie renege example and package the outputs."""

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
        autoplot_example="movie_reneging",
    )
    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_nested_triggering_objects(nested_id="counter")
    env.set_nesting_conditions({"on": "arrival", "frequency": 1})
    env.set_outer_stopping_condition(timeout=SIM_TIME)
    # Inner settings.
    env.set_inner_repetitions(1)
    env.set_inner_stopping_condition(
        relative_time=10.0, triggering_customer_departs=True
    )

    movies = ["Python Unchained", "Kill Process", "Pulp Implementation"]
    theater = Theater(
        counter=NestedResource(env, capacity=1, nested_id="counter", snapshot=False),
        movies=movies,
        available={movie: TICKETS for movie in movies},
        sold_out={movie: env.event() for movie in movies},
        when_sold_out={movie: None for movie in movies},
        num_renegers={movie: 0 for movie in movies},
    )

    env.process(customer_arrivals(env, theater))
    env.nested_run()


if __name__ == "__main__":
    main()
