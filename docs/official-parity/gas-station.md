# Gas Station Refueling

## Scenario

Adapted from SimPy's official [Gas Station Refueling example](https://simpy.readthedocs.io/en/latest/examples/gas_station_refuel.html).

Cars arrive at a gas station with a limited number of pumps. Those pumps share a
common fuel reservoir, and a control process summons a tank truck when fuel
falls below a threshold.

## Files

- Plain SimPy: `simpy_examples/gas_station_plain.py`
- NestedSimPy: `simpy_examples/gas_station_nested.py`

## Code

This example is one of the heavier parity adaptations, so the source includes
are especially useful here.

### Plain SimPy

```{literalinclude} ../../simpy_examples/gas_station_plain.py
:language: python
:caption: simpy_examples/gas_station_plain.py
```

### NestedSimPy

The same model under NestedSimPy. **New lines are highlighted green and modified
lines amber**, relative to the plain baseline above; long unchanged runs are
folded — click to expand them.

```{codeannotate} ../../simpy_examples/gas_station_plain.py ../../simpy_examples/gas_station_nested.py
:title: simpy_examples/gas_station_nested.py
:context: 3
```

## Discussion

Two primitives change together: the pump `simpy.Resource` becomes `NestedResource` and the shared fuel tank `simpy.Container` becomes `NestedContainer`, so inner simulations fork with the full shared-state snapshot. Branching is configured on car arrivals.

## Run

```bash
python simpy_examples/gas_station_plain.py
python simpy_examples/gas_station_nested.py
```
