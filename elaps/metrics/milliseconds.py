#!/usr/bin/env python
"""Time in milliseconds metric."""
from __future__ import division, print_function


def metric(data, experiment, **kwargs):
    """Milliseconds spent during the operations.

    Obtained form the CPU's time stamp counter and information on the system.
    """
    cycles = data.get("cycles")
    freq = experiment.sampler.get("frequency")
    if cycles is None or freq is None:
        return None
    return 1000 * cycles / freq

metric.name = "time [ms]"
