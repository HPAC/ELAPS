#!/usr/bin/env python
from __future__ import division, print_function


def metric(data, report):
    nops = data.get("complexity")
    rdtsc = data.get("rdtsc")
    if nops is None or rdtsc is None:
        return None
    return nops / rdtsc

name = "flops/cycle"
