#!/usr/bin/env python
from __future__ import division, print_function


def metric(data, report, callid):
    """Number of floating point operations necessary to perform the operation.

    This is the number of mathematically required operations,
    not the actual number of operations performed by the implementation.
    """
    return data.get("complexity")

name = "flops"
