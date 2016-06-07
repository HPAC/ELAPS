#!/usr/bin/env python
"""Performance metric in flops/cycle metric."""
from __future__ import division, print_function


def metric(data, **kwargs):
    """Performance in floating-point operations (flops) per cycle.

    Computed as:
        flops / cycles

    flops:  minimal required mathematical flop count
    cycles: execution time in cycles (from time step counter)
    """
    nops = data.get("flops")
    cycles = data.get("cycles")
    if nops is None or cycles is None:
        return None
    return nops / cycles

metric.name = "performance [flops/cycle]"
