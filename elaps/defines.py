#!/usr/bin/env python
"""ELAPS package wide constants."""
from __future__ import division, print_function

import os

# root path
filepath = os.path.dirname(os.path.realpath(__file__))
rootpath = os.path.abspath(os.path.join(filepath, ".."))

# file paths
sigpath = os.path.join(rootpath, "resources", "signatures")
docpath = os.path.join(rootpath, "resources", "kerneldocs")
samplerpath = os.path.join(rootpath, "Sampler", "build")
backendpath = os.path.join(rootpath, "elaps", "backends")
experimentpath = os.path.join(rootpath, "experiments")
reportpath = os.path.join(rootpath, "reports")
metricpath = os.path.join(rootpath, "elaps", "metrics")
papinamespath = os.path.join(rootpath, "resources", "papinames.py")

# extensions
report_extension = "elr"
report_extensions = ("elr", "eer")
experiment_extension = "els"
experiment_extensions = ("els", "ees") + report_extensions
script_extension = "sh"
calls_extension = "calls"
error_extension = "err"
