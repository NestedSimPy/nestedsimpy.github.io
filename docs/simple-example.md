# Simple example

This page walks through the smallest end-to-end example: a single **M/M/1
queue**, first as a plain SimPy model and then adapted for NestedSimPy, with the
outputs a nested run produces.

```{tip}
**Run it live:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NestedSimPy/nestedsimpy.github.io/blob/main/notebooks/NestedSimPy_mm1.ipynb)
— installs NestedSimPy and runs this M/M/1 example in your browser (available on release).
```

## Plain SimPy vs. NestedSimPy

The plain model is a standard SimPy M/M/1 queue. The NestedSimPy version keeps
the same outer behavior and adds instrumented primitives, a triggering event,
and inner simulations.

### Plain SimPy

```{literalinclude} ../simpy_examples/mm1_plain.py
:language: python
:caption: simpy_examples/mm1_plain.py
```

### NestedSimPy

The same model under NestedSimPy. **New lines are highlighted green and modified
lines amber**, relative to the plain baseline above; long unchanged runs are
folded — click to expand them.

```{codeannotate} ../simpy_examples/mm1_plain.py ../simpy_examples/mm1_nested.py
:title: simpy_examples/mm1_nested.py
:context: 3
```

```{tip}
Download: {download}`mm1_plain.py <../simpy_examples/mm1_plain.py>` ·
{download}`mm1_nested.py <../simpy_examples/mm1_nested.py>`
```

## What a nested run produces

```{figure} _static/mm1-nested-illustration.svg
:alt: Number of customers over time for an M/M/1 queue, showing the outer simulation in black with inner simulations forked at two triggering events.
:width: 100%

A nested run of the M/M/1 queue. The **black** line is the outer simulation
(number of customers over time). At each **triggering event** (dots), the outer
simulation pauses and forks a set of **inner simulations** (light lines) that
each explore a possible future from that state.
```

### The dataset a nested run produces

A nested run records **one row per inner simulation** — the customer it forked
from, when they arrived, when their service started and ended, and how long they
waited. Here is the full table from this 10-time-unit run (scroll it):

```{raw} html
<div class="ns-dataset-scroll">
<table class="ns-dataset-table">
<thead><tr><th>Customer</th><th>Branch</th><th>Arrival</th><th>Service start</th><th>Service end</th><th>Waiting time</th></tr></thead>
<tbody>
<tr><td>0</td><td>1</td><td>1.13</td><td>1.13</td><td>1.60</td><td>0.00</td></tr>
<tr><td>0</td><td>2</td><td>1.13</td><td>1.13</td><td>1.16</td><td>0.00</td></tr>
<tr><td>1</td><td>1</td><td>1.33</td><td>1.33</td><td>1.53</td><td>0.00</td></tr>
<tr><td>1</td><td>2</td><td>1.33</td><td>1.33</td><td>1.37</td><td>0.00</td></tr>
<tr><td>2</td><td>1</td><td>2.13</td><td>2.13</td><td>2.91</td><td>0.00</td></tr>
<tr><td>2</td><td>2</td><td>2.13</td><td>2.13</td><td>2.26</td><td>0.00</td></tr>
<tr><td>3</td><td>1</td><td>2.42</td><td>2.42</td><td>2.52</td><td>0.00</td></tr>
<tr><td>3</td><td>2</td><td>2.42</td><td>2.42</td><td>2.93</td><td>0.00</td></tr>
<tr><td>4</td><td>1</td><td>2.45</td><td>2.79</td><td>3.01</td><td>0.34</td></tr>
<tr><td>4</td><td>2</td><td>2.45</td><td>2.55</td><td>2.58</td><td>0.10</td></tr>
<tr><td>5</td><td>1</td><td>2.54</td><td>2.73</td><td>3.23</td><td>0.18</td></tr>
<tr><td>5</td><td>2</td><td>2.54</td><td>2.90</td><td>3.72</td><td>0.36</td></tr>
<tr><td>6</td><td>1</td><td>2.55</td><td>3.31</td><td>4.07</td><td>0.76</td></tr>
<tr><td>6</td><td>2</td><td>2.55</td><td>3.47</td><td>3.71</td><td>0.92</td></tr>
<tr><td>7</td><td>1</td><td>3.07</td><td>3.61</td><td>3.67</td><td>0.54</td></tr>
<tr><td>7</td><td>2</td><td>3.07</td><td>3.35</td><td>3.41</td><td>0.28</td></tr>
<tr><td>8</td><td>1</td><td>3.39</td><td>3.39</td><td>3.43</td><td>0.00</td></tr>
<tr><td>8</td><td>2</td><td>3.39</td><td>3.39</td><td>3.54</td><td>0.00</td></tr>
<tr><td>9</td><td>1</td><td>3.43</td><td>3.43</td><td>3.94</td><td>0.00</td></tr>
<tr><td>9</td><td>2</td><td>3.43</td><td>3.43</td><td>3.51</td><td>0.00</td></tr>
<tr><td>10</td><td>1</td><td>3.65</td><td>3.81</td><td>4.00</td><td>0.16</td></tr>
<tr><td>10</td><td>2</td><td>3.65</td><td>3.90</td><td>4.32</td><td>0.25</td></tr>
<tr><td>11</td><td>1</td><td>3.67</td><td>3.77</td><td>3.83</td><td>0.10</td></tr>
<tr><td>11</td><td>2</td><td>3.67</td><td>4.22</td><td>4.40</td><td>0.54</td></tr>
<tr><td>12</td><td>1</td><td>3.93</td><td>4.07</td><td>4.59</td><td>0.14</td></tr>
<tr><td>12</td><td>2</td><td>3.93</td><td>4.49</td><td>4.93</td><td>0.56</td></tr>
<tr><td>13</td><td>1</td><td>4.14</td><td>4.63</td><td>4.66</td><td>0.49</td></tr>
<tr><td>13</td><td>2</td><td>4.14</td><td>4.61</td><td>5.04</td><td>0.47</td></tr>
<tr><td>14</td><td>1</td><td>4.45</td><td>4.95</td><td>5.07</td><td>0.51</td></tr>
<tr><td>14</td><td>2</td><td>4.45</td><td>4.92</td><td>5.52</td><td>0.47</td></tr>
<tr><td>15</td><td>1</td><td>4.55</td><td>5.10</td><td>5.12</td><td>0.55</td></tr>
<tr><td>15</td><td>2</td><td>4.55</td><td>4.84</td><td>4.91</td><td>0.28</td></tr>
<tr><td>16</td><td>1</td><td>4.90</td><td>5.98</td><td>5.99</td><td>1.08</td></tr>
<tr><td>16</td><td>2</td><td>4.90</td><td>6.62</td><td>7.93</td><td>1.72</td></tr>
<tr><td>17</td><td>1</td><td>4.99</td><td>5.27</td><td>5.33</td><td>0.28</td></tr>
<tr><td>17</td><td>2</td><td>4.99</td><td>5.40</td><td>5.96</td><td>0.40</td></tr>
<tr><td>18</td><td>1</td><td>5.20</td><td>6.93</td><td>7.09</td><td>1.73</td></tr>
<tr><td>18</td><td>2</td><td>5.20</td><td>5.46</td><td>5.98</td><td>0.26</td></tr>
<tr><td>19</td><td>1</td><td>5.45</td><td>6.34</td><td>6.57</td><td>0.89</td></tr>
<tr><td>19</td><td>2</td><td>5.45</td><td>5.92</td><td>6.49</td><td>0.48</td></tr>
<tr><td>20</td><td>1</td><td>5.45</td><td>5.86</td><td>6.03</td><td>0.41</td></tr>
<tr><td>20</td><td>2</td><td>5.45</td><td>6.60</td><td>6.75</td><td>1.15</td></tr>
<tr><td>21</td><td>1</td><td>5.69</td><td>6.99</td><td>7.33</td><td>1.30</td></tr>
<tr><td>21</td><td>2</td><td>5.69</td><td>6.44</td><td>6.67</td><td>0.75</td></tr>
<tr><td>22</td><td>1</td><td>5.90</td><td>6.01</td><td>6.48</td><td>0.10</td></tr>
<tr><td>22</td><td>2</td><td>5.90</td><td>6.33</td><td>6.51</td><td>0.43</td></tr>
<tr><td>23</td><td>1</td><td>5.96</td><td>6.39</td><td>6.67</td><td>0.42</td></tr>
<tr><td>23</td><td>2</td><td>5.96</td><td>6.69</td><td>6.76</td><td>0.73</td></tr>
<tr><td>24</td><td>1</td><td>6.24</td><td>7.26</td><td>7.28</td><td>1.02</td></tr>
<tr><td>24</td><td>2</td><td>6.24</td><td>6.97</td><td>7.58</td><td>0.74</td></tr>
<tr><td>25</td><td>1</td><td>6.73</td><td>6.94</td><td>6.95</td><td>0.21</td></tr>
<tr><td>25</td><td>2</td><td>6.73</td><td>7.11</td><td>8.02</td><td>0.39</td></tr>
<tr><td>26</td><td>1</td><td>7.78</td><td>7.78</td><td>7.87</td><td>0.00</td></tr>
<tr><td>26</td><td>2</td><td>7.78</td><td>7.78</td><td>8.00</td><td>0.00</td></tr>
<tr><td>27</td><td>1</td><td>7.88</td><td>7.97</td><td>7.98</td><td>0.09</td></tr>
<tr><td>27</td><td>2</td><td>7.88</td><td>8.00</td><td>8.67</td><td>0.11</td></tr>
<tr><td>28</td><td>1</td><td>7.95</td><td>8.28</td><td>8.37</td><td>0.33</td></tr>
<tr><td>28</td><td>2</td><td>7.95</td><td>8.18</td><td>8.40</td><td>0.23</td></tr>
<tr><td>29</td><td>1</td><td>8.00</td><td>9.24</td><td>9.29</td><td>1.23</td></tr>
<tr><td>29</td><td>2</td><td>8.00</td><td>9.29</td><td>10.21</td><td>1.28</td></tr>
<tr><td>30</td><td>1</td><td>9.04</td><td>9.04</td><td>9.17</td><td>0.00</td></tr>
<tr><td>30</td><td>2</td><td>9.04</td><td>9.04</td><td>9.31</td><td>0.00</td></tr>
<tr><td>31</td><td>1</td><td>9.20</td><td>9.20</td><td>10.36</td><td>0.00</td></tr>
<tr><td>31</td><td>2</td><td>9.20</td><td>9.20</td><td>9.57</td><td>0.00</td></tr>
<tr><td>32</td><td>1</td><td>9.34</td><td>9.50</td><td>9.71</td><td>0.16</td></tr>
<tr><td>32</td><td>2</td><td>9.34</td><td>9.57</td><td>9.81</td><td>0.23</td></tr>
<tr><td>33</td><td>1</td><td>9.55</td><td>10.72</td><td>11.06</td><td>1.16</td></tr>
<tr><td>33</td><td>2</td><td>9.55</td><td>9.90</td><td>10.03</td><td>0.34</td></tr>
</tbody>
</table>
</div>
```

Look at any single customer's two branches: they share an arrival time but fork
into **different futures**, so their service-end and waiting times differ (e.g.
customer 4 waits 0.34 vs. 0.10; even customer 0, who never waits, finishes
service at 1.60 vs. 1.16). Averaging a customer's inner waiting times estimates
their **expected wait** — the optimal benchmark described in the overview.

## Next

- {doc}`official-parity/index` — the same idea applied to the full set of
  official SimPy examples.
- {doc}`topical-guides/index` — how triggers, stop rules, and outputs work.
