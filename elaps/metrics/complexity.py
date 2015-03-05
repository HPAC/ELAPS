#!/usr/bin/env python
"""Flops (complexity) metric."""
from __future__ import division, print_function


def metric(data, **kwargs):
    """Number of floating point operations necessary to perform the operation.

    Counting mathematically required operations.
    """
    return data.get("flops")

name = "flops"
