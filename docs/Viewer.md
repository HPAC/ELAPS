ELAPS Viewer
============

The *Viewer* in `bin/Viewer` is a PyQt4- and matplotlib-based graphical user
interface to view and plot [`Report`](Report.md).s.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [ELAPS Viewer](#elaps-viewer)
  - [Startup](#startup)
  - [Handling Reports](#handling-reports)
  - [Metrics and Statistics](#metrics-and-statistics)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


Startup
-------
On startup, the *Viewer* reads its arguments as list of `Report` files (`.elr`)
that are immediately loaded.  The `--reset` option resets the *Viewer* layout,
which is normally set to the last used state.


Handling Reports
----------------
All loaded `Report`s are displayed in a list on the left.  Here, new reports
can be added, removed, or loaded in the [*PlayMat*](PlayMat.md) (context menu)
and they can be reordered via drag'n'drop.  The columns next to the `Report`
names allow to set the following:
- Wether the report appears in the plot.
- The color in the plot.
- The name in the plot legend.

`Report`s with more than one call can be unfolded to reveal each call's
contribution and plot.

The currently selected `Report`'s `Experiment` is shown beneath the `Report`
list and statistics of its execution can be found in a table (tabbed with the
plot).


Metrics and Statistics
----------------------
Both metrics and statistics are available from the top tool bar:  The plot
always shows one metric at a time and any number of statistics.
