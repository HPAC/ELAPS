#!/usr/bin/env python
"""flops/second metric."""
from __future__ import division, print_function


def metric(data, report, callid):
    """Floating point operations per second.

    Counting mathematically required operations.
    """
    nops = data.get("complexity")
    rdtsc = data.get("rdtsc")
    if nops is None or rdtsc is None:
        return None
    freq = report["sampler"]["frequency"]
    return nops * (freq / rdtsc)

name = "flops/s"
