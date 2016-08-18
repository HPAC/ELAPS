#!/usr/bin/env python
"""Efficiency metric in %."""
from __future__ import division, print_function


def metric(data, experiment, nthreads, selector, **kwargs):
    """Relative utilization of the hardware's floating point units in %.

    Computed as:
        100 * flops / (ipc * cycles * ncores)

    100:    conversion to percentage
    flops:  minimal required mathematical flop count
    ipc:    maximum instructions per cycle and core (hardware limit)
    cycles: execution time in cycles (from time stamp counter)
    ncores: number of cores used
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
