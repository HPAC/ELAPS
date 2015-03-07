#!/usr/bin/env python
"""Example script for Experiment usage."""
from __future__ import division, print_function

import sys

sys.path.append("../../")

from elaps.experiment import Experiment
from elaps.io import load_sampler, load_signature

sampler = load_sampler("Mac_OpenBLAS")
dgemm = load_signature("dgemm_")

ex = Experiment(sampler=sampler)
ex.range = ["i", range(100, 1000 + 1, 100)]
ex.nreps = 10
ex.call = ex.ranges_parse(dgemm("N", "N", "i", "i", "i", 1,
                                "A", None, "B", None, 1, "C", None))
ex.infer_lds()

ex.submit("test")
