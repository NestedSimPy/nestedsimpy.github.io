# Additional examples

Each example here adapts one of the official SimPy examples to NestedSimPy. The
model and its outer behaviour stay the same — we simply add nested simulation on
top. Every example is shown as a **plain** SimPy baseline and a **nested**
NestedSimPy version.

```{seealso}
**Based on the official SimPy examples.** Every model in this section is
adapted from [SimPy](https://simpy.readthedocs.io/)'s own
[example suite](https://simpy.readthedocs.io/en/latest/examples/index.html).
SimPy is an independent project distributed under the MIT License
(© 2013 Ontje Lünsdorf and Stefan Scherfke); see {doc}`../about` for full
license and attribution details.
```

- **{doc}`Bank Renege <bank-reneging>`** — customers arrive at a bank and wait
  for a counter, abandoning the queue if their patience runs out. Illustrates
  reneging and condition events on a `NestedResource`.
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
```
