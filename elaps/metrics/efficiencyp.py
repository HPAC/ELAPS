#!/usr/bin/env python
"""Efficiency metric in %."""
from __future__ import division, print_function


def metric(data, experiment, nthreads, selector, **kwargs):
    """Performance of the operations relative to peak in %.

    Comparing the flops/cycle to the system's peak.
    Not accounting for Turbo Boost.
    """
    nops = data.get("flops")
    cycles = data.get("cycles")
    if nops is None or cycles is None:
        return None

    # get datatype
    datatypes = set()
    calls = experiment.calls
    ncalls = len(calls)
    for callid, call in enumerate(calls):
        if (experiment.sumrange_parallel or experiment.calls_parallel
                or selector([int(callid == i) for i in range(ncalls)]) != 0):
            # selector responds to call i
            if not hasattr(call, "sig"):
                return None
            datatypes.add(call.sig.datatype())
    if len(datatypes) != 1:
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
    ncores = min(sampler["ncores"], nthreads)

    return 100 * nops / (cycles * ipc * ncores)

metric.name = "efficiency [%]"
