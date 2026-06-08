# Overview

NestedSimPy is an extension to [SimPy](https://simpy.readthedocs.io/) that
supplements it with **nested simulation** functionalities. The package is not
part of the SimPy project.

```{note}
The project is currently under development.
```

## What is nested simulation?

Nested simulation can be thought of as **simulation within simulation**. The
user implements and executes an *outer* simulation of some system (e.g.,
service, inventory, or transportation) — a normal simulation run that also
defines certain **triggering events** (e.g., a customer arrival). When a
triggering event is invoked, the outer simulation **pauses** and **branches**
out to multiple parallel **inner simulations** that independently resume from
that state until some stopping condition is met. Once all inner simulations
terminate, the outer simulation receives information about how they played out
and **resumes**, potentially using the information the inner simulations
collected.

```{figure} _static/mm1-nested-illustration.svg
:alt: Number of customers over time for an M/M/1 queue, showing the outer simulation in black with inner simulations forked at two triggering events.
:width: 100%

An M/M/1 queue under nested simulation. The **black** line is the outer simulation
(number of customers over time). At each **triggering event** (dots), the outer simulation
pauses and forks a set of **inner simulations** (light lines) that each explore a
possible future from that exact state before the outer simulation continues.
```

## When is it useful?

The two primary motivations for using nested simulation in Operations
Management are:

1. **Creating benchmarks for machine learning (ML) models for operations
   problems.**
   ML models are often used for generating predictions in operations problems
   such as waiting-time prediction. Existing research tells us how different
   methods compare to each other in different contexts, but it is difficult to
   discern whether the best-performing method is optimal or whether better
   methods can be developed. We can use nested simulation to simulate service
   systems and compute the average waiting times, which provides **optimal
   predictions** (when the performance metric is MSE).

2. **Implementation of rollout (lookahead) policies for dynamic optimization.**
   A commonly used policy in dynamic optimization is the rollout, or lookahead,
   policy: at the moment of decision-making we pause, simulate a few
   alternative courses of action, and choose the action whose simulation yields
   the best performance. Nested simulation lets the user quickly implement such
   policies.

```{toctree}
:hidden:
:caption: Contents

self
getting-started
simple-example
official-parity/index
topical-guides/index
api/index
architecture
about
```
