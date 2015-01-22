#!/usr/bin/env python
from __future__ import division, print_function


def metric(data, report, callid):
    """Floating point operations per cycle.

    Counting mathematically required operations.
    Not accounting for Turbo Boost.
    """
    nops = data.get("complexity")
    rdtsc = data.get("rdtsc")
    if nops is None or rdtsc is None:
        return None
    return nops / rdtsc

name = "flops/cycle"
