#!/usr/bin/env python
from __future__ import division, print_function


def metric(data, report, callid):
    """milliseconds spent during the operations.

    This is obtained form the RDTSC instruction and information on the system.
    """
    rdtsc = data.get("rdtsc")
    if rdtsc is None:
        return None
    freq = report["sampler"]["frequency"]
    return 1000 * rdtsc / freq

name = "time [ms]"
