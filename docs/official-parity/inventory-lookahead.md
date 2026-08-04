# Inventory with Lookahead Decisions

## Scenario

A NestedSimPy-specific example (not from the SimPy documentation): a
periodic-review stock faces Poisson demand each period, and after each
demand an order decision is made. The plain version follows an
order-up-to rule; the nested version chooses each order by lookahead.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_inventory_lookahead.ipynb)
— installs NestedSimPy and runs this example in your browser.
```

## Files

- Plain SimPy: [`simpy_examples/inventory_lookahead_plain.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/inventory_lookahead_plain.py)
- NestedSimPy: [`simpy_examples/inventory_lookahead_nested.py`](https://github.com/NestedSimPy/nestedsimpy.github.io/blob/main/simpy_examples/inventory_lookahead_nested.py)

## Code

### Plain SimPy

```{literalinclude} ../../simpy_examples/inventory_lookahead_plain.py
:language: python
:caption: simpy_examples/inventory_lookahead_plain.py
```

### NestedSimPy

```{codeannotate} ../../simpy_examples/inventory_lookahead_plain.py ../../simpy_examples/inventory_lookahead_nested.py
:title: simpy_examples/inventory_lookahead_nested.py
:context: 3
```

## Discussion

The policy function is identical in both files. What changes is the
decision line: the plain version calls `base_policy(state)`, the nested
version writes

```python
order = yield from env.decide(base_policy, state)
```

At every decision, each candidate order quantity is tried in inner
simulations — the candidate once, the order-up-to rule afterwards — and
the quantity with the lowest average cost is executed. `None` in the
candidate list is the order-up-to rule running as its own candidate.
The candidates are declared with
`set_inner_actions(ACTIONS, metric="cost", outer_run_mode="rollout")`;
no triggering configuration is needed (see {doc}`Triggering events
<../topical-guides/branch-triggers>`). One
`env.record("cost", period_cost)` line exposes each period's cost so
branches can be scored, and the run writes a `rollout/` folder with the
four lookahead CSV files (see {doc}`Raw data <../api/raw-data>`).

See {doc}`Choosing actions by lookahead
<../topical-guides/lookahead-actions>` for the full contract.
