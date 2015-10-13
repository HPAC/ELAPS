#!/usr/bin/env python
"""Time in seconds metric."""
from __future__ import division, print_function


def metric(data, experiment, **kwargs):
    """Seconds spent during the operations.

    Obtained form the CPU's time stamp counter and information on the system.
    """
    cycles = data.get("cycles")
    freq = experiment.sampler.get("frequency")
    if cycles is None or freq is None:
        return None
    return cycles / freq

metric.name = "time [s]"
