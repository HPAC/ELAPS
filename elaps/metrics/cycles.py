#!/usr/bin/env python
"""Cycle count metric."""
from __future__ import division, print_function


def metric(data, **kwargs):
    """Number of cycles spent during the operations.

    Obtained form the CPU's time stamp counter.
    Not accounting for Turbo Boost.
    """
    return data.get("cycles")

name = "cycles"
