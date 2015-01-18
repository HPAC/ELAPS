#!/usr/bin/env python
from __future__ import division, print_function

from PyQt4 import QtGui
import matplotlib.backends.backend_qt4agg as QtMPL
import matplotlib.figure as MPLfig
import matplotlib.lines as MPLlines
import matplotlib.patches as MPLpatches


class QMPLplot(QtGui.QWidget):
    def __init__(self, app, metric):
        QtGui.QWidget.__init__(self)
        self.metric = metric
        self.app = app

        self.setting = False
        self.fig_init()
        self.plottypes_init()
        self.UI_init()

    def fig_init(self):
        self.fig = MPLfig.Figure()

    def plottypes_init(self):
        def med(data):
            sorteddata = sorted(data)
            datalen = len(sorteddata)
            mid = (datalen - 1) // 2
            if datalen % 2 == 0:
                return sorteddata[mid]
            return (sorteddata[mid] + sorteddata[mid + 1]) / 2
        self.plottypes = {
            "med": med,
            "min": min,
            "max": max,
            "min-max": lambda data: (min(data), max(data)),
            "avg": lambda data: sum(data) / len(data),
            "all": lambda data: data
        }
        self.plottype_styles = {
            "legend": {"linestyle": "-"},
            "med": {"linestyle": "-"},
            "min": {"linestyle": "--"},
            "max": {"linestyle": ":"},
            "avg": {"linestyle": "-."},
            "min-max": {"alpha": .25},
            "all": {"linestyle": "None", "marker": "."},
        }

        self.plottypes_showing = set(["med"])

    def UI_init(self):
        self.setWindowTitle(self.metric)

        # layout
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # canvas
        self.Qcanvas = QtMPL.FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.Qcanvas, 1)

        # toolbar
        toolbar = QtMPL.NavigationToolbar2QT(self.Qcanvas, self)
        layout.addWidget(toolbar)

        # plottypes
        plottypesbox = QtGui.QWidget()
        layout.addWidget(plottypesbox)
        plottypesL = QtGui.QHBoxLayout()
        plottypesbox.setLayout(plottypesL)
        plottypesL.addStretch(1)
        plottypesL.addWidget(QtGui.QLabel("statistics:"))
        self.Qplottypes = {}
        for plottype in ("med", "min", "avg", "max", "min-max", "all"):
            plottype_showing = QtGui.QCheckBox(plottype)
            plottypesL.addWidget(plottype_showing)
            plottype_showing.setChecked(plottype in self.plottypes_showing)
            plottype_showing.stateChanged.connect(self.plottype_changed)
            plottype_showing.plottype = plottype
        plottypesL.addStretch(1)

    def plot_update(self):
        # prepare data
        data = {}
        rangevarnames = set()
        rangevals = set()
        for reportid, report in enumerate(self.app.reports):
            for callid, state in report["plotting"].iteritems():
                if not report["plotting"][callid]:
                    continue
                if report["userange"]:
                    rangevarnames.add(report["rangevar"])
                rawdata = self.app.generateplotdata(reportid, callid,
                                                    self.metric)
                if not rawdata:
                    continue
                rangevals.update(zip(*rawdata)[0])
                linedatas = {
                    plottype: [(x, self.plottypes[plottype](y))
                               for x, y in rawdata
                               if y is not None]
                    for plottype in self.plottypes_showing
                }
                if "all" in linedatas:
                    linedatas["all"] = [(x, y) for x, ys in linedatas["all"]
                                        for y in ys]
                data[reportid, callid] = linedatas
        rangevarname = " = ".join(rangevarnames)

        # set up pseudo range for reports without range
        rangevals.discard(None)
        if rangevals:
            rangemin = min(rangevals)
            rangemax = max(rangevals)
        else:
            # TODO: use barplot
            rangemin = 0
            rangemax = 1
        for linedatas in data.values():
            for linedata in linedatas.values():
                for i, (x, y) in enumerate(linedata[:]):
                    if x is None:
                        linedata += [(rangemin, y), (rangemax, y)]
                        del linedata[i]

        axes = self.fig.gca()

        # set up figure
        self.fig.set_facecolor("#ffffff")
        axes.cla()
        axes.set_axis_bgcolor("#f8f8f8")
        axes.set_xlabel(rangevarname)
        axes.set_ylabel(self.metric)
        axes.hold(True)

        # add plots
        legend = []
        for (reportid, callid), linedatas in data.iteritems():
            color = self.app.reports[reportid]["plotcolors"][callid]
            for plottype, linedata in linedatas.iteritems():
                x, y = zip(*linedata)
                if plottype == "min-max":
                    y1, y2 = zip(*y)
                    axes.fill_between(x, y1, y2, color=color,
                                      **self.plottype_styles[plottype])
                else:
                    axes.plot(x, y, color=color,
                              **self.plottype_styles[plottype])

        # add legend
        for (reportid, callid), linedatas in data.iteritems():
            report = self.app.reports[reportid]
            color = report["plotcolors"][callid]
            legendlabel = report["name"]
            if callid is not None:
                legendlabel += " (%s)" % str(report["calls"][callid][0])
        for plottype in self.plottypes_showing:
            if plottype == "min-max":
                legend.append((MPLpatches.Patch(
                    color="#888888", **self.plottype_styles[plottype]
                ), plottype))
            else:
                legend.append((MPLlines.Line2D(
                    [], [], color="#888888", **self.plottype_styles[plottype]
                ), plottype))

        if legend:
            axes.legend(*zip(*legend), loc=0, numpoints=3)

        limits = axes.axis()
        axes.axis((limits[0], limits[1], 0, limits[3]))
        self.Qcanvas.draw()

    # event handers
    def plottype_changed(self):
        sender = self.app.sender()
        if sender.isChecked():
            self.plottypes_showing.add(sender.plottype)
        else:
            self.plottypes_showing.discard(sender.plottype)
        self.plot_update()
