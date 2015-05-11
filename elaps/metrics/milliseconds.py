#!/usr/bin/env python
"""time in milliseconds metric."""
from __future__ import division, print_function


def metric(data, experiment, **kwargs):
    """milliseconds spent during the operations.

    Obtained form the CPU's time stamp counter and information on the system.
    """
    cycles = data.get("cycles")
    freq = experiment.sampler.get("frequency")
    if cycles is None or freq is None:
        return None
    return 1000 * cycles / freq

name = "time [ms]"
