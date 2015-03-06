#!/usr/bin/env python
"""flops/second metric."""
from __future__ import division, print_function


def metric(data, experiment, **kwargs):
    """Floating point operations per second.

    Counting mathematically required operations.
    """
    nops = data.get("flops")
    rdtsc = data.get("rdtsc")
    freq = experiment.sampler.get("frequency")
    if nops is None or rdtsc is None or freq is None:
        return None
    return nops * (freq / rdtsc)

name = "flops/s"
