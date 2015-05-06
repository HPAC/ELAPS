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
]
background_color = "#f0f0f0"
face_color = "#ffffff"

# plot styles
plot_styles = {
    "legend": {"color": "#808080"},
    "med": {"linestyle": "-"},
    "min": {"linestyle": "--"},
    "max": {"linestyle": ":", "linewidth": 2},
    "avg": {"linestyle": "-."},
    "min-max": {"hatch": "...", "facecolor": (0, 0, 0, 0)},
    "std": {"alpha": .25},
    "all": {"linestyle": "None", "marker": "."},
}

# PlayMat
viz_scale = 100
default_dim = 1000
default_experiment_str = """
Experiment(
    range=[Symbol("i"), Range((100, 100, 2000))],
    nreps=10,
    calls=[
        Signature(
            "dgemm",
            Trans("transA"), Trans("transB"),
            Dim("m"), Dim("n"), Dim("k"),
            dScalar(),
            dData("A", "ldA * (k if transA == 'N' else m)"),
            Ld("ldA", "m if transA == 'N' else k"),
            dData("B", "ldB * (n if transB == 'N' else k)"),
            Ld("ldB", "k if transB == 'N' else n"),
            dScalar("beta"),
            dData("C", "ldC * n"), Ld("ldC", "m"),
            complexity="2 * m * n * k"
        )(
            "N", "N", Symbol("i"), Symbol("i"), Symbol("i"),
            1, "A", Symbol("i"), "B", Symbol("i"), 1, "C", Symbol("i")
        )
    ]
)
"""
