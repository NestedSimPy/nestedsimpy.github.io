# Gas Station Refueling

## Scenario

Adapted from SimPy's official [Gas Station Refueling example](https://simpy.readthedocs.io/en/latest/examples/gas_station_refuel.html).

Cars arrive at a gas station with a limited number of pumps. Those pumps share a
common fuel reservoir, and a control process summons a tank truck when fuel
falls below a threshold.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_gas_station.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: [`simpy_examples/gas_station_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/gas_station_plain.py)
- NestedSimPy: [`simpy_examples/gas_station_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/gas_station_nested.py)

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/gas_station_plain.py
:language: python
:caption: simpy_examples/gas_station_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/gas_station_plain.py ../../simpy_examples/gas_station_nested.py
:title: simpy_examples/gas_station_nested.py
:context: 3
```

## Discussion

Two objects are converted: the pumps become a `NestedResource` with `nested_id="gas_station"` and the shared fuel reservoir becomes a `NestedContainer` with `nested_id="station_tank"`; branching triggers on every fifth arrival at the pumps. All four delays — refueling, the 10-second control check, the tank-truck travel time, and the car interarrival time — become deterministic `env.nested_timeout` calls, with the random interarrival still drawn by `random.randint` before being wrapped. Each car passes a `job_id` on its pump request, which identifies the customer in the recorded trace. The general conversion steps are in {doc}`From SimPy to NestedSimPy <../topical-guides/branching-model>`.

