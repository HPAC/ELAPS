#!/usr/bin/env python
from __future__ import division, print_function


def metric(data, report):
    """Number of cycles spent during the operations.

    This is obtained form the RDTSC instruction.
    It does not account for Turbo Boost.
    """
    return data.get("rdtsc")

name = "cycles"
