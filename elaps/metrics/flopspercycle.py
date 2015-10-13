#!/usr/bin/env python
"""Flops/cycle metric."""
from __future__ import division, print_function


def metric(data, **kwargs):
    """Floating point operations per cycle.

    Counting mathematically required operations.
    Not accounting for Turbo Boost.
    """
    nops = data.get("flops")
    cycles = data.get("cycles")
    if nops is None or cycles is None:
        return None
    return nops / cycles

metric.name = "flops/cycle"
