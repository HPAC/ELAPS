#!/usr/bin/env python
"""Gflops/second metric."""
from __future__ import division, print_function


def metric(data, **kwargs):
    """Billions of floating point operations per second.

    Counting mathematically required operations.
    """
    nops = data.get("flops")
    rdtsc = data.get("rdtsc")
    freq = experiment.sampler.get("frequency")
    if nops is None or rdtsc is None or freq is None:
        return None
    return 1e-9 * nops * (freq / rdtsc)

name = "Gflops/s"
