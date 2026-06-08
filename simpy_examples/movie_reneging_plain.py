"""
Movie renege example

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

import random
from typing import Dict, List, NamedTuple, Optional

import simpy

RANDOM_SEED = 42
TICKETS = 50  # Number of tickets per movie
SELLOUT_THRESHOLD = 2  # Fewer tickets than this is a sellout
SIM_TIME = 120  # Simulate until


def moviegoer(env, movie, num_tickets, theater):
    """A moviegoer tries to by a number of tickets (*num_tickets*) for
    a certain *movie* in a *theater*.

    If the movie becomes sold out, she leaves the theater. If she gets
    to the counter, she tries to buy a number of tickets. If not enough
    tickets are left, she argues with the teller and leaves.

    If at most one ticket is left after the moviegoer bought her
    tickets, the *sold out* event for this movie is triggered causing
    all remaining moviegoers to leave.

    """
    with theater.counter.request() as my_turn:
        result = yield my_turn | theater.sold_out[movie]
        if my_turn not in result:
            theater.num_renegers[movie] += 1
            return

        if theater.available[movie] < num_tickets:
            yield env.timeout(0.5)
            return

        theater.available[movie] -= num_tickets
        if theater.available[movie] < SELLOUT_THRESHOLD:
            theater.sold_out[movie].succeed()
            theater.when_sold_out[movie] = env.now
            theater.available[movie] = 0
        yield env.timeout(1)


def customer_arrivals(env, theater):
    """Create new *moviegoers* until the sim time reaches 120."""
    while True:
        yield env.timeout(random.expovariate(1 / 0.5))
        movie = random.choice(theater.movies)
        num_tickets = random.randint(1, 6)
        if theater.available[movie]:
            env.process(moviegoer(env, movie, num_tickets, theater))


class Theater(NamedTuple):
    """Container bundling the shared state for the movie-theater example."""

    counter: simpy.Resource
    movies: List[str]
    available: Dict[str, int]
    sold_out: Dict[str, simpy.Event]
    when_sold_out: Dict[str, Optional[float]]
    num_renegers: Dict[str, int]


def main():
    """Entry point to run the plain movie renege example."""

    print("Movie renege")
    random.seed(RANDOM_SEED)
    env = simpy.Environment()

    movies = ["Python Unchained", "Kill Process", "Pulp Implementation"]
    theater = Theater(
        counter=simpy.Resource(env, capacity=1),
        movies=movies,
        available={movie: TICKETS for movie in movies},
        sold_out={movie: env.event() for movie in movies},
        when_sold_out={movie: None for movie in movies},
        num_renegers={movie: 0 for movie in movies},
    )

    env.process(customer_arrivals(env, theater))
    env.run(until=SIM_TIME)

    for movie in movies:
        if theater.sold_out[movie]:
            sellout_time = theater.when_sold_out[movie]
            num_renegers = theater.num_renegers[movie]
            print(
                f'Movie "{movie}" sold out {sellout_time:.1f} minutes '
                f"after ticket counter opening."
            )
            print(
                f"  Number of people leaving queue when film sold out: {num_renegers}"
            )


if __name__ == "__main__":
    main()
