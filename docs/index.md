---
hide-toc: true
---

# Overview

::::{div} ns-hero
:::{div} ns-hero-headline
Simulation within Simulation
:::

NestedSimPy is an extension to [SimPy](https://simpy.readthedocs.io/) that
supplements it with **nested simulation**, **rollout**, and **policy-lookahead**
capabilities. The package is **not** part of the SimPy project.

:::{div} ns-cta-row
```{button-ref} simple-example
:color: primary

See a simple example
```

```{button-ref} getting-started
:color: light
:outline:

Get started
```
:::

:::{div} ns-hero-demo
```{raw} html
:file: _static/hero-branching-demo.svg
```
:::
::::

```{tip}
**New to SimPy?** NestedSimPy builds directly on SimPy — if you haven't used
SimPy before, start there. The [SimPy documentation](https://simpy.readthedocs.io/)
and its [Getting Started guide](https://simpy.readthedocs.io/en/latest/simpy_intro/index.html)
are the best entry point. Once SimPy feels familiar, this site shows how to add
nested simulation on top.
```

```{note}
The project is currently under development.
```

## What is nested simulation?

Nested simulation can be thought of as *simulation within simulation*. The user
first implements and executes a typical simulation of some system (e.g., service,
inventory, or transportation), which is referred to as the **outer simulation**.
The user also defines **triggering events** (e.g., a customer arrival). When a
triggering event is invoked, the outer simulation **pauses** and **branches** out
to multiple parallel copies of the outer simulation at that moment in time, called
**inner simulations**. These independently continue executing the simulation from
the paused state until a user-defined **inner stopping condition** is met. Once all
inner simulations terminate, the outer simulation receives information about the
inner simulations' execution, at which point it may continue its run, using or
simply recording the inner-simulation realizations. The outer simulation continues
until a user-defined **outer stopping condition** is met.

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

## Explore the docs

````{grid} 1 2 2 3
:gutter: 2

```{grid-item-card} 🧩 Simple example
:link: simple-example
:link-type: doc

An M/M/1 queue, plain SimPy vs. NestedSimPy, side by side.
```

```{grid-item-card} 🚀 NestedSimPy in 10 Minutes
:link: getting-started
:link-type: doc

Install, run the first branching demo, and learn the mental model.
```

```{grid-item-card} 📚 Additional examples
:link: official-parity/index
:link-type: doc

The official SimPy examples, adapted with branching and replay.
```

```{grid-item-card} 🧭 Using NestedSimPy
:link: topical-guides/index
:link-type: doc

Convert code, place triggers, set stop rules, then visualize and export.
```

```{grid-item-card} 🔌 API Reference
:link: api/index
:link-type: doc

The SimPy-facing API surface and reporting helpers.
```

```{grid-item-card} 🏗️ Architecture
:link: architecture
:link-type: doc

How the runtime model works under the hood.
```
````

```{toctree}
:hidden:
:caption: Contents

self
simple-example
getting-started
official-parity/index
topical-guides/index
api/index
architecture
about
```
