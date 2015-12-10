#!/usr/bin/env python
"""ELAPS package wide constants."""
from __future__ import division, print_function

import os
from random import randint

# root path
filepath = os.path.dirname(os.path.realpath(__file__))
rootpath = os.path.abspath(os.path.join(filepath, ".."))

# file paths
sigpath = os.path.join(rootpath, "resources", "signatures")
docpath = os.path.join(rootpath, "resources", "kerneldocs")
samplerpath = os.path.join(rootpath, "Sampler", "build")
backendpath = os.path.join(rootpath, "elaps", "backends")
reportpath = os.path.join(rootpath, "reports")
experimentpath = reportpath
metricpath = os.path.join(rootpath, "elaps", "metrics")
papinamespath = os.path.join(rootpath, "resources", "papinames.py")

# extensions
report_extension = "elr"
report_extensions = ("elr", "eer")
experiment_extension = "ele"
experiment_extensions = ("ele", "els", "ees") + report_extensions
script_extension = "sh"
calls_extension = "calls"
error_extension = "err"

# colors
colors = [
    "#ff0000", "#00c000", "#0000ff", "#c0c000", "#00c0c0", "#c000c0",  # light
    "#800000", "#008000", "#000080", "#808000", "#008080", "#800080",  # dark
    "#ff8000", "#00ff80", "#8000ff", "#80ff00", "#0080ff", "#ff0080",  # mixed
    "#c04000", "#00c040", "#4000c0", "#40c000", "#0040c0", "#c00040",  # mdark
] + ["#%6x" % randint(0, 0xFFFFFF) for _ in range(100)]
background_color = "#f0f0f0"
face_color = "#ffffff"

# plot styles
plot_styles = {
    "legend": {"color": "#808080"},
    "grid": {"zorder": 0, "color": "#808080", "linestyle": "-"},
    "bar": {"zorder": 3},
    "all": {"zorder": 3, "linestyle": "None", "marker": "."},
    "med": {"zorder": 3, "linestyle": "-"},
    "min": {"zorder": 3, "linestyle": "--"},
    "max": {"zorder": 3, "linestyle": ":", "linewidth": 2},
    "avg": {"zorder": 3, "linestyle": "-."},
    "min-max": {"zorder": 3, "hatch": "...", "facecolor": (0, 0, 0, 0)},
    "std": {"zorder": 3, "alpha": .25},
}

# PlayMat
viz_scale = 100
default_dim = 1000
default_reportname = "default"
jobprogress_timeout = 1000
truncatedreload_timeout = 5000
github_url = "https://github.com/HPAC/ELAPS/"
