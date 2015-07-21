#!/usr/bin/env python
"""Utility routines to load ELAPS objects."""
from __future__ import division, print_function

from signature import *
from symbolic import *
from experiment import Experiment
from report import Report
from defines import *

import os
import imp
from collections import defaultdict


def write_signature(sig, filename):
    """Write a Signature."""
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
            sig = load_signature_file(filename)
            if str(sig[0]) != name:
                raise IOError("Routine mismatch for Signature %s" % name)
            return sig
    raise IOError("No signature found for %s" % name)


def load_all_signatures():
    """Load all Signatures."""
    if not os.path.isdir(sigpath):
        return {}
    sigs = {}
    for dirname in os.listdir(sigpath):
        dirpath = os.path.join(sigpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        for filename in os.listdir(os.path.join(sigpath, dirname)):
            if not filename[-6:] == ".pysig":
                continue
            filepath = os.path.join(dirpath, filename)
            if not os.path.isfile(filepath):
                continue
            try:
                sig = load_signature_file(filepath)
            except:
                raise IOError("Error parsing %s" % filepath)
            if str(sig[0]) != filename[:-6]:
                raise IOError("Routine mismatch for %s" % filepath)
            sigs[str(sig[0])] = sig
    return sigs


def write_experiment(experiment, filename):
    """Write an Experiment."""
    with open(filename, "w") as fout:
        fout.write(repr(experiment))


def load_experiment_string(string):
    """Load a Experiment from a string."""
    ex = eval(string)
    if not isinstance(ex, Experiment):
        raise TypeError("not an Experiment")
    try:
        ex.sampler["backend"] = None
        ex.sampler["backend"] = load_backend(ex.sampler["backend_name"])
    except:
        pass
    return ex


def load_experiment(filename):
    """Load an Experiment."""
    with open(filename) as fin:
        if filename[-4:] == "." + experiment_extension:
            return load_experiment_string(fin.read())
        return load_experiment_string(fin.readline())


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
    """Load all documentations."""
    if not os.path.isdir(docpath):
        return {}
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
        sampler = eval(fin.read())
    try:
        sampler["backend"] = load_backend(sampler["backend_name"])
    except:
        sampler["backend"] = None
    return sampler


def load_sampler(name):
    """Find and load a Sampler."""
    filename = os.path.join(samplerpath, name, "info.py")
    if os.path.isfile(filename):
        return load_sampler_file(filename)
    raise IOError("Sampler %s not found" % name)


def load_all_samplers():
    """Load all Samplers."""
    if not os.path.isdir(samplerpath):
        return {}
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
    if not os.path.isdir(backendpath):
        return {}
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
    """Load all PAPI names."""
    class keydefaultdict(defaultdict):
        def __missing__(self, key):
            self[key] = self.default_factory(key)
            return self[key]
    with open(papinamespath) as fin:
        return keydefaultdict(lambda key: {"short": key, "long": key},
                              eval(fin.read()))


def load_report(filename, discard_first_repetitions=False):
    """Load a Report from a file."""
    with open(filename) as fin:
        experiment = eval(fin.readline())
        rawdata = []
        for line in fin:
            vals = []
            for val in line.split():
                try:
                    val = int(val)
                except:
                    pass
                vals.append(val)
            rawdata.append(vals)
    report = Report(experiment, rawdata)
    if discard_first_repetitions:
        return report.discard_first_repetitions()
    errfile = "%s.%s" % (filename[:-4], error_extension)
    if os.path.isfile(errfile) and os.path.getsize(errfile):
        report.error = True
    return report


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
    if not os.path.isdir(metricpath):
        return {}
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
