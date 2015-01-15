#!/usr/bin/env python
from __future__ import division, print_function

import signature
import symbolic

import os
import sys
import time
import re
import imp
import random
from collections import defaultdict

import traceback


class Viewer(object):
    def __init__(self):
        thispath = os.path.dirname(__file__)
        if thispath not in sys.path:
            sys.path.append(thispath)
        self.rootpath = os.path.join(thispath, "..", "..")
        self.reportpath = os.path.join(self.rootpath, "GUI", "reports")

        self.init()
        self.UI_init()
        self.UI_start()

    # utility
    def log(self, *args):
        print(*args)

    def alert(self, *args):
        print(*args, file=sys.stderr)

    def init(self):
        self.reports = []
        self.showplots = defaultdict(lambda: defaultdict(lambda: False))
        self.metrics_init()

    def metrics_init(self):
        self.metrics = {}
        metricpath = os.path.join(self.rootpath, "GUI", "src", "metrics")
        for filename in os.listdir(metricpath):
            if not filename[-3:] == ".py":
                continue
            try:
                module = imp.load_source(filename[:-3],
                                         os.path.join(metricpath, filename))
                if hasattr(module, "metric") and hasattr(module, "name"):
                    self.metrics[module.name] = module.metric
                else:
                    self.alert(os.path.relpath(filename),
                               "did not contain a valid metric")
            except:
                self.alert("couldn't load", os.path.relpath(filename))
        self.log("loaded", len(self.metrics), "metrics:",
                 *map(repr, sorted(self.metrics)))
        if len(self.metrics) == 0:
            raise Exception("No metrics found")
        self.metric_selected = min(self.metrics.keys())
        if "cycles" in self.metrics:
            self.metric_selected = "cycles"

    def metrics_adddefaultmetric(self, name):
        self.metrics[name] = lambda data, sampler: data.get(name)

    def nextcolor(self, colors=[
            "#ff0000", "#00ff00", "#0000ff", "#ffff00", "#00ffff", "#ff00ff",
            "#880000", "#008800", "#000088", "#888800", "#008888", "#880088",
    ]):
        if colors:
            return colors.pop(0)
        "#%06x" % random.randint(0, 0xffffff)

    def report_load(self, filename):
        name = os.path.basename(filename)[:-5]
        errfile = filename + ".err"

        # check for errors
        if os.path.isfile(errfile):
            # TODO: make this a UI_alert
            self.alert("report", name, "produced errors")
            with open(errfile) as fin:
                lines = fin.readlines()
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
            report["starttime"] = int(fin.readline())
        except:
            traceback.print_exc()
            raise IOError(name, "doesn't contain a valid report")
        report["filename"] = os.path.relpath(filename)
        report["valid"] = False
        report["endtime"] = None
        report["name"] = name

        rangevals = [None]
        if report["userange"]:
            rangevals = range(*report["range"])
        reportdata = {}
        report["data"] = reportdata
        for rangeval in rangevals:
            rangevaldata = []
            reportdata[rangeval] = rangevaldata
            for rep in range(report["nrep"] + 1):
                repdata = []
                if rep > 0:
                    rangevaldata.append(repdata)
                for call in report["calls"]:
                    try:
                        line = fin.readline()
                    except:
                        self.alert(filename, "is truncated")
                        return report
                    repdata.append(map(int, line.split()))
        try:
            report["endtime"] = int(fin.readline())
        except:
            self.alert(name, "was truncated")
            return report
        if len(fin.readlines()):
            self.alert(name, "contained extra lines")
        else:
            report["valid"] = True
        return report

    def report_infostr_HTML(self, reportid, callid):
        report = self.reports[reportid]
        sampler = report["sampler"]
        result = "<table>"
        result += "<tr><td>File:</td><td>%s</td></tr>" % report["filename"]
        result += "<tr><td>CPU:</td><td>%s</td></tr>" % sampler["cpu_model"]
        result += "<tr><td>#threads:</td><td>%d</td></tr>" % report["nt"]
        result += "<tr><td>BLAS:</td><td>%s</td></tr>" % sampler["blas_name"]
        if report["valid"]:
            date = time.strftime("%c", time.localtime(report["endtime"]))
            result += "<tr><td>Date:</td><td>%s</td></tr>" % date
        else:
            result += "<tr><td>:</td><td><b>Invalid Report!</b></td></tr>"
        if report["userange"]:
            result += "<tr><td>Range:</td><td>%s = %d:%d:%d</td></tr>" % (
                report["rangevar"],
                report["range"][0],
                report["range"][2],
                report["range"][1] - 1
            )

        def format_call(call):
            return call[0] + "(" + ", ".join(map(str, call[1:])) + ")"

        if callid is None:
            calls = report["calls"]
        else:
            calls = [report["calls"][callid]]
        result += "<tr><td>Call%s:</td><td>" % "s"[:len(calls) - 1]
        result += "<br>".join(map(format_call, calls))
        result += "</td></tr>"
        result += "</table>"
        result += "<br><br>TODO: show some numbers here"
        return result

    def report_infostr(self, reportid, callid):
        result = self.report_infostr_HTML(reportid, callid)
        result = result.replace("</td><td>", "\t")
        result = result.replace("</tr>", "\n")
        result = re.sub("<.*?>", "", result)
        return result

    def generateplotdata(self, reportid, callid, metricname, rangeval=None):
        report = self.reports[reportid]
        # ifrangeval not given: return all
        if report["userange"] and rangeval is None:
            plotdata = []
            rangevals = [None]
            if report["userange"]:
                rangevals = range(*report["range"])
            for rangeval in rangevals:
                plotdata.append((rangeval, self.generateplotdata(
                    reportid, callid, metricname, rangeval)))
            plotdata = [(x, y) for x, y in plotdata if y is not None]
            if not plotdata:
                return None
            return plotdata
        # extract some variables
        rangevaldata = report["data"][rangeval]
        calls = report["calls"]
        metric = self.metrics[metricname]
        # if callid not given: all calls
        callids = [callid]
        if callid is None:
            callids = range(len(calls))
        data = defaultdict(lambda: None)
        # complexity is constant across repetitions
        rangevar = report["rangevar"]
        complexities = [calls[callid2].complexity()
                        if isinstance(calls[callid2], signature.Call) else None
                        for callid2 in callids]
        if all(isinstance(complexity, symbolic.Expression)
               for complexity in complexities):
            data["complexity"] = sum(complexity(**{rangevar: rangeval})
                                     for complexity in complexities)
        # generate plotdata
        plotdata = []
        for rep in range(report["nrep"]):
            repdata = rangevaldata[rep]
            # set up data
            data["rdtsc"] = sum(repdata[callid][0] for callid in callids)
            if report["usepapi"]:
                for counterid, counter in enumerate(report["counters"]):
                    data[counter] = sum(repdata[callid][counterid + 1]
                                        for callid in callids)
            # call metric
            val = metric(data, report)
            if val is not None:
                plotdata.append(val)
        if not plotdata:
            return None
        if report["userange"]:
            return plotdata
        return [(None, plotdata)]

    # event handlers
    def UI_load_report(self, filename):
        try:
            report = self.report_load(filename)
        except:
            traceback.print_exc()
            self.alert("could not load", os.path.relpath(filename))
            return
        reportid = len(self.reports)
        self.reports.append(report)
        report["plotting"] = {None: True}
        report["plotcolors"] = {None: self.nextcolor()}
        for callid in range(len(report["calls"])):
            report["plotting"][callid] = False
            if len(report["calls"]) == 1:
                report["plotcolors"][0] = report["plotcolors"][None]
            else:
                report["plotcolors"][callid] = self.nextcolor()
        if report["usepapi"]:
            for counter in report["counters"]:
                if counter is not None and counter not in self.metrics:
                    self.metrics_adddefaultmetric(counter)
        self.UI_report_add(reportid)
        self.UI_plots_update()

    def UI_report_select(self, reportid, callid):
        if hasattr(self, "UI_hasHTML") and self.UI_hasHTML:
            self.UI_reportinfo_set(self.report_infostr_HTML(reportid, callid))
        else:
            self.UI_reportinfo_set(self.report_infostr(reportid, callid))

    def UI_reportcheck_change(self, reportid, callid, state):
        self.reports[reportid]["plotting"][callid] = state
        self.UI_plots_update()

    def UI_reportcolor_change(self, reportid, callid, color):
        self.reports[reportid]["plotcolors"][callid] = color
        self.UI_report_update(reportid)
        self.UI_showplots_update()

    def UI_metricselect_change(self, metric):
        self.metric_selected = metric
        info = self.metrics[metric].__doc__
        if isinstance(info, str):
            self.UI_metricinfo_set(info.strip())
        else:
            self.UI_metricinfo_set("[no docstring for %s]" % metric)

    def UI_plot_clicked(self):
        self.UI_plot_show(self.metric_selected)
