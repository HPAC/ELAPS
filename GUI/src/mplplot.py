#!/usr/bin/env python
from __future__ import division, print_function

import matplotlib.figure as MPLfig
import matplotlib.lines as MPLlines
import matplotlib.patches as MPLpatches


class MPLPlot(object):
    def __init__(self):
        self.fig_init()
        self.stat_styles_init()

    def fig_init(self):
        self.fig = MPLfig.Figure()

    def stat_styles_init(self):
        self.stat_styles = {
            "legend": {},
            "med": {"linestyle": "-"},
            "min": {"linestyle": "--"},
            "max": {"linestyle": ":"},
            "avg": {"linestyle": "-."},
            "min-max": {"hatch": "...", "facecolor": (0, 0, 0, 0)},
            "std": {"alpha": .25},
            "all": {"linestyle": "None", "marker": "."},
        }
        self.stats_order = ["med", "min", "max", "avg", "min-max", "std", "all"]

    def set_all(self, xlabel, ylabel, data, colors, title):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.data = {}
        self.colors = colors.copy()
        self.title = ylabel if title is None else title
        stats = set()
        rangevals = set()
        for name, linedatas in data.iteritems():
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
            self.data[name] = linedatas

        rangevals.discard(None)
        if not rangevals:
            # TODO: barplot
            rangevals = set([0, 1])
        rangemin = min(rangevals)
        rangemax = max(rangevals)
        # whole range for norange datasets
        for linedatas in self.data.values():
            for linedata in linedatas.values():
                for i, (x, y) in enumerate(linedata[:]):
                    if x is None:
                        linedata += [(rangemin, y), (rangemax, y)]
                        del linedata[i]

        # stats ordering
        self.stats = [stat for stat in self.stats_order if stat in stats]

    def plot(self, xlabel="", ylabel="", data={}, colors={}, title=None):
        self.set_all(xlabel, ylabel, data, colors, title)

        axes = self.fig.gca()

        # set up figure
        self.fig.set_facecolor("#ffffff")
        axes.cla()
        axes.set_axis_bgcolor("#f0f0f0")
        axes.set_xlabel(self.xlabel)
        axes.set_ylabel(self.ylabel)
        axes.hold(True)

        # add plots
        legend = []
        for name, linedatas in self.data.iteritems():
            color = self.colors[name]
            for statname, linedata in linedatas.iteritems():
                x, y = zip(*linedata)
                if statname in ["min-max", "std"]:
                    y1, y2 = zip(*y)
                    axes.fill_between(x, y1, y2, color=color,
                                      **self.stat_styles[statname])
                else:
                    axes.plot(x, y, color=color,
                              **self.stat_styles[statname])

        # add legend
        for name, linedatas in self.data.iteritems():
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

        # ymin = 0
        limits = axes.axis()
        axes.axis((limits[0], limits[1], 0, limits[3]))

        self.UI_update()

    # user interface
    def UI_init(self):
        raise Exception("Plot needs to be subclassed")
