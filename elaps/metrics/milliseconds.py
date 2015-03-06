#!/usr/bin/env python
"""time in milliseconds metric."""
from __future__ import division, print_function


def metric(data, experiment, **kwargs):
    """milliseconds spent during the operations.

    Obtained form the RDTSC instruction and information on the system.
    """
    rdtsc = data.get("rdtsc")
    freq = experiment.sampler.get("frequency")
    if rdtsc is None or freq is None:
        return None
    return 1000 * rdtsc / freq

name = "time [ms]"
