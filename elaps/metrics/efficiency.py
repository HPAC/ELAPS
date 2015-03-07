#!/usr/bin/env python
"""Efficiency metric."""
from __future__ import division, print_function


def metric(data, experiment, nthreads, callid, **kwargs):
    """Performance the operations relative to peak.

    Comparing the flops/cycle to the system's peak.
    Not acocuting for Turbo Boost.
    """
    nops = data.get("flops")
    rdtsc = data.get("rdtsc")
    if nops is None or rdtsc is None:
        return None

    # get datatype
    calls = experiment.calls
    if callid is not None:
        calls = [callid[callid]]
    if any(not hasattr(call, "sig") for call in calls):
        return None
    datatypes = set(call.sig.datatype() for call in calls)
    if len(datatypes) > 1:
        return None
    datatype = datatypes.pop()

    # get ipc
    sampler = experiment.sampler
    if "single" in datatype:
        ipc = sampler["sflops/cycle"]
    elif "double" in datatype:
        ipc = sampler["dflops/cycle"]
    else:
        return None

    return nops / (rdtsc * ipc * nthreads)

name = "efficiency"