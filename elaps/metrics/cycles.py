#!/usr/bin/env python
"""Cycle count metric."""
from __future__ import division, print_function


def metric(data, **kwargs):
    """Execution time in cycles.

    Computed as:
        cycles  (atomic metric)

    cycles: execution time in cycles (from time stamp counter)
    """
    return data.get("cycles")

metric.name = "time [cycles]"
