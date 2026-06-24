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
`simpy.Resource` with `nestedsimpy.NestedResource`. We also add a few commands
that configure the execution of the nested simulation (e.g., what the triggering
points are, or how long to run the nested simulation before stopping).

```{tip}
Download: {download}`mm1_plain.py <../simpy_examples/mm1_plain.py>` ·
{download}`mm1_nested.py <../simpy_examples/mm1_nested.py>`
```

## NestedSimPy output

The package offers visualization and data-generation functionalities. When the
nested simulator runs, it stores intermediate outputs under `nested_output/mm1`
(the `out_dir` set in the code above). Once the outer simulation terminates, the
user can create an `OutputManager` from that folder — even in a fresh session —
to visualize and export the data:

```python
from nestedsimpy import OutputManager

om = OutputManager("nested_output/mm1")            # load a completed nested run

om.visualize_outer_static("outer.png")             # static image of the outer simulation
om.visualize_outer_interactive()                   # interactive plot of the outer simulation
om.visualize_inner(trigger_id=0, inner_id=0)       # a single inner simulation at trigger 0
om.visualize_inner(trigger_id=0)                   # all inner simulations at trigger 0

om.export_inner(trigger_id=0, inner_id=0, path="inner.csv")   # one inner sample path
om.export_outer("outer.csv")                                  # the outer sample path
om.export_outer("predictions.csv", inner_aggregate="mean")    # + averaged inner outcomes
```

### Visualization

`OutputManager` plots the run in four ways — the **outer** simulation on its own
(static or interactive), and the **inner** simulations forked at a triggering
event. All four show the **queue length** at the server over time.

#### Outer simulation (static)

`visualize_outer_static` draws the outer sample path — the queue length over the
10 units of simulated time — with a grey dot at every **triggering event** (here,
each customer arrival).

```{figure} _static/mm1-outer-static.svg
:alt: Static outer simulation — queue length over time with a dot at every triggering event
:width: 100%
```

#### Outer simulation (interactive)

`visualize_outer_interactive` shows the same outer path as a clickable plot.
**Click any triggering event** to reveal the three **inner simulations** forked
there; each inner runs for 5 units of time before stopping, after which the outer
simulation resumes.

```{raw} html
<iframe src="_static/mm1-interactive.html" title="Interactive nested M/M/1: click a triggering event to reveal its inner simulations" style="width:100%; height:520px; border:1px solid var(--color-background-border); border-radius:8px;" loading="lazy"></iframe>
```

#### A single inner simulation

`visualize_inner(trigger_id, inner_id)` plots one inner branch. The grey line is
the outer context up to the fork (at time 0 on this axis); the coloured line is
the inner simulation that continues from there.

```{figure} _static/mm1-inner-one.svg
:alt: A single inner simulation forked at a triggering event
:width: 100%
```

#### All inner simulations

`visualize_inner(trigger_id)` overlays the three inner simulations forked at the
same triggering event. They share the outer history but fork into **different
futures**, so their queue lengths diverge after the checkpoint.

```{figure} _static/mm1-inner-all.svg
:alt: All inner simulations forked at one triggering event
:width: 100%
```

### Data

`OutputManager` also exports the run as tables. Three are shown here: one inner
sample path, the outer sample path, and the prediction table that averages each
customer's inner simulations.

#### One inner sample path

`export_inner(trigger_id, inner_id)` returns a single inner simulation as a
sample path — the queue length after each event, with a few rows of outer context
just before the fork (scroll it):

```{raw} html
<!-- mm1-table-inner:begin (auto-generated by docs/_scripts/make_mm1_outputs.py — do not edit by hand) -->
<div class="ns-dataset-scroll">
<table class="ns-dataset-table">
<thead><tr><th>Segment</th><th>Time</th><th>Queue length</th><th>Event</th></tr></thead>
<tbody>
<tr><td>outer_before</td><td>2.91</td><td>4</td><td>arrival</td></tr>
<tr><td>outer_before</td><td>3.44</td><td>4</td><td>service_departure</td></tr>
<tr><td>outer_before</td><td>3.44</td><td>3</td><td>service_start</td></tr>
<tr><td>outer_before</td><td>3.54</td><td>4</td><td>arrival</td></tr>
<tr><td>inner</td><td>3.68</td><td>4</td><td>service_departure</td></tr>
<tr><td>inner</td><td>3.68</td><td>3</td><td>service_start</td></tr>
<tr><td>inner</td><td>3.75</td><td>3</td><td>service_departure</td></tr>
<tr><td>inner</td><td>3.75</td><td>2</td><td>service_start</td></tr>
<tr><td>inner</td><td>3.79</td><td>3</td><td>arrival</td></tr>
<tr><td>inner</td><td>3.90</td><td>4</td><td>arrival</td></tr>
<tr><td>inner</td><td>4.06</td><td>4</td><td>service_departure</td></tr>
<tr><td>inner</td><td>4.06</td><td>3</td><td>service_start</td></tr>
<tr><td>inner</td><td>4.12</td><td>3</td><td>service_departure</td></tr>
<tr><td>inner</td><td>4.12</td><td>2</td><td>service_start</td></tr>
<tr><td>inner</td><td>4.15</td><td>2</td><td>service_departure</td></tr>
<tr><td>inner</td><td>4.15</td><td>1</td><td>service_start</td></tr>
<tr><td>inner</td><td>4.28</td><td>1</td><td>service_departure</td></tr>
<tr><td>inner</td><td>4.28</td><td>0</td><td>service_start</td></tr>
<tr><td>inner</td><td>4.84</td><td>0</td><td>service_departure</td></tr>
<tr><td>inner</td><td>4.91</td><td>1</td><td>arrival</td></tr>
<tr><td>inner</td><td>4.91</td><td>0</td><td>service_start</td></tr>
<tr><td>inner</td><td>4.96</td><td>0</td><td>service_departure</td></tr>
<tr><td>inner</td><td>5.08</td><td>1</td><td>arrival</td></tr>
<tr><td>inner</td><td>5.08</td><td>0</td><td>service_start</td></tr>
<tr><td>inner</td><td>5.11</td><td>1</td><td>arrival</td></tr>
<tr><td>inner</td><td>5.13</td><td>2</td><td>arrival</td></tr>
<tr><td>inner</td><td>5.34</td><td>2</td><td>service_departure</td></tr>
<tr><td>inner</td><td>5.34</td><td>1</td><td>service_start</td></tr>
<tr><td>inner</td><td>5.48</td><td>1</td><td>service_departure</td></tr>
<tr><td>inner</td><td>5.48</td><td>0</td><td>service_start</td></tr>
<tr><td>inner</td><td>5.53</td><td>0</td><td>service_departure</td></tr>
<tr><td>inner</td><td>6.19</td><td>1</td><td>arrival</td></tr>
<tr><td>inner</td><td>6.19</td><td>0</td><td>service_start</td></tr>
<tr><td>inner</td><td>6.25</td><td>1</td><td>arrival</td></tr>
<tr><td>inner</td><td>6.69</td><td>2</td><td>arrival</td></tr>
<tr><td>inner</td><td>7.00</td><td>2</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.00</td><td>1</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.00</td><td>1</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.00</td><td>0</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.02</td><td>0</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.21</td><td>1</td><td>arrival</td></tr>
<tr><td>inner</td><td>7.21</td><td>0</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.25</td><td>1</td><td>arrival</td></tr>
<tr><td>inner</td><td>7.48</td><td>1</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.48</td><td>0</td><td>service_start</td></tr>
<tr><td>inner</td><td>7.57</td><td>1</td><td>arrival</td></tr>
<tr><td>inner</td><td>7.77</td><td>2</td><td>arrival</td></tr>
<tr><td>inner</td><td>7.87</td><td>2</td><td>service_departure</td></tr>
<tr><td>inner</td><td>7.87</td><td>1</td><td>service_start</td></tr>
</tbody>
</table>
</div>
<!-- mm1-table-inner:end -->
```

#### The outer sample path

`export_outer()` returns the outer simulation as a sample path — the queue length
after each arrival and service completion (scroll it):

```{raw} html
<!-- mm1-table-outer:begin (auto-generated by docs/_scripts/make_mm1_outputs.py — do not edit by hand) -->
<div class="ns-dataset-scroll">
<table class="ns-dataset-table">
<thead><tr><th>Time</th><th>Queue length</th><th>Event</th><th>Customer</th></tr></thead>
<tbody>
<tr><td>0.34</td><td>1</td><td>arrival</td><td>0</td></tr>
<tr><td>0.34</td><td>0</td><td>service_start</td><td>0</td></tr>
<tr><td>0.35</td><td>1</td><td>arrival</td><td>1</td></tr>
<tr><td>0.42</td><td>1</td><td>service_departure</td><td>0</td></tr>
<tr><td>0.42</td><td>0</td><td>service_start</td><td>1</td></tr>
<tr><td>0.43</td><td>1</td><td>arrival</td><td>2</td></tr>
<tr><td>0.75</td><td>1</td><td>service_departure</td><td>1</td></tr>
<tr><td>0.75</td><td>0</td><td>service_start</td><td>2</td></tr>
<tr><td>0.81</td><td>1</td><td>arrival</td><td>3</td></tr>
<tr><td>0.84</td><td>2</td><td>arrival</td><td>4</td></tr>
<tr><td>1.02</td><td>3</td><td>arrival</td><td>5</td></tr>
<tr><td>1.03</td><td>4</td><td>arrival</td><td>6</td></tr>
<tr><td>1.11</td><td>5</td><td>arrival</td><td>7</td></tr>
<tr><td>1.31</td><td>5</td><td>service_departure</td><td>2</td></tr>
<tr><td>1.31</td><td>4</td><td>service_start</td><td>3</td></tr>
<tr><td>1.32</td><td>4</td><td>service_departure</td><td>3</td></tr>
<tr><td>1.32</td><td>3</td><td>service_start</td><td>4</td></tr>
<tr><td>1.35</td><td>4</td><td>arrival</td><td>8</td></tr>
<tr><td>1.37</td><td>4</td><td>service_departure</td><td>4</td></tr>
<tr><td>1.37</td><td>3</td><td>service_start</td><td>5</td></tr>
<tr><td>1.57</td><td>3</td><td>service_departure</td><td>5</td></tr>
<tr><td>1.57</td><td>2</td><td>service_start</td><td>6</td></tr>
<tr><td>1.63</td><td>2</td><td>service_departure</td><td>6</td></tr>
<tr><td>1.63</td><td>1</td><td>service_start</td><td>7</td></tr>
<tr><td>1.70</td><td>2</td><td>arrival</td><td>9</td></tr>
<tr><td>1.85</td><td>2</td><td>service_departure</td><td>7</td></tr>
<tr><td>1.85</td><td>1</td><td>service_start</td><td>8</td></tr>
<tr><td>1.86</td><td>1</td><td>service_departure</td><td>8</td></tr>
<tr><td>1.86</td><td>0</td><td>service_start</td><td>9</td></tr>
<tr><td>2.25</td><td>1</td><td>arrival</td><td>10</td></tr>
<tr><td>2.27</td><td>1</td><td>service_departure</td><td>9</td></tr>
<tr><td>2.27</td><td>0</td><td>service_start</td><td>10</td></tr>
<tr><td>2.37</td><td>0</td><td>service_departure</td><td>10</td></tr>
<tr><td>2.65</td><td>1</td><td>arrival</td><td>11</td></tr>
<tr><td>2.65</td><td>0</td><td>service_start</td><td>11</td></tr>
<tr><td>2.71</td><td>1</td><td>arrival</td><td>12</td></tr>
<tr><td>2.84</td><td>2</td><td>arrival</td><td>13</td></tr>
<tr><td>2.88</td><td>3</td><td>arrival</td><td>14</td></tr>
<tr><td>2.91</td><td>4</td><td>arrival</td><td>15</td></tr>
<tr><td>3.44</td><td>4</td><td>service_departure</td><td>11</td></tr>
<tr><td>3.44</td><td>3</td><td>service_start</td><td>12</td></tr>
<tr><td>3.54</td><td>4</td><td>arrival</td><td>16</td></tr>
<tr><td>3.67</td><td>4</td><td>service_departure</td><td>12</td></tr>
<tr><td>3.67</td><td>3</td><td>service_start</td><td>13</td></tr>
<tr><td>4.00</td><td>3</td><td>service_departure</td><td>13</td></tr>
<tr><td>4.00</td><td>2</td><td>service_start</td><td>14</td></tr>
<tr><td>4.09</td><td>3</td><td>arrival</td><td>17</td></tr>
<tr><td>4.19</td><td>3</td><td>service_departure</td><td>14</td></tr>
<tr><td>4.19</td><td>2</td><td>service_start</td><td>15</td></tr>
<tr><td>4.31</td><td>2</td><td>service_departure</td><td>15</td></tr>
<tr><td>4.31</td><td>1</td><td>service_start</td><td>16</td></tr>
<tr><td>4.51</td><td>1</td><td>service_departure</td><td>16</td></tr>
<tr><td>4.51</td><td>0</td><td>service_start</td><td>17</td></tr>
<tr><td>4.95</td><td>0</td><td>service_departure</td><td>17</td></tr>
<tr><td>5.29</td><td>1</td><td>arrival</td><td>18</td></tr>
<tr><td>5.29</td><td>0</td><td>service_start</td><td>18</td></tr>
<tr><td>5.61</td><td>1</td><td>arrival</td><td>19</td></tr>
<tr><td>5.79</td><td>1</td><td>service_departure</td><td>18</td></tr>
<tr><td>5.79</td><td>0</td><td>service_start</td><td>19</td></tr>
<tr><td>5.90</td><td>1</td><td>arrival</td><td>20</td></tr>
<tr><td>5.91</td><td>2</td><td>arrival</td><td>21</td></tr>
<tr><td>6.00</td><td>3</td><td>arrival</td><td>22</td></tr>
<tr><td>6.09</td><td>3</td><td>service_departure</td><td>19</td></tr>
<tr><td>6.09</td><td>2</td><td>service_start</td><td>20</td></tr>
<tr><td>6.11</td><td>2</td><td>service_departure</td><td>20</td></tr>
<tr><td>6.11</td><td>1</td><td>service_start</td><td>21</td></tr>
<tr><td>6.12</td><td>2</td><td>arrival</td><td>23</td></tr>
<tr><td>6.15</td><td>3</td><td>arrival</td><td>24</td></tr>
<tr><td>6.18</td><td>3</td><td>service_departure</td><td>21</td></tr>
<tr><td>6.18</td><td>2</td><td>service_start</td><td>22</td></tr>
<tr><td>6.26</td><td>3</td><td>arrival</td><td>25</td></tr>
<tr><td>6.41</td><td>4</td><td>arrival</td><td>26</td></tr>
<tr><td>6.43</td><td>4</td><td>service_departure</td><td>22</td></tr>
<tr><td>6.43</td><td>3</td><td>service_start</td><td>23</td></tr>
<tr><td>6.49</td><td>3</td><td>service_departure</td><td>23</td></tr>
<tr><td>6.49</td><td>2</td><td>service_start</td><td>24</td></tr>
<tr><td>6.56</td><td>3</td><td>arrival</td><td>27</td></tr>
<tr><td>6.57</td><td>3</td><td>service_departure</td><td>24</td></tr>
<tr><td>6.57</td><td>2</td><td>service_start</td><td>25</td></tr>
<tr><td>6.83</td><td>2</td><td>service_departure</td><td>25</td></tr>
<tr><td>6.83</td><td>1</td><td>service_start</td><td>26</td></tr>
<tr><td>7.06</td><td>1</td><td>service_departure</td><td>26</td></tr>
<tr><td>7.06</td><td>0</td><td>service_start</td><td>27</td></tr>
<tr><td>7.11</td><td>0</td><td>service_departure</td><td>27</td></tr>
<tr><td>7.48</td><td>1</td><td>arrival</td><td>28</td></tr>
<tr><td>7.48</td><td>0</td><td>service_start</td><td>28</td></tr>
<tr><td>7.53</td><td>0</td><td>service_departure</td><td>28</td></tr>
<tr><td>7.92</td><td>1</td><td>arrival</td><td>29</td></tr>
<tr><td>7.92</td><td>0</td><td>service_start</td><td>29</td></tr>
<tr><td>8.08</td><td>1</td><td>arrival</td><td>30</td></tr>
<tr><td>8.42</td><td>2</td><td>arrival</td><td>31</td></tr>
<tr><td>8.69</td><td>3</td><td>arrival</td><td>32</td></tr>
<tr><td>9.06</td><td>3</td><td>service_departure</td><td>29</td></tr>
<tr><td>9.06</td><td>2</td><td>service_start</td><td>30</td></tr>
<tr><td>9.08</td><td>3</td><td>arrival</td><td>33</td></tr>
<tr><td>9.52</td><td>3</td><td>service_departure</td><td>30</td></tr>
<tr><td>9.52</td><td>2</td><td>service_start</td><td>31</td></tr>
<tr><td>9.57</td><td>3</td><td>arrival</td><td>34</td></tr>
<tr><td>9.58</td><td>4</td><td>arrival</td><td>35</td></tr>
<tr><td>9.59</td><td>4</td><td>service_departure</td><td>31</td></tr>
<tr><td>9.59</td><td>3</td><td>service_start</td><td>32</td></tr>
<tr><td>9.66</td><td>3</td><td>service_departure</td><td>32</td></tr>
<tr><td>9.66</td><td>2</td><td>service_start</td><td>33</td></tr>
<tr><td>9.71</td><td>3</td><td>arrival</td><td>36</td></tr>
<tr><td>9.72</td><td>3</td><td>service_departure</td><td>33</td></tr>
<tr><td>9.72</td><td>2</td><td>service_start</td><td>34</td></tr>
</tbody>
</table>
</div>
<!-- mm1-table-outer:end -->
```

#### Prediction table

`export_outer(inner_aggregate="mean")` adds, for each triggering customer, the
**average outcome over its inner simulations** — for example the mean waiting
time, which estimates that customer's expected wait (the optimal benchmark from
the {doc}`overview <index>`):

```{raw} html
<!-- mm1-table-pred:begin (auto-generated by docs/_scripts/make_mm1_outputs.py — do not edit by hand) -->
<div class="ns-dataset-scroll">
<table class="ns-dataset-table">
<thead><tr><th>Customer</th><th>Arrival</th><th># inner sims</th><th>Mean inner wait</th><th>Mean inner service time</th></tr></thead>
<tbody>
<tr><td>0</td><td>0.34</td><td>3</td><td></td><td>0.21</td></tr>
<tr><td>1</td><td>0.35</td><td>3</td><td>0.34</td><td>0.52</td></tr>
<tr><td>2</td><td>0.43</td><td>3</td><td>0.03</td><td>0.35</td></tr>
<tr><td>3</td><td>0.81</td><td>3</td><td>0.27</td><td>0.65</td></tr>
<tr><td>4</td><td>0.84</td><td>3</td><td>0.53</td><td>0.79</td></tr>
<tr><td>5</td><td>1.02</td><td>3</td><td>1.02</td><td>1.16</td></tr>
<tr><td>6</td><td>1.03</td><td>3</td><td>0.55</td><td>0.68</td></tr>
<tr><td>7</td><td>1.11</td><td>3</td><td>1.59</td><td>1.95</td></tr>
<tr><td>8</td><td>1.35</td><td>3</td><td>0.74</td><td>0.97</td></tr>
<tr><td>9</td><td>1.70</td><td>3</td><td>1.16</td><td>1.37</td></tr>
<tr><td>10</td><td>2.25</td><td>3</td><td>0.06</td><td>0.33</td></tr>
<tr><td>11</td><td>2.65</td><td>3</td><td></td><td>0.16</td></tr>
<tr><td>12</td><td>2.71</td><td>3</td><td>0.24</td><td>0.40</td></tr>
<tr><td>13</td><td>2.84</td><td>3</td><td>0.54</td><td>0.74</td></tr>
<tr><td>14</td><td>2.88</td><td>3</td><td>0.86</td><td>1.14</td></tr>
<tr><td>15</td><td>2.91</td><td>3</td><td>1.14</td><td>1.23</td></tr>
<tr><td>16</td><td>3.54</td><td>3</td><td>0.79</td><td>0.95</td></tr>
<tr><td>17</td><td>4.09</td><td>3</td><td>0.62</td><td>1.09</td></tr>
<tr><td>18</td><td>5.29</td><td>3</td><td></td><td>0.23</td></tr>
<tr><td>19</td><td>5.61</td><td>3</td><td>0.30</td><td>0.43</td></tr>
<tr><td>20</td><td>5.90</td><td>3</td><td>0.03</td><td>0.24</td></tr>
<tr><td>21</td><td>5.91</td><td>3</td><td>0.67</td><td>1.01</td></tr>
<tr><td>22</td><td>6.00</td><td>3</td><td>0.74</td><td>1.06</td></tr>
<tr><td>23</td><td>6.12</td><td>3</td><td>0.65</td><td>1.31</td></tr>
<tr><td>24</td><td>6.15</td><td>3</td><td>1.10</td><td>1.17</td></tr>
<tr><td>25</td><td>6.26</td><td>3</td><td>0.45</td><td>0.77</td></tr>
<tr><td>26</td><td>6.41</td><td>3</td><td>1.05</td><td>1.19</td></tr>
<tr><td>27</td><td>6.56</td><td>3</td><td>0.67</td><td>1.00</td></tr>
<tr><td>28</td><td>7.48</td><td>3</td><td></td><td>0.25</td></tr>
<tr><td>29</td><td>7.92</td><td>3</td><td></td><td>0.13</td></tr>
<tr><td>30</td><td>8.08</td><td>3</td><td>0.55</td><td>1.23</td></tr>
<tr><td>31</td><td>8.42</td><td>3</td><td>0.40</td><td>0.55</td></tr>
<tr><td>32</td><td>8.69</td><td>3</td><td>0.32</td><td>0.50</td></tr>
<tr><td>33</td><td>9.08</td><td>3</td><td>0.74</td><td>1.07</td></tr>
<tr><td>34</td><td>9.57</td><td>3</td><td>0.41</td><td>0.78</td></tr>
<tr><td>35</td><td>9.58</td><td>3</td><td>1.52</td><td>1.69</td></tr>
<tr><td>36</td><td>9.71</td><td>3</td><td>0.86</td><td>1.12</td></tr>
</tbody>
</table>
</div>
<!-- mm1-table-pred:end -->
```

## Next

- {doc}`official-parity/index` — the same idea applied to the full set of
  official SimPy examples.
- {doc}`topical-guides/index` — how triggers, stop rules, and outputs work.
