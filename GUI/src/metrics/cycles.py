#!/usr/bin/env python
"""Cycle count metric."""
from __future__ import division, print_function


def metric(data, report, callid):
    """Number of cycles spent during the operations.

    Obtained form the RDTSC instruction.
    Not accounting for Turbo Boost.
    """
    return data.get("rdtsc")

name = "cycles"
