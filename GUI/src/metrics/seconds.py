#!/usr/bin/env python
"""time in seconds metric."""
from __future__ import division, print_function


def metric(data, report, callid):
    """seconds spent during the operations.

    Obtained form the RDTSC instruction and information on the system.
    """
    rdtsc = data.get("rdtsc")
    if rdtsc is None:
        return None
    freq = report["sampler"]["frequency"]
    return rdtsc / freq

name = "time [s]"
