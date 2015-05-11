#!/usr/bin/env python
"""flops/second metric."""
from __future__ import division, print_function


def metric(data, experiment, **kwargs):
    """Floating point operations per second.

    Counting mathematically required operations.
    """
    nops = data.get("flops")
    cycles = data.get("cycles")
    freq = experiment.sampler.get("frequency")
    if nops is None or cycles is None or freq is None:
        return None
    return nops * (freq / cycles)

name = "flops/s"
