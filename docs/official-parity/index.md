# Additional examples

The examples section is intentionally centered on the official SimPy examples.

The point of this section is not to show a random collection of demos. The
point is to show that NestedSimPy can sit on top of familiar SimPy models and
preserve their outer behavior while adding branching, traces, and replay.

```{seealso}
**Based on the official SimPy examples.** Every model in this section is
adapted from [SimPy](https://simpy.readthedocs.io/)'s own
[example suite](https://simpy.readthedocs.io/en/latest/examples/index.html).
SimPy is an independent project distributed under the MIT License
(© 2013 Ontje Lünsdorf and Stefan Scherfke). The NestedSimPy adaptations
preserve each example's outer behavior and add branch-aware instrumentation;
see {doc}`../about` for full license and attribution details.
```

## Scope

This section tracks the official SimPy examples that are represented here
through a `plain` baseline and a `nested` NestedSimPy adaptation.

The claim here is narrow and deliberate:

- use the official SimPy examples as the baseline,
- keep the outer behavior aligned,
- add branch-aware instrumentation around that baseline.

## Coverage

This site currently includes parity adaptations for the following official
SimPy examples:

| SimPy example | Plain baseline | NestedSimPy adaptation | Main parity focus |
| --- | --- | --- | --- |
| Bank Renege | `bank_reneging_plain.py` | `bank_reneging_nested.py` | Reneging behavior and condition events |
| Carwash | `carwash_plain.py` | `carwash_nested.py` | Resource queueing and process waiting |
| Event Latency | `event_latency_plain.py` | `event_latency_nested.py` | Store-based message propagation |
| Gas Station Refueling | `gas_station_plain.py` | `gas_station_nested.py` | Resource plus shared container state |
| Machine Shop | `machine_shop_plain.py` | `machine_shop_nested.py` | Interrupts and preemptive repair flow |
| Movie Renege | `movie_reneging_plain.py` | `movie_reneging_nested.py` | Shared events and sold-out reneging |
| Process Communication | `process_communication_plain.py` | `process_communication_nested.py` | Asynchronous Store-based communication |

Parity is enforced by an automated regression suite that compares the outer
printed sequence of each plain example against its NestedSimPy adaptation.

````{grid} 1 1 2 2
:gutter: 2

```{grid-item-card} Queue Reneging
:link: bank-reneging
:link-type: doc

Bank Renege and Movie Renege cover abandonment, sold-out state, and condition
event behavior layered onto instrumented queue resources.
```

```{grid-item-card} Resource Queueing
:link: carwash
:link-type: doc

Carwash is the clearest entry point for understanding how a plain SimPy
resource example becomes branch-aware.
```

```{grid-item-card} Stores and Communication
:link: process-communication
:link-type: doc

Event Latency and Process Communication show how Store-based examples can fork
on message traffic instead of only on queue arrivals.
```

```{grid-item-card} Interrupts and Shared State
:link: machine-shop
:link-type: doc

Machine Shop and Gas Station Refueling show the heavier end of the parity set:
preemption, interrupts, and shared system state.
```
````

## Concept Map

| Theme | Examples |
| --- | --- |
| Resource queues | Carwash, Bank Renege, Movie Renege |
| Stores and message passing | Event Latency, Process Communication |
| Shared inventory/state | Gas Station Refueling |
| Interrupts and preemption | Machine Shop |

## What Changes In The Nested Versions

Across the parity set, the nested scripts add the same kinds of capabilities:

- instrumented resources, stores, or containers,
- branch configuration on meaningful boundary events,
- packaged output folders for traces and manifests,
- post-run inspection and plotting utilities.

What should not change is the intended outer trajectory behavior of the original
example.

## How To Read These Pages

Each example page is organized around four questions:

1. What is the original SimPy scenario?
2. What file pair implements the plain and nested versions?
3. What parity property is being preserved?
4. What branch-aware capabilities are added by NestedSimPy?

```{toctree}
:maxdepth: 1

bank-reneging
carwash
event-latency
gas-station
machine-shop
movie-reneging
process-communication
```
