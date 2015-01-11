#!/usr/bin/env python
from __future__ import division, print_function

import signature
import symbolic

import os
import sys
import time

import traceback


class Viewer(object):
    def __init__(self):
        thispath = os.path.dirname(__file__)
        if thispath not in sys.path:
            sys.path.append(thispath)
        self.rootpath = os.path.join(thispath, "..", "..")
        self.reportpath = os.path.join(self.rootpath, "GUI", "reports")

        self.state_init()
        self.UI_init()
        self.UI_start()
        return

        self.UI_setall()

    # utility
    def log(self, *args):
        print(*args)

    def alert(self, *args):
        print(*args, file=sys.stderr)

    def state_init(self):
        self.reports = []

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

    def report_infostr(self, reportid, callid):
        report = self.reports[reportid]
        sampler = report["sampler"]
        result = ""
        result += "File:\t%s\n" %report["filename"]
        result += "CPU:\t%s\n" % sampler["cpu_model"]
        result += "#threads: %d\n" % report["nt"]
        result += "BLAS:\t%s\n" % sampler["blas_name"]
        if report["valid"]:
            timeobj = time.localtime(report["endtime"])
            result += time.strftime("Date:\t%c\n", timeobj)
        else:
            result += "<i>Report is invalid</i>\n"
        if report["userange"]:
            result += "Range:\t%s = %d:%d:%d\n" % (
                report["rangevar"],
                report["range"][0],
                report["range"][2],
                report["range"][1] - 1
            )

        def format_call(call):
            return call[0] + "(" + ", ".join(map(str, call[1:])) + ")"

        if callid is None:
            if len(report["calls"]) > 1:
                result += "Calls:\n"
                for call in report["calls"]:
                    result += "\t%s\n" % format_call(call)
            else:
                result += "Call:\t%s\n" % format_call(report["calls"][0])
        else:
            result += "Call:\t%s\n" % format_call(report["calls"][callid])
        return result

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
        self.UI_report_add(reportid)

    def UI_report_select(self, reportid, callid):
        self.UI_info_set(self.report_infostr(reportid, callid))

    def UI_reportcheck_change(self, reportid, callid, state):
        self.alert("reportcheck_change", reportid, callid, state)

    def UI_showplot_click(self):
        self.UI_load_report(os.path.join(self.reportpath, "dgemm.smpl"))
        self.UI_report_select(0, None)
