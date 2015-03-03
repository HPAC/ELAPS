#!/usr/bin/env python
"""Utility routines to load ELAPS objects."""
from __future__ import division, print_function

from signature import *
from symbolic import *
from experiment import Experiment

import os

rootpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_signature_file(filename):
    """Load a Signature from a file."""
    with open(filename) as fin:
        return eval(fin.read())


def load_signature(name):
    """Find a load a Signature."""
    sigpath = os.path.join(rootpath, "data", "signatures")
    for dirname in os.listdir(sigpath):
        dirpath = os.path.join(sigpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        filename = os.path.join(dirpath, name + ".pysig")
        if os.path.isfile(filename):
            return load_signature_file(filename)
    return None


def load_experiment(filename):
    """Load an experiment."""
    with open(filename) as fin:
        return eval(fin.read())


def load_doc(name):
    """Load documentation for name."""
    docpath = os.path.join(rootpath, "data", "kerneldocs")
    for dirname in os.listdir(docpath):
        dirpath = os.path.join(docpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        filename = os.path.join(dirpath, name + ".pydoc")
        if os.path.isfile(filename):
            with open(filename) as fin:
                return eval(fin.read())
    raise IOError("No documentation found for %s" % name)


def load_report(name):
    """Load a report from a frile."""
    # TODO
