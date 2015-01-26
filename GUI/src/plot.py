#!/usr/bin/env python
from __future__ import division, print_function


class Plot(object):
    def __init__(self, app, metric, plots_showing, stats_showing):
        self.app = app
        self.metric = metric
        self.plots_showing = plots_showing
        self.stats_showing = stats_showing

        self.UI_init()
        self.UI_update()

    def data_update(self):
        # prepare data
        self.data = {}
        rangevarnames = set()
        rangevals = set()
        for reportid, callid in self.plots_showing:
            report = self.app.reports[reportid]
            if report["userange"]:
                rangevarnames.add(report["rangevar"])
            elif report["usentrange"]:
                rangevarnames.add("#threads")
            rawdata = self.app.generateplotdata(reportid, callid,
                                                self.metric)
            if not rawdata:
                continue
            rangevals.update(zip(*rawdata)[0])
            linedatas = {
                statname: [(x, self.app.stats_funs[statname](y))
                           for x, y in rawdata
                           if y is not None]
                for statname in self.stats_showing
            }
            if "all" in linedatas:
                linedatas["all"] = [(x, y) for x, ys in linedatas["all"]
                                    for y in ys]
            self.data[reportid, callid] = linedatas
        self.rangevarname = " = ".join(rangevarnames)

        # set up pseudo range for reports without range
        rangevals.discard(None)
        if rangevals:
            rangemin = min(rangevals)
            rangemax = max(rangevals)
        else:
            # TODO: use barplot
            rangemin = 0
            rangemax = 1
        for linedatas in self.data.values():
            for linedata in linedatas.values():
                for i, (x, y) in enumerate(linedata[:]):
                    if x is None:
                        linedata += [(rangemin, y), (rangemax, y)]
                        del linedata[i]
