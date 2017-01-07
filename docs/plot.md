ELAPS Report plotting
=====================

The matplotlib-based module `elaps.plot` provides `plot()` that plots a series
of metric data sets as produced by [`Report.evaluate()`](Report.md).  If any of
the provided data sets contains a range, it produces a line-plot,
otherwise a bar-plot.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Input](#input)
  - [`datas`](#datas)
  - [`stat_names`](#stat_names)
  - [`colors`](#colors)
  - [`styles`](#styles)
  - [`xlabel`](#xlabel)
  - [`ylabel`](#ylabel)
  - [`legendargs`](#legendargs)
  - [`figure`](#figure)
- [Output](#output)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


Input
-----

`plot()` takes the following arguments, all of which but the first are optional.

### `datas`
(required)  
The datasets to be plotted as a `list` of two-element `tuples` consisting of the
legend entry and the data set as returned by `Report.apply_metric()`.

### `stat_names`
(default: `["med"]`)  
A `list` of statistics to be plotted.  May contain `"min"`, `"med"`, `"max"`,
`"avg"`, `"std"`, and `"all"`.

`"min"` through `"avg"` on their own are plotted as lines (or simple bars); when
both `"min"` and `"max"` are present, the range between them (`"min-max"`) is
filled; `"std"` fills the range between of the average +/- one standard
deviation; `"all"` plots all data points as markers.

### `colors`
(default: built-in color set)  
A `list` of colors for the datasets in the same order.

### `styles`
(default: built-in styles)  
A `dict` of style options for different statistics that overwrite the built-in
options.  Relevant: the statistics names, `"min-max"` and `"legend"`.  Allowed
values: keyword arguments (`dict`) for matplotlib's `plot()` method
(`fill_between()` for `"min-max"` and `"std"`).

### `xlabel`
(default: no label)  
The plots x-axis label.  Ignored for bar-plots.

### `ylabel`
(default: no label)  
The plots y-axis label.

### `legendargs`
(default: `{}`)
Keyword arguments (`dict`) for matplotlib's `legend()` method (e.g., for
custom legend placement).

### `figure`
(default: `pyplot.gcf()`)  
The matplotlib `Figure` in which to plot.


Output
------

`plot()` returns a matplotlib `Figure` that can be further modified or exported
via its `savefig()` method.
