#!/usr/bin/env python
"""time in milliseconds metric."""
from __future__ import division, print_function


def metric(data, report, callid):
    """milliseconds spent during the operations.

    Obtained form the RDTSC instruction and information on the system.
    """
    rdtsc = data.get("rdtsc")
    if rdtsc is None:
        return None
    freq = report["sampler"]["frequency"]
    return 1000 * rdtsc / freq

name = "time [ms]"
