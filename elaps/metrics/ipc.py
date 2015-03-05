#!/usr/bin/env python
"""flops/cycle metric."""
from __future__ import division, print_function


def metric(data, **kwargs):
    """Floating point operations per cycle.

    Counting mathematically required operations.
    Not accounting for Turbo Boost.
    """
    nops = data.get("flops")
    rdtsc = data.get("rdtsc")
    if nops is None or rdtsc is None:
        return None
    return nops / rdtsc

name = "flops/cycle"
