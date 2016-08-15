#!/usr/bin/env python
"""Time metric in milliseconds."""
from __future__ import division, print_function


def metric(data, experiment, **kwargs):
    """Execution time in milliseconds.

    Computed as:
        1000 * cycles / freq

    1000:   Milli prefix
    cycles: execution time in cycles (from time step counter)
    freq:   CPU frequency
    """
    cycles = data.get("cycles")
    freq = experiment.sampler.get("frequency")
    if cycles is None or freq is None:
        return None
    return 1000 * cycles / freq

metric.name = "time [ms]"
