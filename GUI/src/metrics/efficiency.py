#!/usr/bin/env python
"""Efficiency metric."""
from __future__ import division, print_function


def metric(data, report, callid):
    """Performance the operations relative to peak.

    Comparing the flops/cycle to the system's peak.
    Not acocuting for Turbo Boost.
    """
    nops = data.get("complexity")
    rdtsc = data.get("rdtsc")
    if nops is None or rdtsc is None:
        return None

    # get datatype
    calls = report["calls"]
    if callid is not None:
        calls = [report["calls"][callid]]
    if any(not hasattr(call, "sig") for call in calls):
        return None
    datatypes = set(call.sig.datatype() for call in calls)
    if len(datatypes) > 1:
        return None
    datatype = datatypes.pop()

    # get ipc
    sampler = report["sampler"]
    if "single" in datatype:
        ipc = sampler["sflops/cycle"]
    elif "double" in datatype:
        ipc = sampler["dflops/cycle"]
    else:
        return None

    # get #threads
    nt = report["nt"]
    if report["options"]["omp"]:
        nt *= len(report["calls"])
    nt = min(sampler["ncores"], nt)
    if report["userange"]["inner"] == "omp":
        nt = sampler["ncores"]

    return nops / (rdtsc * ipc * nt)

name = "efficiency"
