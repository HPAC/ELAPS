#!/usr/bin/env python
"""time in seconds metric."""
from __future__ import division, print_function


def metric(data, experiment, **kwargs):
    """Seconds spent during the operations.

    Obtained form the RDTSC instruction and information on the system.
    """
    rdtsc = data.get("rdtsc")
    freq = experiment.sampler.get("frequency")
    if rdtsc is None or freq is None:
        return None
    return rdtsc / freq

name = "time [s]"
