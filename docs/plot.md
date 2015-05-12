ELAPS Report plotting
=====================

The matplotlib-based module `elaps.plot` provides the function `plot()` that
plots a series of metric data sets as produced by a [`Report`](Report.md)'s
`apply_metric()` method.  If any of the provided data sets contains a range,
it produces a line-plot, otherwise a bar-plot.


Input
-----

`plot()` takes the following arguments:

### `datas` 
(no default)
The datasets to be plotted as a `list` of two-element `tuples` consisting of the
legend entry and the data set as returned by `Report.apply_metric()`.

### `stat_names`
(default: `["med"]`)
A `list` of statistics to be plotted.  May contain `"min"`, `"med"`, `"max"`,
`"avg"`, `"std"`, and `"all"`. `

"min"` through `"avg"` on their own are plotted as lines (or simple bars); when
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
Keyword arguments (`dict`) for matplotlib's `legend()` method (e.g., for
custom legend placement).

### `figure`
(default: new `pyplot.gcf()`)
The matplotlib `Figure` in which to plot.


Output
------

`plot()` returns a matplotlib `Figure` instance that can be further modified or
exported via its `savefig()` method.
