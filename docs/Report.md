ELAPS Report
============

`Report`s are loaded from report files (extension: `.elr`) through the
`elaps.io` routine `load_report(filename)`.  A `Report` contains a copy of the
executed [`Experiment`](Experiment.md) as well as the resulting measurements.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [ELAPS Report](#elaps-report)
  - [Measurement results](#measurement-results)
    - [`rawdata`](#rawdata)
    - [`fulldata`](#fulldata)
    - [`data`](#data)
  - [Dropping first repetitions](#dropping-first-repetitions)
  - [Applying metrics](#applying-metrics)
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
- `sumrange_val`: the sumrange value (or `None`).
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


Applying metrics
----------------
Metrics turn raw measurement data (i.e., cycle counts) into more meaningful
quantities, such as "Execution time in seconds" (`seconds`) or "floating point
operations per cycle" (`ipc`).  A set of predefined metrics can be loaded using
`elaps.io`'s `load_metric(name)`.  Such a metric, which is essentially a python
function, can be applied to an experiment (or a subset of its calls) through
`apply_metric(metric, callid)`.  In addition to valid call numbers, `callid` can
be `None` to access the sum of all calls.

`apply_metric()` returns a data structure with the following hierarchy:

    metric_data[range_val][rep]

- `range_val`: The range value (or `None`).
- `rep`: The repetition number.


Computing statistics
--------------------
The function `apply_stat(stat_name, data)` applies a statistics to a data
structure as returned by a `Report`'s `apply_metric()`.  The following
`stat_name`'s are available:
- `"min"`: Minimum.
- `"med"`: Median
- `"max"`: Maximum.
- `"avg"`: Average or Mean.
- `"std"`: Standard deviation (square root of the variance).
