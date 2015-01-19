#!/usr/bin/env python
from __future__ import division, print_function


def metric(data, report, callid):
    """Billions of floating point operations per second.

    Counting mathematically required operations (see flops).
    """
    nops = data.get("complexity")
    rdtsc = data.get("rdtsc")
    if nops is None or rdtsc is None:
        return None
    freq = report["sampler"]["frequency"]
    return 1e-9 * nops * (freq / rdtsc)

name = "Gflops/s"
