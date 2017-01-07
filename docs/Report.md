ELAPS Report
============

`Report`s are loaded from report files (extension: `.elr`) through the
`elaps.io` routine `load_report(filename)`.  A `Report` contains a copy of the
executed [`Experiment`](Experiment.md) as well as the resulting measurements.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Measurement results](#measurement-results)
  - [`rawdata`](#rawdata)
  - [`fulldata`](#fulldata)
  - [`data`](#data)
- [Dropping first repetitions](#dropping-first-repetitions)
- [Evaluating a metric for a Report](#evaluating-a-metric-for-a-report)
- [Computing statistics](#computing-statistics)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


Measurement results
-------------------
The Sampling measurements are available in three data structures:
`rawdata`, `fulldata`, and `data`.

### `rawdata`
contains the raw data as produced by the Sampler in the form of a list, each
entry of which corresponds to one line in the Sampler's output.  Each split by
white spaces, where numbers are parsed as such where possible.

###`fulldata`
is a nested data structure that organizes the data according to the
`Experiment`'s setup in the following hierarchy:

    fulldata[range_val][rep][sumrange_val][callid][counter]

- `range_val`: The range value (or `None`).
- `rep`: The repetition number.
- `sumrange_val`: the sum-range value (or `None`).
- `callid`: The call number.
- `counterid`: Number of the PAPI counter (`0` for cycle count).

When `sumrange_parallel` or `calls_parallel` are set, the levels
`sumrange_val` and `callid` are left out accordingly.

###`data`
is a nested data structure containing reduced data according to the `Experiment`
setup in the following hierarchy:

    data[range_val][rep][callid][counter]

- `range_val`: The range value (or `None`).
- `rep`: The repetition number.
- `callid`: The call number or `None` for a sum across all calls.
- `counter`: The PAPI event name, `"cycles"` or `"flops"`.  The latter contains
  the number of floating point operations involved in the operation, provided
  that the `Call`'s `Signature` has its `complexity` attribute set.

If `calls_parallel` is set, the level `callid` is left out.


Dropping first repetitions
--------------------------
The first repetition of an experiment is often an outlier due to, e.g.,  library
or cache initialization.  `discard_first_repetitions()` will discard each first
repetition within a `Report`, resulting in a derived `Report` object.


Evaluating a metric for a Report
--------------------------------
`Report`s can be evaluated with various metrics (such as "Execution time",
"Performance", or "Efficiency").  The method `Report.evaluate()` applies such a
metric and optionally a statistic to a its dataset.

`Report.evaluate()` takes the following arguments:
- `callselector` determines which calls contribute to the evaluation. It can
  take several different values:
  - An `int` identifies a single call (numbered from `0`)
  - A `list` of `int`s considers all calls in that list together
  - A general function that receives as input the values for each call and
    returns the gathered value.  This allows to evaluate linear combinations or
    scalings.
- `metric`: A metric loaded by `elaps.io.load_metric()`.
- `stat` (default: `"all"`):  Apply a statistic to the output (see below).

The result is a `dict` with one entry for each `range_val`.  The entries are the
statistics computed from the metrics applied to the selected calls.


Computing statistics
--------------------
The method `apply_stat(stat, data)` applies a statistics to a `list` or a nested
to each list in a `dict`.  `stat` is either a function that compute the metric
itself or one of the following `string`s identifying a predefined statistic:
- `"min"`: minimum,
- `"med"`: median,
- `"max"`: maximum,
- `"avg"`: average or mean, and
- `"std"`: standard deviation (square root of the variance).
