# Additional examples

The [SimPy documentation](https://simpy.readthedocs.io/en/latest/examples/index.html)
provides multiple examples of discrete-event simulations. We demonstrate how each
of these examples can be modified and executed using nested simulation, and add
two NestedSimPy-specific examples at the end. Every example is shown as a
**plain** SimPy baseline and a **nested** NestedSimPy version.

The SimPy examples are distributed under the MIT License (© 2013 Ontje Lünsdorf
and Stefan Scherfke); see {doc}`../about` for full license and attribution.

- **{doc}`Bank Renege <bank-reneging>`** — models customers arriving at a bank and
  waiting for service at a counter, abandoning the queue if their patience runs
  out. Illustrates defining trigger events on a `NestedResource`.
- **{doc}`Carwash <carwash>`** — cars wait for one of a few washing machines and
  leave once washed. The simplest `NestedResource` queueing example.
- **{doc}`Event Latency <event-latency>`** — messages sent over a channel are
  received after a delay. Illustrates `NestedStore`-based message propagation.
- **{doc}`Gas Station Refueling <gas-station>`** — cars refuel from a shared fuel
  tank that a tanker truck refills. Combines a `NestedResource` with a shared
  `NestedContainer`.
- **{doc}`Machine Shop <machine-shop>`** — machines run and break down, and a
  repairman handles breakdowns with preemptive priority. Illustrates the
  `NestedPreemptiveResource` (preemption and interrupts).
- **{doc}`Movie Renege <movie-reneging>`** — moviegoers queue for tickets and
  leave when a film sells out. Illustrates shared events and sold-out reneging on a `NestedResource`.
- **{doc}`Process Communication <process-communication>`** — producer and
  consumer processes exchange messages through a store. Illustrates asynchronous
  `NestedStore` communication.
- **{doc}`Inventory with Lookahead Decisions <inventory-lookahead>`** — a
  NestedSimPy-specific example (not from the SimPy documentation): a periodic
  stock whose order decision is chosen by trying each candidate quantity in
  inner simulations. Illustrates `env.decide` and `set_inner_actions`.
- **{doc}`Dual Sourcing with Lookahead Expediting <dual-sourcing>`** — a
  NestedSimPy-specific example (not from the SimPy documentation): the
  dual-sourcing inventory model of Song, Xiao, Zhang and Zipkin (2017), where
  lead times are endogenous and each review decides whether to expedite.
  Illustrates tuple actions and redrawable `nested_timeout` delays.

```{toctree}
:hidden:
:maxdepth: 1

bank-reneging
carwash
event-latency
gas-station
machine-shop
movie-reneging
process-communication
inventory-lookahead
dual-sourcing
```
