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

- Plain SimPy: `simpy_examples/gas_station_plain.py`
- NestedSimPy: `simpy_examples/gas_station_nested.py`

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

The plain SimPy model is unchanged except for the nesting setup: the pumps are a `NestedResource` (capacity 2) and the fuel tank a `NestedContainer`, the run is `env.nested_run()`, and branching fires on **every 5th car arrival**, forking **1 inner simulation** that runs for **120 time units, or until the triggering car departs**.

## Run

```bash
python simpy_examples/gas_station_plain.py
python simpy_examples/gas_station_nested.py
```
