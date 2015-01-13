#!/usr/bin/env python
from __future__ import division, print_function

import signature
import symbolic

import os
import sys
import time
import re
import imp
from collections import defaultdict

import traceback


class Viewer(object):
    def __init__(self):
        thispath = os.path.dirname(__file__)
        if thispath not in sys.path:
            sys.path.append(thispath)
        self.rootpath = os.path.join(thispath, "..", "..")
        self.reportpath = os.path.join(self.rootpath, "GUI", "reports")

        self.reports = []
        self.showplots = defaultdict(lambda: defaultdict(lambda: False))
        self.plottypes = ["med", "min", "avg", "max", "all"]
        self.metrics_init()
        self.UI_init()
        self.UI_setall()
        self.UI_start()

    # utility
    def log(self, *args):
        print(*args)

    def alert(self, *args):
        print(*args, file=sys.stderr)

    def metrics_init(self):
        self.metrics = {}
        metricpath = os.path.join(self.rootpath, "GUI", "src", "metrics")
        for filename in os.listdir(metricpath):
            if not filename[-3:] == ".py":
                continue
            name = filename[:-3]
            module = imp.load_source(name, os.path.join(metricpath, filename))
            if hasattr(module, name):
                self.metrics[name] = getattr(module, name)
        self.log("loaded", len(self.metrics), "metrics:",
                 *sorted(self.metrics))
        if len(self.metrics) == 0:
            raise Exception("No metrics found")

    def metrics_adddefaultmetric(self, name):
        self.metrics[name] = lambda data, sampler: data.get(name)

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

        rangevals = [0]
        if report["userange"]:
            rangevals = range(*report["range"])
        reportdata = []
        report["data"] = reportdata
        for rangeval in rangevals:
            rangevaldata = []
            reportdata.append(rangevaldata)
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
                    repdata.append(line.split())
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
        return result

    def report_infostr(self, reportid, callid):
        result = self.report_infostr_HTML(reportid, callid)
        result = result.replace("</td><td>", "\t")
        result = result.replace("</tr>", "\n")
        result = re.sub("<.*?>", "", result)
        return result

    def UI_setall(self):
        self.UI_showplots_update()

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
        if report["usepapi"]:
            for counter in report["counters"]:
                if counter is not None and counter not in self.metrics:
                    self.metrics_adddefaultmetric(counter)
        self.UI_report_add(reportid)

    def UI_report_select(self, reportid, callid):
        if hasattr(self, "UI_hasHTML") and self.UI_hasHTML:
            self.UI_info_set(self.report_infostr_HTML(reportid, callid))
        else:
            self.UI_info_set(self.report_infostr(reportid, callid))

    def UI_reportcheck_change(self, reportid, callid, state):
        self.alert("reportcheck_change", reportid, callid, state)

    def UI_showplot_click(self):
        self.UI_load_report(os.path.join(self.reportpath, "dgemm.smpl"))
        self.UI_report_select(0, None)
