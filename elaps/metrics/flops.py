#!/usr/bin/env python
"""Flop-count metric."""
from __future__ import division, print_function


def metric(data, **kwargs):
    """Minimum required number of floating-point operations (flops).

    Computed as:
        flops (atomic metric)

    flops:  minimal required mathematical flop count
    """
    return data.get("flops")

metric.name = "flops"
