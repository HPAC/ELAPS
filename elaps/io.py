#!/usr/bin/env python
"""Utility routines to load ELAPS objects."""
from __future__ import division, print_function

from signature import *
from symbolic import *
from experiment import Experiment
from report import Report

import os
import imp

rootpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sigpath = os.path.join(rootpath, "resources", "signatures")
docpath = os.path.join(rootpath, "resources", "kerneldocs")
samplerpath = os.path.join(rootpath, "Sampler", "build")
backendpath = os.path.join(rootpath, "elaps", "backends")
setuppath = os.path.join(rootpath, "setups")
reportpath = os.path.join(rootpath, "reports")
metricpath = os.path.join(rootpath, "elaps", "metrics")
papinamespath = os.path.join(rootpath, "resources", "papinames.py")


def write_signature(sig, filename):
    """Write a Siganture."""
    with open(filename, "w") as fout:
        fout.write(repr(sig))


def load_signature_string(string):
    """Load a Signature from a string."""
    sig = eval(string)
    if not isinstance(sig, Signature):
        raise TypeError("not a Signature")
    return sig


def load_signature_file(filename):
    """Load a Signature from a file."""
    with open(filename) as fin:
        return load_signature_string(fin.read())


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


def write_experiment(ex, filename):
    """Write an Experiment."""
    with open(filename, "w") as fout:
        fout.write(repr(ex))


def load_experiment_string(string):
    """Load a Experiment from a string."""
    ex = eval(string)
    if not isinstance(ex, Experiment):
        raise TypeError("not an Experiment")
    return ex


def load_experiment(filename):
    """Load an Experiment."""
    with open(filename) as fin:
        if filename[-4:] == ".ees":
            return eval(fin.read())
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
            if filename[-6:] != ".pydoc":
                continue
            filepath = os.path.join(dirpath, filename)
            if not os.path.isfile(filepath):
                continue
            try:
                docs[filename[:-6]] = load_doc_file(filepath)
            except:
                pass
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
            try:
                samplers[dirname] = load_sampler_file(filename)
            except:
                pass
    return samplers


def load_backend_file(filename):
    """Load a backend from a file."""
    name = os.path.basename(filename)[:-3]
    module = imp.load_source(name, filename)
    return module.Backend()


def load_backend(name):
    """Load a backend."""
    filename = os.path.join(backendpath, name + ".py")
    if os.path.isfile(filename):
        return load_backend_file(filename)
    raise IOError("Backend %s not found" % name)


def load_all_backends():
    """Load all backends."""
    backends = {}
    for filename in os.listdir(backendpath):
        if filename[-3:] != ".py":
            continue
        filepath = os.path.join(backendpath, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            backends[filename[:-3]] = load_backend_file(filepath)
        except:
            pass
    return backends


def load_papinames():
    """Load all papi names."""
    with open(papinamespath) as fin:
        return eval(fin.read())


def load_report(filename):
    """Load a Report from a frile."""
    # TODO: check for error file
    with open(filename) as fin:
        experiment = eval(fin.readline())
        rawdata = [map(eval, line.split()) for line in fin.readlines()]
        return Report(experiment, rawdata)


def load_metric_file(filename):
    """Load a metric from a file."""
    name = os.path.basename(filename)[:-3]
    module = imp.load_source(name, filename)
    metric = module.metric
    metric.name = module.name
    return metric


def load_metric(name):
    """Load a metric."""
    filename = os.path.join(metricpath, name + ".py")
    if os.path.isfile(filename):
        return load_metric_file(filename)
    raise IOError("Metric %s not found" % name)


def load_all_metrics():
    """Load all metrics."""
    metrics = {}
    for filename in os.listdir(metricpath):
        if filename[-3:] != ".py":
            continue
        filepath = os.path.join(metricpath, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            metric = load_metric_file(filepath)
            metrics[metric.name] = metric
        except:
            pass
    return metrics
