"""
Gas Station Refueling example (nested-sim adaptation).

Adapted from the SimPy tutorial: a gas station has limited pumps sharing a
common fuel reservoir. Cars arrive, request a pump, and refuel from that
reservoir. A control process monitors fuel level and calls a tank truck
to refill when it drops below a threshold.
"""

import itertools
import random

from _imports import *

# fmt: off
RANDOM_SEED = 42
STATION_TANK_SIZE = 200    # Size of the gas station tank (liters)
THRESHOLD = 25             # Station tank minimum level (% of full)
CAR_TANK_SIZE = 50         # Size of car fuel tanks (liters)
CAR_TANK_LEVEL = [5, 25]   # Min/max levels of car fuel tanks (liters)
REFUELING_SPEED = 2        # Rate of refuelling car fuel tank (liters / second)
TANK_TRUCK_TIME = 300      # Time it takes tank truck to arrive (seconds)
T_INTER = [30, 300]        # Interval between car arrivals [min, max] (seconds)
SIM_TIME = 1000            # Simulation time (seconds)
# fmt: on

NESTED_OUTPUT_FOLDER = set_nested_output_folder("simpy_examples", "gas_station")


def car(name, env, gas_station, station_tank, cust_id=None):
    """A car arrives at the gas station for refueling.

    It requests one of the gas station's fuel pumps and tries to get the
    desired amount of fuel from it. If the station's fuel tank is depleted,
    the car has to wait for the tank truck to arrive.
    """
    car_tank_level = random.randint(*CAR_TANK_LEVEL)
    user_print(f"{env.now:6.1f} s: {name} arrived at gas station", env=env)
    with gas_station.request(job_id=cust_id) as req:
        yield req
        fuel_required = CAR_TANK_SIZE - car_tank_level
        yield station_tank.get(fuel_required)
        yield env.nested_timeout(
            {"distribution": "deterministic", "value": fuel_required / REFUELING_SPEED},
            label="refuel",
        )
        user_print(
            f"{env.now:6.1f} s: {name} refueled with {fuel_required:.1f}L", env=env
        )


def gas_station_control(env, station_tank):
    """Periodically check the level of the gas station tank and call the tank
    truck if the level falls below a threshold."""
    while True:
        if station_tank.level / station_tank.capacity * 100 < THRESHOLD:
            user_print(f"{env.now:6.1f} s: Calling tank truck", env=env)
            yield env.process(tank_truck(env, station_tank))
        yield env.nested_timeout(
            {"distribution": "deterministic", "value": 10}, label="control_check"
        )


def tank_truck(env, station_tank):
    """Arrives at the gas station after a certain delay and refuels it."""
    yield env.nested_timeout(
        {"distribution": "deterministic", "value": TANK_TRUCK_TIME},
        label="truck_travel",
    )
    amount = station_tank.capacity - station_tank.level
    station_tank.put(amount)
    user_print(
        f"{env.now:6.1f} s: Tank truck arrived and refuelled station "
        f"with {amount:.1f}L",
        env=env,
    )


def car_generator(env, gas_station, station_tank):
    """Generate new cars that arrive at the gas station."""
    for i in itertools.count():
        yield env.nested_timeout(
            {"distribution": "deterministic", "value": random.randint(*T_INTER)},
            label="interarrival",
        )
        env.process(car(f"Car {i}", env, gas_station, station_tank, cust_id=i))


def main():
    """Run the nested-sim gas station example and package the outputs."""

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
        autoplot_example="gas_station",
    )
    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(RANDOM_SEED)
    env.set_triggering_objects(nested_id="gas_station")
    env.set_triggering_conditions({"on": "arrival", "frequency": 5})
    env.set_outer_stopping_condition(timeout=SIM_TIME)
    # Inner settings.
    env.set_inner_repetitions(1)
    env.set_inner_stopping_condition(
        relative_time=120.0, triggering_customer_departs=True
    )

    gas_station = NestedResource(env, capacity=2, nested_id="gas_station")
    station_tank = NestedContainer(
        env,
        STATION_TANK_SIZE,
        init=STATION_TANK_SIZE,
        nested_id="station_tank",
        snapshot=False,
    )

    env.process(gas_station_control(env, station_tank))
    env.process(car_generator(env, gas_station, station_tank))
    env.nested_run()


if __name__ == "__main__":
    main()
