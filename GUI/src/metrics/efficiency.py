#!/usr/bin/env python
from __future__ import division, print_function


def metric(data, report):
    """Performance the operations relative to peak.

    This is comparing the flops/cycle to the system's peak.
    """
    nops = data.get("complexity")
    rdtsc = data.get("rdtsc")
    call = report["calls"][0]
    if nops is None or rdtsc is None or not hasattr(call, "sig"):
        return None
    sampler = report["sampler"]
    nt = report["nt"]
    datatype = call.sig.datatype()
    if "single" in datatype:
        ipc = sampler["sflops/cycle"]
    elif "double" in datatype:
        ipc = sampler["dflops/cycle"]
    else:
        return None
    return nops / (rdtsc * ipc * nt)

name = "efficiency"
