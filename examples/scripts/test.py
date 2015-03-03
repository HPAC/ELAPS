#!/usr/bin/env python
"""Example script for Experiment usage."""
from __future__ import division, print_function

import sys

sys.path.append("../../elaps/")

from experiment import Experiment
from elapsio import load_sampler, load_signature, load_backend

sampler = load_sampler("Mac_OpenBLAS")
dgemm = load_signature("dgemm_")
backend_local = load_backend("local")

ex = Experiment(sampler=sampler)
ex.range = ("i", range(100, 1000 + 1, 100))
ex.nreps = 10
ex.call = ex.ranges_parse(dgemm("n", "n", "i", "i", "i", 1,
                                "a", None, "b", None, 1, "c", None))
ex.infer_lds()

ex.submit("test", backend_local)
