# Gas Station Refueling

## Scenario

Cars arrive at a gas station with a limited number of pumps. Those pumps share a
common fuel reservoir, and a control process summons a tank truck when fuel
falls below a threshold.

## Files

- Plain SimPy: `simpy_examples/gas_station_plain.py`
- NestedSimPy: `simpy_examples/gas_station_nested.py`

## Parity Goal

The nested version keeps the outer refueling storyline aligned with the plain
example while exposing additional state around both the pumps and the shared
fuel level.

## What NestedSimPy Adds

- instrumented resource traces for the pumps,
- instrumented inventory/state traces for the fuel reservoir path,
- branch artifacts rooted in meaningful service arrivals.

## Code

This example is one of the heavier parity adaptations, so the source includes
are especially useful here.

```{codediff} ../../simpy_examples/gas_station_plain.py ../../simpy_examples/gas_station_nested.py
:left-title: gas_station_plain.py
:right-title: gas_station_nested.py
:context: 3
```

````{dropdown} Plain SimPy source
```{literalinclude} ../../simpy_examples/gas_station_plain.py
:language: python
:caption: simpy_examples/gas_station_plain.py
```
````

````{dropdown} NestedSimPy source
```{literalinclude} ../../simpy_examples/gas_station_nested.py
:language: python
:caption: simpy_examples/gas_station_nested.py
```
````

## Run

```bash
python simpy_examples/gas_station_plain.py
python simpy_examples/gas_station_nested.py
```
