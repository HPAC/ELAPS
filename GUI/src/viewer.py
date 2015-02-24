#!/usr/bin/env python
"""API independent base for ELAPS:Viewer."""
from __future__ import division, print_function

import signature
import symbolic
import papi

import sys
import os
import imp
import time
import re
import random
from numbers import Number
from collections import defaultdict
from math import sqrt


class Viewer(object):

    """Base class for ELAPS:Viewer."""

    requiresstatetime = 1423087329
    state = {}

    def __init__(self, loadstate=True):
        """Initialize the Viewer."""
        thispath = os.path.dirname(__file__)
        if thispath not in sys.path:
            sys.path.append(thispath)
        self.rootpath = os.path.abspath(os.path.join(thispath, "..", ".."))
        self.reportpath = os.path.join(self.rootpath, "reports")

        self.metrics_init()
        self.stats_init()
        self.reports_init()
        self.plotdata_init()
        self.UI_init()
        self.state_init(loadstate)
        self.UI_setall()

        # load reports from command line
        for arg in sys.argv[1:]:
            if arg[-4:] == ".emr" and os.path.isfile(arg):
                self.UI_report_load(arg)

    # state access attributes
    def __getattr__(self, name):
        """Catch attribute accesses to state variables."""
        if name in self.__dict__["state"]:
            return self.__dict__["state"][name]
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))

    def __setattr__(self, name, value):
        """Catch attribute accesses to state variables."""
        if name in self.state:
            self.state[name] = value
        else:
            super(Viewer, self).__setattr__(name, value)

    def start(self):
        """Start the Viewer (enter the main loop)."""
        self.UI_start()

    # utility
    @staticmethod
    def log(*args):
        """Log a message to stdout."""
        print(*args)

    @staticmethod
    def alert(*args):
        """Log a message to stderr."""
        print("\033[31m" + " ".join(map(str, args)) + "\033[0m",
              file=sys.stderr)

    # initializers
    def metrics_init(self):
        """Initialize the metrics."""
        self.metrics = {}
        self.metricnames = {}
        metricpath = os.path.join(self.rootpath, "GUI", "src", "metrics")
        for filename in os.listdir(metricpath):
            if not filename[-3:] == ".py":
                continue
            try:
                module = imp.load_source(filename[:-3],
                                         os.path.join(metricpath, filename))
                if hasattr(module, "metric") and hasattr(module, "name"):
                    self.metrics[module.name] = module.metric
                    self.metricnames[module.name] = module.name
                else:
                    self.alert(os.path.relpath(filename),
                               "did not contain a valid metric")
            except:
                self.alert("couldn't load", os.path.relpath(filename))
        self.log("loaded", len(self.metrics), "metrics:",
                 *map(repr, sorted(self.metrics)))
        if len(self.metrics) == 0:
            raise Exception("No metrics found")

    def stats_init(self):
        """Initialize the statistics."""
        self.stats_desc = [
            ("med", "median"),
            ("min", "minimum"),
            ("avg", "average"),
            ("max", "maximum"),
            ("min-max", "range: minimum - maximum"),
            ("std", "standard deviation\n(requies avg to be plotted)"),
            ("all", "all data points"),
        ]
        self.stat_funs = {
            "med": lambda l: sum(sorted(l)[
                ((len(l) - 1) // 2):(len(l) // 2 + 1)
            ]) / (2 - len(l) % 2),
            "min": min,
            "avg": lambda l: sum(l) / len(l),
            "max": max,
            "min-max": lambda l: [min(l), max(l)],
            "std": lambda l: sqrt(sum(x ** 2 for x in l) / len(l)
                                  - (sum(l) / len(l)) ** 2),
            "all": lambda l: l
        }

    def reports_init(self):
        """Initialize the reports list."""
        self.reports = {}
        self.showplots = defaultdict(lambda: defaultdict(lambda: False))
        self.reportid_selected = None
        self.callid_selected = None

    def plotdata_init(self):
        """Initialize the plot data."""
        self.plotdata = []
        self.plots_showing = set()
        self.plotrangevar = ""

    def state_init(self, load=True):
        """Initialize the Viewer state."""
        self.state_reset()

    def state_reset(self):
        """(Re)set the Viewer state to a default state."""
        self.state = {
            "statetime": time.time(),
            "metric_selected": "Gflops/s",
            "stats_showing": set(["med"])
        }

    # papi metrics
    def metrics_addcountermetric(self, name):
        """Add a default metric for a PAPI counter."""
        event = papi.events[name]
        metric = lambda data, report, callid: data.get(name)
        metric.__doc__ = event["long"] + "\n\n    " + name
        self.metrics[name] = metric
        self.metricnames[name] = event["short"]

    # default colors
    def nextcolor(self, colors=[
        "#004280", "#e6a500", "#bf0000", "#009999", "#5b59b2", "#969900",
        "#bf0073", "#bf9239", "#004ee6", "#ff7a00"
    ]):
        """Get a new plot color."""
        if colors:
            return colors.pop(0)
        return "#%06x" % random.randint(0, 0xffffff)

    # report handling
    def report_load(self, filename):
        """Load a report from a file."""
        name = os.path.basename(filename)[:-4]
        errfile = filename + ".err"

        # check for errors
        if os.path.isfile(errfile):
            with open(errfile) as fin:
                lines = fin.readlines()
            if len(lines) == 0:
                self.UI.alerT("report %r is not finished" % name)
            else:
                self.UI_alert("report %r produced errors" % name)
                for line in lines[:10]:
                    self.alert(line.rstrip("\n"))
                if len(lines) > 10:
                    self.alert("[%d more lines]" % (len(lines) - 10))

        fin = open(filename)

        # read header
        evaldir = symbolic.__dict__.copy()
        evaldir.update(signature.__dict__)
        try:
            report = eval(fin.readline(), evaldir)
            report["counters"] = filter(None, report["counters"])
            report["starttime"] = int(fin.readline())
        except:
            raise IOError(filename, "doesn't contain a valid report")
        report["filename"] = os.path.relpath(filename)
        report["valid"] = False
        report["endtime"] = None
        report["name"] = name

        userange_outer = report["userange"]["outer"]
        userange_inner = report["userange"]["inner"]
        samplesperinnerval = len(report["calls"])
        if userange_inner == "omp" or report["options"]["omp"]:
            samplesperinnerval = 1

        rangevals = None,
        if userange_outer:
            rangevals = report["ranges"][userange_outer]
        reportdata = {}
        report["data"] = reportdata
        for rangeval in rangevals:
            innervals = None,
            if userange_inner == "sum":
                sumrange = report["ranges"]["sum"]
                if userange_outer:
                    sumrange = sumrange(**{
                        report["rangevars"][userange_outer]: rangeval
                    })
                innervals = list(sumrange)
            rangevaldata = []
            reportdata[rangeval] = rangevaldata
            for rep in range(report["nrep"] + 1):
                repdata = {}
                if rep > 0:
                    rangevaldata.append(repdata)
                for innerval in innervals:
                    innervaldata = []
                    repdata[innerval] = innervaldata
                    for sample in range(samplesperinnerval):
                        line = fin.readline()
                        if not line:
                            self.alert(filename, "was truncated")
                            return report
                        innervaldata.append(tuple(map(int, line.split())))
        reportdata = {key: tuple(map(tuple, val))
                      for key, val in reportdata.iteritems()}
        try:
            report["endtime"] = int(fin.readline())
        except:
            self.alert(name, "was truncated (missing 1 line)")
            return report
        extralines = fin.readlines()
        if len(extralines):
            self.alert("%r contained %s extra lines:" %
                       (filename, len(extralines)))
            self.alert("".join(extralines[:10]))
            if len(extralines) > 10:
                self.alert("...")
        else:
            report["valid"] = True
        return report

    def report_infostr_HTML(self):
        """Get an info string on a report in HTML format."""
        report = self.reports[self.reportid_selected]
        sampler = report["sampler"]
        result = "<table>"
        result += "<tr><td>File:</td><td>%s</td></tr>" % report["filename"]
        result += "<tr><td>CPU:</td><td>%s</td></tr>" % sampler["cpu_model"]
        if report["userange"]["outer"] == "threads":
            result += (
                "<tr><td>#threads:</td><td>%s</td></tr>"
                % report["ranges"]["threads"]
            )
        else:
            result += "<tr><td>#threads:</td><td>%d</td></tr>" % report["nt"]
        result += "<tr><td>BLAS:</td><td>%s</td></tr>" % sampler["blas_name"]
        if report["valid"]:
            date = time.strftime("%c", time.localtime(report["endtime"]))
            result += "<tr><td>Date:</td><td>%s</td></tr>" % date
        else:
            result += "<tr><td></td><td><b>Invalid Report!</b></td></tr>"
        if report["userange"]["outer"] == "range":
            result += (
                "<tr><td>For each:</td><td>%s = %s</td></tr>"
                % (report["rangevars"]["range"], report["ranges"]["range"])
            )
        if report["userange"]["inner"] == "sum":
            result += (
                "<tr><td>Sum over:</td><td>%s = %s</td></tr>"
                % (report["rangevars"]["sum"], report["ranges"]["sum"])
            )
        elif report["userange"]["inner"] == "omp":
            result += (
                "<tr><td>parallel calls:</td><td>%s = %s</td></tr>"
                % (report["rangevars"]["omp"], report["ranges"]["omp"])
            )

        def format_call(call):
            return call[0] + "(" + ", ".join(map(str, call[1:])) + ")"

        if self.callid_selected is None:
            calls = report["calls"]
        else:
            calls = [report["calls"][self.callid_selected]]
        plural = "s"
        if report["userange"]["inner"] == "omp" or report["options"]["omp"]:
            plural = "s (parallel)"
        result += "<tr><td>Call%s:</td><td>" % (plural if len(calls) > 1
                                                else "")
        result += "<br>".join(map(format_call, calls))
        result += "</td></tr>"
        result += "</table>"
        return result

    def report_infostr(self):
        """Get an info string on a report in plain text format."""
        result = self.report_infostr_HTML()
        result = result.replace("</td><td>", "\t")
        result = result.replace("</tr>", "\n")
        result = re.sub("<.*?>", "", result)
        return result

    # data generation
    def get_metricdata(self, reportid, callid, metricname, rangeval=None):
        """Get metric values for a certain report configuration."""
        report = self.reports[reportid]
        # ifrangeval not given: return all
        userange_outer = report["userange"]["outer"]
        userange_inner = report["userange"]["inner"]
        if userange_outer and rangeval is None:
            plotdata = []
            for rangeval in sorted(report["data"]):
                plotdata.append((rangeval, self.get_metricdata(
                    reportid, callid, metricname, rangeval)))
            plotdata = tuple((x, y) for x, y in plotdata if y is not None)
            if not plotdata:
                return None
            return plotdata

        # extract some variables
        rangevaldata = report["data"][rangeval]
        calls = report["calls"]
        metric = self.metrics[metricname]
        usepapi = report["options"]["papi"]

        # if callid not given: all calls
        callids = callid,
        if callid is None:
            callids = range(len(calls))
        if userange_inner == "omp" or report["options"]["omp"]:
            callids = 0,
        data = defaultdict(lambda: None)

        symdict = {}
        if userange_outer:
            symdict[report["rangevars"][userange_outer]] = rangeval

        # complexity is constant across repetitions
        data["complexity"] = None
        if all(isinstance(calls[callid2], signature.Call)
               for callid2 in callids):
            complexity = 0
            for callid2 in callids:
                call = calls[callid2]
                innervals = None,
                if userange_inner:
                    innerrange = report["ranges"][userange_inner]
                    if userange_outer:
                        innerrange = innerrange(**{
                            report["rangevars"][userange_outer]: rangeval
                        })
                    innervals = list(innerrange)
                for innerval in innervals:
                    if userange_inner:
                        symdict[report["rangevars"][userange_inner]] = \
                            innerval
                    callcomplexity = call.complexity()
                    if isinstance(callcomplexity, symbolic.Expression):
                        complexity += callcomplexity(**symdict)
                    elif isinstance(callcomplexity, Number):
                        complexity += callcomplexity
                    else:
                        complexity = None
                        break
                if complexity is None:
                    break
        data["complexity"] = complexity

        # generate plotdata
        plotdata = []
        for repdata in rangevaldata:
            # set up data
            data["rdtsc"] = 0
            if usepapi:
                for counter in report["counters"]:
                    data[counter] = 0
            for innervaldata in repdata.itervalues():
                data["rdtsc"] += sum(innervaldata[callid][0]
                                     for callid in callids)
                if usepapi:
                    for counterid, counter in enumerate(report["counters"]):
                        data[counter] += sum(
                            innervaldata[callid][counterid + 1]
                            for callid in callids
                        )
            # call metric
            val = metric(data, report, callid)
            if val is not None:
                plotdata.append(val)
        if not plotdata:
            return None
        plotdata = tuple(plotdata)
        if userange_outer:
            return plotdata
        return ((None, plotdata),)

    def plotdata_update(self):
        """Update the data for plotting."""
        self.plotdata = []
        self.plotcolors = {}
        rangevars = set()
        for reportid, callid in sorted(self.plots_showing):
            rawdata = self.get_metricdata(reportid, callid,
                                          self.metric_selected)
            if not rawdata:
                continue
            linedatas = {
                statname: [(x, self.stat_funs[statname](y))
                           for x, y in rawdata
                           if y is not None]
                for statname in self.stats_showing
            }

            report = self.reports[reportid]

            # rangevar
            if report["userange"]["outer"]:
                rangevars.add(report["rangevars"][report["userange"]["outer"]])

            # name
            name = report["name"]
            if callid is not None:
                name += "[%s] (%s)" % (callid, report["calls"][callid][0])

            self.plotdata.append((name, linedatas))
            self.plotcolors[name] = report["plotcolors"][callid]
        self.plotrangevar = " = ".join(rangevars)

    # user interface
    def UI_setall(self):
        """Set all GUI elements."""
        self.UI_metrics_update()
        self.UI_metric_set()
        self.UI_stats_set()

    # event handlers
    def UI_report_load(self, filename):
        """Event: Load a report."""
        filename = os.path.abspath(filename)
        new = filename not in self.reports
        try:
            report = self.report_load(filename)
        except:
            self.UI_alert("Couldn't load %r." % os.path.relpath(filename))
            return
        reportid = filename
        plotcolors = {}
        if new:
            self.log("Loaded %r." % os.path.relpath(filename))
            plotcolors[None] = self.nextcolor()
        else:
            self.log("Reloaded %r." % os.path.relpath(filename))
            oldreport = self.reports[reportid]
            plotcolors[None] = oldreport["plotcolors"][None]
        if (not report["options"]["omp"] and
                report["userange"]["inner"] != "omp"):
            for callid in range(len(report["calls"])):
                if len(report["calls"]) == 1:
                    plotcolors[0] = plotcolors[None]
                elif new:
                    plotcolors[callid] = self.nextcolor()
                elif callid in oldreport["plotcolors"]:
                    plotcolors[callid] = oldreport["plotcolors"][callid]
                else:
                    plotcolors[callid] = self.nextcolor()
        report["plotcolors"] = plotcolors
        if report["options"]["papi"]:
            for counter in report["counters"]:
                if counter not in self.metrics:
                    self.metrics_addcountermetric(counter)
            self.UI_metriclist_update()
        self.plots_showing.add((reportid, None))
        if not new:
            for callid in range(len(report["calls"]), len(oldreport["calls"])):
                self.plots_showing.discard((reportid, callid))
            if (report["options"]["omp"] or
                    report["userange"]["inner"] == "omp"):
                for callid in range(len(report["calls"])):
                    self.plots_showing.discard((reportid, callid))
        self.reports[reportid] = report
        self.plotdata_update()
        self.UI_report_add(reportid)
        self.UI_plot_update()

    def UI_report_reload(self, reportid):
        """Event: Reload a report."""
        self.UI_report_load(reportid)

    def UI_report_close(self, reportid):
        """Event: Close a report."""
        report = self.reports[reportid]
        for callid in report["plotcolors"]:
            self.plots_showing.discard((reportid, callid))
        del self.reports[reportid]
        self.plotdata_update()
        self.UI_plot_update()
        self.UI_report_remove(reportid)

    def UI_report_select(self, reportid, callid):
        """Event: Report selected."""
        self.reportid_selected = reportid
        self.callid_selected = callid
        if reportid:
            self.UI_reportinfo_update()
        else:
            self.UI_reportinfo_clear()

    def UI_reportcheck_change(self, reportid, callid, state):
        """Event: Changed plotting selection of a report (or call)."""
        if state:
            self.plots_showing.add((reportid, callid))
        else:
            self.plots_showing.discard((reportid, callid))
        self.plotdata_update()
        self.UI_plot_update()

    def UI_reportcolor_change(self, reportid, callid, color):
        """Event: Changed the plotting color for a report (or call)."""
        self.reports[reportid]["plotcolors"][callid] = color
        self.UI_report_update(reportid)
        self.plotdata_update()
        self.UI_plot_update()

    def UI_metric_change(self, metric):
        """Event: Changed the selected metric."""
        self.metric_selected = metric
        self.plotdata_update()
        self.UI_plot_update()

    def UI_stat_change(self, statname, state):
        """Event: Changed which statistics to plot."""
        if state:
            self.stats_showing.add(statname)
        else:
            self.stats_showing.discard(statname)
        if statname == "avg" and not state:
            self.stats_showing.discard("std")
        elif statname == "std" and state:
            self.stats_showing.add("avg")
        self.UI_stats_set()
        self.plotdata_update()
        self.UI_plot_update()

    def UI_export(self, filename):
        """Event: Raw plot data export."""
        # data layout
        data = {}
        rows = set()
        cols = set()
        for name, linedatas in self.plotdata:
            for stat, linedata in linedatas.iteritems():
                for rangeval, val in linedata:
                    data[rangeval, name, stat] = val
                    rows.add(rangeval)
                cols.add((name, stat))
        lines = []

        # header
        reportline = ["#"]
        statline = ["# " + self.plotrangevar]
        for name, stat in sorted(cols):
            if name in reportline:
                reportline.append("")
            else:
                reportline.append(name)
            statline.append(stat)
        lines.append(reportline)
        lines.append(statline)

        # content
        for rangeval in sorted(rows):
            line = [str(rangeval)]
            for name, stat in sorted(cols):
                if (rangeval, name, stat) in data:
                    val = data[rangeval, name, stat]
                    if isinstance(val, list):
                        val = ",".join(map(str, val))
                    else:
                        val = str(val)
                    line.append(val)
                else:
                    line.append("NaN")
            lines.append(line)

        # alignment
        colwidths = [max(map(len, col)) for col in zip(*lines)]
        lines[0][0] = lines[0][0].ljust(colwidths[0])
        lines[1][0] = lines[1][0].ljust(colwidths[0])
        lines = [[v.rjust(w) for v, w in zip(l, colwidths)] for l in lines]

        # write file
        with open(filename, "w") as fout:
            for line in lines:
                print(*line, sep="  ", file=fout)
