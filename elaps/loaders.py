#!/usr/bin/env python
"""Utility routines to load ELAPS objects."""
from __future__ import division, print_function

from signature import *
from symbolic import *
from experiment import Experiment

import os

rootpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sigpath = os.path.join(rootpath, "data", "signatures")
docpath = os.path.join(rootpath, "data", "kerneldocs")
samplerpath = os.path.join(rootpath, "Sampler", "build")


def load_signature_file(filename):
    """Load a Signature from a file."""
    with open(filename) as fin:
        return eval(fin.read())


def load_signature(name):
    """Find and load a Signature."""
    for dirname in os.listdir(sigpath):
        dirpath = os.path.join(sigpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        filename = os.path.join(dirpath, name + ".pysig")
        if os.path.isfile(filename):
            return load_signature_file(filename)
    raise IOError("No signature found for %s" % name)


def load_all_signatures():
    """Load all Signatures."""
    sigs = {}
    for dirname in os.listdir(sigpath):
        dirpath = os.path.join(sigpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        for filename in os.listdir(sigpath):
            if not filename[-6:] == ".pysig":
                continue
            filepath = os.path.join(dirpath, filename)
            if not os.path.isfile(filepath):
                continue
            sig = load_signature_file(filepath)
            sigs[str(sig[0])] = sig
    return sigs


def load_experiment(filename):
    """Load an experiment."""
    with open(filename) as fin:
        return eval(fin.readline())


def load_doc_file(filename):
    """Load a documentation."""
    with open(filename) as fin:
        return eval(fin.read())


def load_doc(name):
    """Load documentation for name."""
    for dirname in os.listdir(docpath):
        dirpath = os.path.join(docpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        filepath = os.path.join(dirpath, name + ".pydoc")
        if os.path.isfile(filepath):
            return load_doc_file(filepath)
    raise IOError("No documentation found for %s" % name)


def load_all_docs():
    """Load all documenations."""
    docs = {}
    for dirname in os.listdir(docpath):
        dirpath = os.path.join(docpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        for filename in os.listdir(sigpath):
            if not filename[-6:] == ".pydoc":
                continue
            filepath = os.path.join(dirpath, filename)
            if not os.path.isfile(filepath):
                continue
            docs[filename[:-6]] = load_doc_file(filepath)
    return docs


def load_sampler_file(filename):
    """Load a Sampler from a file."""
    with open(filename) as fin:
        return eval(fin.read())


def load_sampler(name):
    """Find and load a Sampler."""
    filename = os.path.join(samplerpath, name, "info.py")
    if os.path.isfile(filename):
        return load_sampler_file(filename)
    raise IOError("Sampler %s not found" % name)


def load_all_samplers():
    """Load all Samplers."""
    samplers = {}
    for dirname in os.listdir(samplerpath):
        filename = os.path.join(samplerpath, dirname, "info.py")
        if os.path.isfile(filename):
            samplers[dirname] = load_sampler_file(filename)
    return samplers


def load_report(name):
    """Load a report from a frile."""
    # TODO
