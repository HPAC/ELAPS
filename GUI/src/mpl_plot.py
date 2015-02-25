#!/usr/bin/env python
"""Matplotlib implementaiton of plots in ELAPS:Viewer."""
from __future__ import division, print_function

from copy import deepcopy

import matplotlib.figure as MPLfig
import matplotlib.lines as MPLlines
import matplotlib.patches as MPLpatches


class MPLPlot(object):

    """Matplotlib plot for the ELAPS:Viewer."""

    def __init__(self):
        """Initialize the plot."""
        self.fig_init()
        self.stat_styles_init()

    def fig_init(self):
        """Initialize the matplotlib figure."""
        self.fig = MPLfig.Figure()

    def stat_styles_init(self):
        """Initialize the plot styles."""
        self.stat_styles = {
            "legend": {},
            "med": {"linestyle": "-"},
            "min": {"linestyle": "--"},
            "max": {"linestyle": ":", "linewidth": 2},
            "avg": {"linestyle": "-."},
            "min-max": {"hatch": "...", "facecolor": (0, 0, 0, 0)},
            "std": {"alpha": .25},
            "all": {"linestyle": "None", "marker": "."},
        }
        self.stats_order = ("med", "min", "max", "avg", "min-max", "std", "all")

    def set_all(self, xlabel, ylabel, data, colors, title):
        """Set teh plot data."""
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.data = []
        self.colors = colors.copy()
        self.title = ylabel if title is None else title
        stats = set()
        rangevals = set()
        for name, linedatas in data:
            linedatas = deepcopy(linedatas)
            # flatten all data
            if "all" in linedatas:
                linedatas["all"] = [(x, y) for x, ys in linedatas["all"]
                                    for y in ys]
            if "std" in linedatas:
                if "avg" in linedatas:
                    stddict = dict(linedatas["std"])
                    linedatas["std"] = [(x, (y - stddict[x], y + stddict[x]))
                                        for x, y in linedatas["avg"]]
                else:
                    del linedatas["std"]
            stats.update(linedatas.keys())
            rangevals.update(sum((zip(*linedata)[0]
                                  for linedata in linedatas.values()), tuple()))
            self.data.append((name, linedatas))

        rangevals.discard(None)
        self.barplot = (not rangevals) and self.data
        if not self.barplot and self.data:
            rangemin = min(rangevals)
            rangemax = max(rangevals)
            # whole range for norange datasets
            for name, linedatas in self.data:
                for linedata in linedatas.values():
                    for i, (x, y) in enumerate(linedata[:]):
                        if x is None:
                            linedata += [(rangemin, y), (rangemax, y)]
                            del linedata[i]

        # stats ordering
        self.stats = [stat for stat in self.stats_order if stat in stats]

    def plot(self, xlabel="", ylabel="", data={}, colors={}, title=None):
        """Plot given data."""
        self.set_all(xlabel, ylabel, data, colors, title)

        axes = self.fig.gca()

        # set up figure
        self.fig.set_facecolor("#ffffff")
        axes.cla()
        axes.set_axis_bgcolor("#f0f0f0")
        axes.set_xlabel(self.xlabel)
        axes.set_ylabel(self.ylabel)
        axes.hold(True)

        if self.barplot:
            self.plot_barplot()
        else:
            self.plot_lineplot()

        # ymin = 0
        limits = axes.axis()
        axes.axis((limits[0], limits[1], 0, limits[3]))

        self.UI_update()

    def plot_lineplot(self):
        """Plot as a lineplot."""
        axes = self.fig.gca()

        # add plots
        for name, linedatas in self.data:
            color = self.colors[name]
            for statname, linedata in linedatas.iteritems():
                x, y = zip(*linedata)
                if statname in ("min-max", "std"):
                    y1, y2 = zip(*y)
                    axes.fill_between(x, y1, y2, color=color,
                                      **self.stat_styles[statname])
                else:
                    axes.plot(x, y, color=color,
                              **self.stat_styles[statname])

        # add legend
        legend = []
        for name, linedatas in self.data:
            color = self.colors[name]
            legend.append((MPLlines.Line2D(
                [], [], color=color, **self.stat_styles["legend"]
            ), name))
        for statname in self.stats:
            if statname == "min-max":
                legend.append((MPLpatches.Patch(
                    edgecolor="#888888",
                    **self.stat_styles[statname]
                ), statname))
            elif statname == "std":
                legend.append((MPLpatches.Patch(
                    color="#888888",
                    **self.stat_styles[statname]
                ), statname))
            else:
                legend.append((MPLlines.Line2D(
                    [], [], color="#888888",
                    **self.stat_styles[statname]
                ), statname))
        if legend:
            axes.legend(*zip(*legend), loc=0, numpoints=3)

    def plot_barplot(self):
        """Plot as a barplot."""
        axes = self.fig.gca()

        width = .8 / len(self.data)

        # add plots
        for i, (name, linedatas) in enumerate(self.data):
            color = self.colors[name]
            statcount = 0
            for statname in self.stats:
                if statname not in linedatas:
                    continue
                val = linedatas[statname][0][1]
                left = statcount + i * width
                if statname in ("med", "min", "max", "avg"):
                    axes.bar(left, val, width, color=color)
                    statcount += 1
                elif statname == "min-max":
                    bottom = val[0]
                    height = val[1] - bottom
                    axes.bar(left, height, width, bottom, color=color)
                    statcount += 1
                elif statname == "std":
                    if "avg" not in self.stats:
                        continue
                    avg = linedatas["avg"][0][1]
                    std = val[1] - avg
                    left = self.stats.index("avg") + (i + .5) * width
                    axes.errorbar(left, avg, std, color="#000000")
                elif statname == "all":
                    linedata = linedatas["all"]
                    x = len(linedata) * [statcount + (i + .5) * width]
                    y = zip(*linedata)[1]
                    axes.plot(x, y, color=color, **self.stat_styles["all"])
                    statcount += 1

        # add legend
        legend = []
        for name, linedatas in self.data:
            color = self.colors[name]
            legend.append((MPLpatches.Patch(color=color), name))
        if legend:
            axes.legend(*zip(*legend), loc=0, numpoints=3)

        # add xlabels
        xlabels = list(self.stats)
        if "std" in self.stats:
            xlabels.remove("std")
            if "avg" in self.stats:
                xlabels[xlabels.index("avg")] = "avg / std"
        axes.set_xticks([i + .4 for i in range(len(xlabels))])
        axes.set_xticklabels(xlabels)

        # xaxis
        limits = axes.axis()
        axes.axis((-.2, len(xlabels), limits[2], limits[3]))

        self.UI_update()
