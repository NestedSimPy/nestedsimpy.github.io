# Simple example

This page walks through a simple use case of nested simulation. We start with
simulating an **M/M/1 queue** using SimPy code, and then add to it nested
simulation capabilities using NestedSimPy.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_mm1.ipynb)
— installs NestedSimPy and runs this M/M/1 example in your browser. To run it
locally instead, see {doc}`installing NestedSimPy <getting-started>`.
```

## An M/M/1 queue in SimPy

Here is a simple implementation of an M/M/1 queue using SimPy. It runs for 10
units of time.

```{literalinclude} ../simpy_examples/mm1_plain.py
:language: python
:caption: simpy_examples/mm1_plain.py
```

## Nested simulation using NestedSimPy

Here is a modified version that runs the same M/M/1 queue using NestedSimPy.
Highlighted in **green** are new lines of code, in **amber** modified lines, and
the remaining lines are identical to the original code.

```{codeannotate} ../simpy_examples/mm1_plain.py ../simpy_examples/mm1_nested.py
:title: simpy_examples/mm1_nested.py
```

As can be seen in the example above, to use NestedSimPy we reuse SimPy code,
replacing certain SimPy objects with corresponding NestedSimPy objects — for
example, `simpy.Environment` with `nestedsimpy.NestedEnvironment`, or
`simpy.Resource` with `nestedsimpy.NestedResource` (each NestedSimPy object is
given a `nested_id` — here `"srv"` — a unique name that identifies it in the
outputs). We also add a few commands
that configure the execution of the nested simulation (e.g., what the trigger
points are, or how long to run the nested simulation before stopping).

```{tip}
Download: {download}`mm1_plain.py <../simpy_examples/mm1_plain.py>` ·
{download}`mm1_nested.py <../simpy_examples/mm1_nested.py>`
```

## NestedSimPy output

NestedSimPy offers visualization and data-generation functionalities. When the
nested simulator runs, it stores intermediate outputs under `nested_output/mm1`
(configured by the argument `out_dir` in the code above). Once the outer
simulation terminates, the user can create an `OutputManager` object initialized
from that folder — even in a fresh session — to visualize and export the data:

```python
from nestedsimpy import OutputManager

# Load a completed nested simulation run
om = OutputManager("nested_output/mm1")

# Visualization: plot the outer simulation and the inner simulations
om.visualize_outer_static("outer.png")             # display outer simulation
om.visualize_outer_interactive()                   # display outer simulation
om.visualize_inner(trigger_id=0, inner_id=0)       # display a single inner simulation
om.visualize_inner(trigger_id=0)                   # display all inner simulations

# Data export: write the run out as CSV tables
om.export_inner_event_log(trigger_id=0, inner_id=0, path="inner.csv")   # export a single inner simulation
om.export_outer_event_log("outer.csv")                                  # export the outer simulation
om.export_outer_case_table("predictions.csv")   # export the outer simulation and aggregate the output of the inner simulations at every trigger event
```

### Visualization

`OutputManager` plots the run in four ways — the **outer** simulation on its own
(static or interactive), and the **inner** simulations launched at a trigger
event. All four show the **queue length** at the server over time.

#### Outer simulation (static)

`visualize_outer_static` draws the outer sample path — the queue length over the
10 units of simulated time — with a grey dot at every **trigger point** (here,
each customer arrival).

```{figure} _static/mm1-outer-static.svg
:alt: Static outer simulation — queue length over time with a dot at every trigger point
:width: 100%
```

#### Outer simulation (interactive)

`visualize_outer_interactive` shows the same outer path as a clickable plot.
**Click any trigger point** to reveal the three **inner simulations** launched
there; each inner runs for 5 units of time before stopping, after which the outer
simulation resumes.

```{raw} html
<iframe src="_static/mm1-interactive.html" title="Interactive nested M/M/1: click a trigger point to reveal its inner simulations" style="width:100%; height:520px; border:1px solid var(--color-background-border); border-radius:8px;" loading="lazy"></iframe>
```

#### A single inner simulation

`visualize_inner(trigger_id, inner_id)` plots one inner branch. The grey line is
the outer context up to the trigger point (at time 0 on this axis); the coloured line is
the inner simulation that continues from there. Trigger events are numbered in
the order they fire (`trigger_id` 0 is the first). In this run every arrival
triggers, so trigger event 16 below is the one that fired at customer 16's
arrival.

```{figure} _static/mm1-inner-one.svg
:alt: A single inner simulation launched at a trigger event
:width: 100%
```

#### All inner simulations

`visualize_inner(trigger_id)` overlays the three inner simulations launched at the
same trigger event. They share the outer history but branch into **different
futures**, so their queue lengths diverge after the trigger point.

```{figure} _static/mm1-inner-all.svg
:alt: All inner simulations launched at one trigger event
:width: 100%
```

### Data

`OutputManager` also exports the run as tables of two kinds: **event logs** —
one row per simulation event, giving a sample path of the run — and **case
tables** — one row per case (here, per customer), giving its predicted outcomes.

#### Exporting event logs

An event log records the simulation event by event: each row represents one
event (e.g., an arrival, a service start, or a service departure) together with
the timestamp at which it occurred and the system state it produced. The system
state is tracked by NestedSimPy using the individual state of three objects:
resources, containers, and stores. Resources are used by SimPy to maintain
queues, while containers and stores are used for tracking continuous and
discrete quantities such as inventory. We use `nested_id` to uniquely identify
these objects. When generating the event log, a column is added for each of the
resources, containers, and stores to represent the overall system state. For
resources, we report on the number of customers **in queue**, **in service**,
and **in system** (the system represents the total number in queue plus in
service). In the example below the single server `srv` contributes the three
`(srv)` columns. Both the inner and the outer simulations can be exported this
way.

##### One inner sample path

`export_inner_event_log(trigger_id, inner_id)` returns one inner
simulation's event log. **Simulation source** says where each row comes
from — `outer` before the trigger point, `inner` after it — and `(srv)` is
the server's `nested_id` (scroll it):

```{raw} html
<!-- mm1-table-inner:begin (auto-generated by docs/_scripts/make_mm1_outputs.py — do not edit by hand) -->
<p class="ns-dataset-caption"><em>Inner simulation with replication number k&nbsp;=&nbsp;0 at trigger event 16.</em></p>
<div class="ns-dataset-scroll">
<table class="ns-dataset-table">
<thead><tr><th>Simulation source</th><th>Time</th><th>Customer</th><th>(srv) # in queue</th><th>(srv) # in service</th><th>(srv) # in system</th><th>Event</th></tr></thead>
<tbody>
<tr><td>outer</td><td>2.91</td><td>15</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>outer</td><td>3.44</td><td>11</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>outer</td><td>3.44</td><td>12</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>outer</td><td>3.54</td><td>16</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>inner</td><td>3.75</td><td>12</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>inner</td><td>3.75</td><td>13</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>inner</td><td>3.92</td><td>13</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>inner</td><td>3.92</td><td>14</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>inner</td><td>4.32</td><td>17</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>inner</td><td>4.36</td><td>14</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>inner</td><td>4.36</td><td>15</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>inner</td><td>4.37</td><td>18</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>inner</td><td>4.66</td><td>19</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>inner</td><td>4.70</td><td>20</td><td>5</td><td>1</td><td>6</td><td>arrival</td></tr>
<tr><td>inner</td><td>4.82</td><td>21</td><td>6</td><td>1</td><td>7</td><td>arrival</td></tr>
<tr><td>inner</td><td>4.95</td><td>15</td><td>6</td><td>0</td><td>6</td><td>service_departure</td></tr>
<tr><td>inner</td><td>4.95</td><td>16</td><td>5</td><td>1</td><td>6</td><td>service_start</td></tr>
<tr><td>inner</td><td>5.15</td><td>16</td><td>5</td><td>0</td><td>5</td><td>service_departure</td></tr>
<tr><td>inner</td><td>5.15</td><td>17</td><td>4</td><td>1</td><td>5</td><td>service_start</td></tr>
<tr><td>inner</td><td>5.38</td><td>17</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>inner</td><td>5.38</td><td>18</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>inner</td><td>5.96</td><td>22</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>inner</td><td>6.05</td><td>23</td><td>5</td><td>1</td><td>6</td><td>arrival</td></tr>
<tr><td>inner</td><td>6.09</td><td>18</td><td>5</td><td>0</td><td>5</td><td>service_departure</td></tr>
<tr><td>inner</td><td>6.09</td><td>19</td><td>4</td><td>1</td><td>5</td><td>service_start</td></tr>
<tr><td>inner</td><td>6.30</td><td>19</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>inner</td><td>6.30</td><td>20</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>inner</td><td>6.42</td><td>24</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>inner</td><td>6.56</td><td>25</td><td>5</td><td>1</td><td>6</td><td>arrival</td></tr>
<tr><td>inner</td><td>6.60</td><td>26</td><td>6</td><td>1</td><td>7</td><td>arrival</td></tr>
<tr><td>inner</td><td>6.99</td><td>27</td><td>7</td><td>1</td><td>8</td><td>arrival</td></tr>
<tr><td>inner</td><td>7.11</td><td>20</td><td>7</td><td>0</td><td>7</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.11</td><td>21</td><td>6</td><td>1</td><td>7</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.35</td><td>21</td><td>6</td><td>0</td><td>6</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.35</td><td>22</td><td>5</td><td>1</td><td>6</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.55</td><td>28</td><td>6</td><td>1</td><td>7</td><td>arrival</td></tr>
<tr><td>inner</td><td>7.57</td><td>22</td><td>6</td><td>0</td><td>6</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.57</td><td>23</td><td>5</td><td>1</td><td>6</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.62</td><td>23</td><td>5</td><td>0</td><td>5</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.62</td><td>24</td><td>4</td><td>1</td><td>5</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.81</td><td>24</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.81</td><td>25</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.82</td><td>29</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>inner</td><td>7.96</td><td>30</td><td>5</td><td>1</td><td>6</td><td>arrival</td></tr>
<tr><td>inner</td><td>8.03</td><td>25</td><td>5</td><td>0</td><td>5</td><td>service_departure</td></tr>
<tr><td>inner</td><td>8.03</td><td>26</td><td>4</td><td>1</td><td>5</td><td>service_start</td></tr>
</tbody>
</table>
</div>
<!-- mm1-table-inner:end -->
```

##### The outer sample path

Notice that running nested simulation results in a single outer simulation but
many inner simulations. Each inner simulation is associated with a trigger
event, and an inner simulation replication number.

`export_outer_event_log()` returns the event log of the outer simulation — the state of
the server `srv` after each arrival and service completion (scroll it):

```{raw} html
<!-- mm1-table-outer:begin (auto-generated by docs/_scripts/make_mm1_outputs.py — do not edit by hand) -->
<div class="ns-dataset-scroll">
<table class="ns-dataset-table">
<thead><tr><th>Time</th><th>Customer</th><th>(srv) # in queue</th><th>(srv) # in service</th><th>(srv) # in system</th><th>Event</th></tr></thead>
<tbody>
<tr><td>0.34</td><td>0</td><td>1</td><td>0</td><td>1</td><td>arrival</td></tr>
<tr><td>0.34</td><td>0</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>0.35</td><td>1</td><td>1</td><td>1</td><td>2</td><td>arrival</td></tr>
<tr><td>0.42</td><td>0</td><td>1</td><td>0</td><td>1</td><td>service_departure</td></tr>
<tr><td>0.42</td><td>1</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>0.43</td><td>2</td><td>1</td><td>1</td><td>2</td><td>arrival</td></tr>
<tr><td>0.75</td><td>1</td><td>1</td><td>0</td><td>1</td><td>service_departure</td></tr>
<tr><td>0.75</td><td>2</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>0.81</td><td>3</td><td>1</td><td>1</td><td>2</td><td>arrival</td></tr>
<tr><td>0.84</td><td>4</td><td>2</td><td>1</td><td>3</td><td>arrival</td></tr>
<tr><td>1.02</td><td>5</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>1.03</td><td>6</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>1.11</td><td>7</td><td>5</td><td>1</td><td>6</td><td>arrival</td></tr>
<tr><td>1.31</td><td>2</td><td>5</td><td>0</td><td>5</td><td>service_departure</td></tr>
<tr><td>1.31</td><td>3</td><td>4</td><td>1</td><td>5</td><td>service_start</td></tr>
<tr><td>1.32</td><td>3</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>1.32</td><td>4</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>1.35</td><td>8</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>1.37</td><td>4</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>1.37</td><td>5</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>1.57</td><td>5</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>1.57</td><td>6</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>1.63</td><td>6</td><td>2</td><td>0</td><td>2</td><td>service_departure</td></tr>
<tr><td>1.63</td><td>7</td><td>1</td><td>1</td><td>2</td><td>service_start</td></tr>
<tr><td>1.70</td><td>9</td><td>2</td><td>1</td><td>3</td><td>arrival</td></tr>
<tr><td>1.85</td><td>7</td><td>2</td><td>0</td><td>2</td><td>service_departure</td></tr>
<tr><td>1.85</td><td>8</td><td>1</td><td>1</td><td>2</td><td>service_start</td></tr>
<tr><td>1.86</td><td>8</td><td>1</td><td>0</td><td>1</td><td>service_departure</td></tr>
<tr><td>1.86</td><td>9</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>2.25</td><td>10</td><td>1</td><td>1</td><td>2</td><td>arrival</td></tr>
<tr><td>2.27</td><td>9</td><td>1</td><td>0</td><td>1</td><td>service_departure</td></tr>
<tr><td>2.27</td><td>10</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>2.37</td><td>10</td><td>0</td><td>0</td><td>0</td><td>service_departure</td></tr>
<tr><td>2.65</td><td>11</td><td>1</td><td>0</td><td>1</td><td>arrival</td></tr>
<tr><td>2.65</td><td>11</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>2.71</td><td>12</td><td>1</td><td>1</td><td>2</td><td>arrival</td></tr>
<tr><td>2.84</td><td>13</td><td>2</td><td>1</td><td>3</td><td>arrival</td></tr>
<tr><td>2.88</td><td>14</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>2.91</td><td>15</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>3.44</td><td>11</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>3.44</td><td>12</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>3.54</td><td>16</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>3.67</td><td>12</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>3.67</td><td>13</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>4.00</td><td>13</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>4.00</td><td>14</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>4.09</td><td>17</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>4.19</td><td>14</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>4.19</td><td>15</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>4.31</td><td>15</td><td>2</td><td>0</td><td>2</td><td>service_departure</td></tr>
<tr><td>4.31</td><td>16</td><td>1</td><td>1</td><td>2</td><td>service_start</td></tr>
<tr><td>4.51</td><td>16</td><td>1</td><td>0</td><td>1</td><td>service_departure</td></tr>
<tr><td>4.51</td><td>17</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>4.95</td><td>17</td><td>0</td><td>0</td><td>0</td><td>service_departure</td></tr>
<tr><td>5.29</td><td>18</td><td>1</td><td>0</td><td>1</td><td>arrival</td></tr>
<tr><td>5.29</td><td>18</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>5.61</td><td>19</td><td>1</td><td>1</td><td>2</td><td>arrival</td></tr>
<tr><td>5.79</td><td>18</td><td>1</td><td>0</td><td>1</td><td>service_departure</td></tr>
<tr><td>5.79</td><td>19</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>5.90</td><td>20</td><td>1</td><td>1</td><td>2</td><td>arrival</td></tr>
<tr><td>5.91</td><td>21</td><td>2</td><td>1</td><td>3</td><td>arrival</td></tr>
<tr><td>6.00</td><td>22</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>6.09</td><td>19</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>6.09</td><td>20</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>6.11</td><td>20</td><td>2</td><td>0</td><td>2</td><td>service_departure</td></tr>
<tr><td>6.11</td><td>21</td><td>1</td><td>1</td><td>2</td><td>service_start</td></tr>
<tr><td>6.12</td><td>23</td><td>2</td><td>1</td><td>3</td><td>arrival</td></tr>
<tr><td>6.15</td><td>24</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>6.18</td><td>21</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>6.18</td><td>22</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>6.26</td><td>25</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>6.41</td><td>26</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>6.43</td><td>22</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>6.43</td><td>23</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>6.49</td><td>23</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>6.49</td><td>24</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>6.56</td><td>27</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>6.57</td><td>24</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>6.57</td><td>25</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>6.83</td><td>25</td><td>2</td><td>0</td><td>2</td><td>service_departure</td></tr>
<tr><td>6.83</td><td>26</td><td>1</td><td>1</td><td>2</td><td>service_start</td></tr>
<tr><td>7.06</td><td>26</td><td>1</td><td>0</td><td>1</td><td>service_departure</td></tr>
<tr><td>7.06</td><td>27</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>7.11</td><td>27</td><td>0</td><td>0</td><td>0</td><td>service_departure</td></tr>
<tr><td>7.48</td><td>28</td><td>1</td><td>0</td><td>1</td><td>arrival</td></tr>
<tr><td>7.48</td><td>28</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>7.53</td><td>28</td><td>0</td><td>0</td><td>0</td><td>service_departure</td></tr>
<tr><td>7.92</td><td>29</td><td>1</td><td>0</td><td>1</td><td>arrival</td></tr>
<tr><td>7.92</td><td>29</td><td>0</td><td>1</td><td>1</td><td>service_start</td></tr>
<tr><td>8.08</td><td>30</td><td>1</td><td>1</td><td>2</td><td>arrival</td></tr>
<tr><td>8.42</td><td>31</td><td>2</td><td>1</td><td>3</td><td>arrival</td></tr>
<tr><td>8.69</td><td>32</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>9.06</td><td>29</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>9.06</td><td>30</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>9.08</td><td>33</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>9.52</td><td>30</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>9.52</td><td>31</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>9.57</td><td>34</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>9.58</td><td>35</td><td>4</td><td>1</td><td>5</td><td>arrival</td></tr>
<tr><td>9.59</td><td>31</td><td>4</td><td>0</td><td>4</td><td>service_departure</td></tr>
<tr><td>9.59</td><td>32</td><td>3</td><td>1</td><td>4</td><td>service_start</td></tr>
<tr><td>9.66</td><td>32</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>9.66</td><td>33</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
<tr><td>9.71</td><td>36</td><td>3</td><td>1</td><td>4</td><td>arrival</td></tr>
<tr><td>9.72</td><td>33</td><td>3</td><td>0</td><td>3</td><td>service_departure</td></tr>
<tr><td>9.72</td><td>34</td><td>2</td><td>1</td><td>3</td><td>service_start</td></tr>
</tbody>
</table>
</div>
<!-- mm1-table-outer:end -->
```

#### Exporting case tables

A case table has one row per case — here, per customer — rather than one row per
event. `export_outer_case_table()` produces the **prediction table**:
for each triggering customer it reports the system state at the trigger point
— the `(srv)` columns give the number in queue, in service, and in system at
that moment — together with the **average outcome over its inner simulations** —
for example the mean waiting time, which estimates that customer's expected wait
(the optimal benchmark from the {doc}`overview <index>`). A mean inner wait of
`0.00` means the customer never waited: it arrived to an idle server and entered
service immediately at the trigger point, so its waiting time is exactly zero in
every inner simulation. Note that the state columns show the snapshot **at the
trigger event instant**: the arriving triggering customer is counted in the
queue until the same-instant `service_start` on the next log row. So a row with
`(srv) # in queue` 1, `(srv) # in service` 0 and a mean inner wait of `0.00`
means the customer entered service immediately — not that it waited. (The **mean inner service time** column is the service *completion* time measured from arrival — waiting time plus the service duration — so it is nonzero even for customers that never waited.):

```{raw} html
<!-- mm1-table-pred:begin (auto-generated by docs/_scripts/make_mm1_outputs.py — do not edit by hand) -->
<div class="ns-dataset-scroll">
<table class="ns-dataset-table">
<thead><tr><th>Customer</th><th>Arrival</th><th>(srv) # in queue</th><th>(srv) # in service</th><th>(srv) # in system</th><th># inner branches</th><th>Mean inner wait</th><th>Mean inner service time</th></tr></thead>
<tbody>
<tr><td>0</td><td>0.34</td><td>1</td><td>0</td><td>1</td><td>3</td><td>0.00</td><td>0.11</td></tr>
<tr><td>1</td><td>0.35</td><td>1</td><td>1</td><td>2</td><td>3</td><td>0.19</td><td>0.31</td></tr>
<tr><td>2</td><td>0.43</td><td>1</td><td>1</td><td>2</td><td>3</td><td>0.26</td><td>0.54</td></tr>
<tr><td>3</td><td>0.81</td><td>1</td><td>1</td><td>2</td><td>3</td><td>0.15</td><td>0.62</td></tr>
<tr><td>4</td><td>0.84</td><td>2</td><td>1</td><td>3</td><td>3</td><td>0.56</td><td>0.61</td></tr>
<tr><td>5</td><td>1.02</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.56</td><td>0.70</td></tr>
<tr><td>6</td><td>1.03</td><td>4</td><td>1</td><td>5</td><td>3</td><td>1.23</td><td>1.59</td></tr>
<tr><td>7</td><td>1.11</td><td>5</td><td>1</td><td>6</td><td>3</td><td>1.51</td><td>2.60</td></tr>
<tr><td>8</td><td>1.35</td><td>4</td><td>1</td><td>5</td><td>3</td><td>0.95</td><td>1.17</td></tr>
<tr><td>9</td><td>1.70</td><td>2</td><td>1</td><td>3</td><td>3</td><td>0.39</td><td>0.71</td></tr>
<tr><td>10</td><td>2.25</td><td>1</td><td>1</td><td>2</td><td>3</td><td>0.22</td><td>0.35</td></tr>
<tr><td>11</td><td>2.65</td><td>1</td><td>0</td><td>1</td><td>3</td><td>0.00</td><td>0.07</td></tr>
<tr><td>12</td><td>2.71</td><td>1</td><td>1</td><td>2</td><td>3</td><td>0.21</td><td>0.49</td></tr>
<tr><td>13</td><td>2.84</td><td>2</td><td>1</td><td>3</td><td>3</td><td>0.46</td><td>0.87</td></tr>
<tr><td>14</td><td>2.88</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.32</td><td>0.43</td></tr>
<tr><td>15</td><td>2.91</td><td>4</td><td>1</td><td>5</td><td>3</td><td>0.95</td><td>1.07</td></tr>
<tr><td>16</td><td>3.54</td><td>4</td><td>1</td><td>5</td><td>3</td><td>1.00</td><td>1.30</td></tr>
<tr><td>17</td><td>4.09</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.85</td><td>0.92</td></tr>
<tr><td>18</td><td>5.29</td><td>1</td><td>0</td><td>1</td><td>3</td><td>0.00</td><td>0.17</td></tr>
<tr><td>19</td><td>5.61</td><td>1</td><td>1</td><td>2</td><td>3</td><td>0.11</td><td>0.41</td></tr>
<tr><td>20</td><td>5.90</td><td>1</td><td>1</td><td>2</td><td>3</td><td>0.47</td><td>0.67</td></tr>
<tr><td>21</td><td>5.91</td><td>2</td><td>1</td><td>3</td><td>3</td><td>1.03</td><td>1.22</td></tr>
<tr><td>22</td><td>6.00</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.96</td><td>1.27</td></tr>
<tr><td>23</td><td>6.12</td><td>2</td><td>1</td><td>3</td><td>3</td><td>0.67</td><td>0.92</td></tr>
<tr><td>24</td><td>6.15</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.92</td><td>1.48</td></tr>
<tr><td>25</td><td>6.26</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.62</td><td>0.67</td></tr>
<tr><td>26</td><td>6.41</td><td>4</td><td>1</td><td>5</td><td>3</td><td>0.98</td><td>1.19</td></tr>
<tr><td>27</td><td>6.56</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.99</td><td>1.16</td></tr>
<tr><td>28</td><td>7.48</td><td>1</td><td>0</td><td>1</td><td>3</td><td>0.00</td><td>0.21</td></tr>
<tr><td>29</td><td>7.92</td><td>1</td><td>0</td><td>1</td><td>3</td><td>0.00</td><td>0.13</td></tr>
<tr><td>30</td><td>8.08</td><td>1</td><td>1</td><td>2</td><td>3</td><td>0.23</td><td>0.55</td></tr>
<tr><td>31</td><td>8.42</td><td>2</td><td>1</td><td>3</td><td>3</td><td>0.23</td><td>0.59</td></tr>
<tr><td>32</td><td>8.69</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.68</td><td>0.98</td></tr>
<tr><td>33</td><td>9.08</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.71</td><td>0.92</td></tr>
<tr><td>34</td><td>9.57</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.61</td><td>0.77</td></tr>
<tr><td>35</td><td>9.58</td><td>4</td><td>1</td><td>5</td><td>3</td><td>0.97</td><td>1.04</td></tr>
<tr><td>36</td><td>9.71</td><td>3</td><td>1</td><td>4</td><td>3</td><td>0.72</td><td>0.93</td></tr>
</tbody>
</table>
</div>
<!-- mm1-table-pred:end -->
```

```{note}
As the number of inner simulations grows, each row converges to theory: a
customer with n in system has n - 1 customers ahead, so its wait is
Erlang(n - 1, mu) with mean (n - 1)/mu, and its service completion time is
Erlang(n, mu) with mean n/mu (the service rate mu is 4 here). With 400 inner
simulations per trigger, the rows with 5 in system average a 1.00 wait
(theory 1.00) and a 1.24 service time (theory 1.25).
```

#### User-defined metrics

By default, NestedSimPy keeps track of waiting times for service and service
times and reports them using `export_outer_case_table()` — the two
inner-outcome columns above. The user may also define custom functions that
compute performance metrics for each inner simulation run. These are then
automatically aggregated when `export_outer_case_table()` is called. Such a
function should take two arguments: `eventlog` and `inner_sim_context`. The
argument `eventlog` is the event log of the particular inner simulation run —
a list of rows, each a dict with the columns of the table shown under
*Exporting event logs* above — and `inner_sim_context` is a dictionary with
information about the broader inner simulation context (e.g. the ID of the
triggering customer, or when that customer arrived).

Below is an example of a user-defined function that manually computes the
waiting time. Add it anywhere before `env.nested_run()`:

```python
def user_wait(eventlog, inner_sim_context):
    # eventlog: the inner branch's event log (the table above);
    # inner_sim_context: trigger info
    for row in eventlog:
        if (row["simulation_source"] == "inner"
                and row["Customer"] == inner_sim_context["triggering_customer_id"]
                and row["Event"] == "service_start"):
            return row["Time"] - inner_sim_context["anchor_arrival_time"]
    return float("nan")            # not served within the horizon

env.register_metric("user_wait", user_wait)   # register BEFORE nested_run()
env.nested_run()
```

Adding this code gives the prediction table two **new** columns, named
after the registered metric (`user_wait` -> `inner_user_wait_mean` and
`inner_user_wait_std`): the mean and standard deviation of `user_wait` over
each trigger event's three inner simulations. Below they are shown next to
the table's original **Mean inner wait** column — the new mean matches it
exactly, because `user_wait` recomputes the same quantity (first rows
shown):

```{raw} html
<!-- mm1-table-user:begin (auto-generated by docs/_scripts/make_mm1_outputs.py — do not edit by hand) -->
<p class="ns-dataset-caption"><em>Prediction rows for customers 1&ndash;8 (of 37).</em></p>
<div class="ns-dataset-scroll">
<table class="ns-dataset-table">
<thead><tr><th>Customer</th><th>Mean inner wait (existing)</th><th>inner_user_wait_mean (new)</th><th>inner_user_wait_std (new)</th></tr></thead>
<tbody>
<tr><td>1</td><td>0.19</td><td>0.19</td><td>0.04</td></tr>
<tr><td>2</td><td>0.26</td><td>0.26</td><td>0.17</td></tr>
<tr><td>3</td><td>0.15</td><td>0.15</td><td>0.10</td></tr>
<tr><td>4</td><td>0.56</td><td>0.56</td><td>0.23</td></tr>
<tr><td>5</td><td>0.56</td><td>0.56</td><td>0.05</td></tr>
<tr><td>6</td><td>1.23</td><td>1.23</td><td>0.95</td></tr>
<tr><td>7</td><td>1.51</td><td>1.51</td><td>0.27</td></tr>
<tr><td>8</td><td>0.95</td><td>0.95</td><td>0.26</td></tr>
</tbody>
</table>
</div>
<!-- mm1-table-user:end -->
```

Note that the user-defined function may return NaN — as `user_wait` does
for customer 0, which entered service before the inner simulations fork — in
which case that run is ignored by the aggregation. The full list of
`eventlog` columns and `inner_sim_context` keys is in Using NestedSimPy →
Exporting data: {ref}`user-defined-metrics`.

## Next

- {doc}`official-parity/index` — the same idea applied to the full set of
  official SimPy examples.
- {doc}`topical-guides/index` — how triggers, stop rules, and outputs work.
