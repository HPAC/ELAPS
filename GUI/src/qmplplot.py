#!/usr/bin/env python
from __future__ import division, print_function

from PyQt4 import QtGui
import matplotlib.backends.backend_qt4agg as QtMPL
import matplotlib.figure as MPLfig
import matplotlib.lines as MPLlines
import matplotlib.patches as MPLpatches

from plot import Plot


class QMPLplot(Plot, QtGui.QWidget):
    def __init__(self, app, metric, plots_showing, stats_showing):
        QtGui.QWidget.__init__(self)
        self.setting = False
        self.fig_init()
        self.stat_styles_init()
        Plot.__init__(self, app, metric, plots_showing, stats_showing)

    def fig_init(self):
        self.fig = MPLfig.Figure()

    def stat_styles_init(self):
        self.stat_styles = {
            "legend": {},
            "med": {"linestyle": "-"},
            "min": {"linestyle": "--"},
            "max": {"linestyle": ":"},
            "avg": {"linestyle": "-."},
            "min-max": {"alpha": .25},
            "min-max": {"hatch": "...", "facecolor": (0, 0, 0, 0)},
            "std": {"alpha": .25},
            "all": {"linestyle": "None", "marker": "."},
        }

    def UI_init(self):
        self.setWindowTitle(self.app.metricnames[self.metric])

        # layout
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # canvas
        self.Qcanvas = QtMPL.FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.Qcanvas, 1)

        # toolbar
        toolbarL = QtGui.QHBoxLayout()
        layout.addLayout(toolbarL)
        self.Qtoolbar = QtMPL.NavigationToolbar2QT(self.Qcanvas, self)
        toolbarL.addWidget(self.Qtoolbar)

    def UI_update(self):
        self.data_update()
        axes = self.fig.gca()

        # set up figure
        self.fig.set_facecolor("#ffffff")
        axes.cla()
        axes.set_axis_bgcolor("#f0f0f0")
        axes.set_xlabel(self.rangevarname)
        axes.set_ylabel(self.app.metricnames[self.metric])
        axes.hold(True)

        # add plots
        legend = []
        for (reportid, callid), linedatas in self.data.iteritems():
            color = self.app.reports[reportid]["plotcolors"][callid]
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
        for (reportid, callid), linedatas in self.data.iteritems():
            report = self.app.reports[reportid]
            color = report["plotcolors"][callid]
            legendlabel = report["name"]
            if callid is not None:
                legendlabel += " (%s)" % str(report["calls"][callid][0])
            legend.append((MPLlines.Line2D(
                [], [], color=color, **self.stat_styles["legend"]
            ), legendlabel))
        for statname, _ in self.app.stats_desc:
            if statname not in self.stats_showing:
                continue
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

        limits = axes.axis()
        axes.axis((limits[0], limits[1], 0, limits[3]))
        self.Qcanvas.draw()
