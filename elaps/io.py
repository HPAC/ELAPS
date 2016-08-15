#!/usr/bin/env python
"""Utility routines to load ELAPS objects."""
from __future__ import division, print_function

from . import defines, Experiment, Report
from .symbolic import *
from .signature import *

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


def load_signature(name, cache={}):
    """Find and load a Signature."""
    if isinstance(cache, dict):
        if name not in cache:
            cache[name] = load_signature(name, False)
        return cache[name]
    for dirname in os.listdir(defines.sigpath):
        dirpath = os.path.join(defines.sigpath, dirname)
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
    if not os.path.isdir(defines.sigpath):
        return {}
    sigs = {}
    for dirname in os.listdir(defines.sigpath):
        dirpath = os.path.join(defines.sigpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        for filename in os.listdir(os.path.join(defines.sigpath, dirname)):
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
        if filename[-4:] == "." + defines.experiment_extension:
            return load_experiment_string(fin.read())
        return load_experiment_string(fin.readline())


def load_doc_file(filename):
    """Load a documentation."""
    with open(filename) as fin:
        return eval(fin.read())


def load_doc(name, cache={}):
    """Load documentation for name."""
    if isinstance(cache, dict):
        if name not in cache:
            cache[name] = load_doc(name, False)
        return cache[name]
    for dirname in os.listdir(defines.docpath):
        dirpath = os.path.join(defines.docpath, dirname)
        if not os.path.isdir(dirpath):
            continue
        filepath = os.path.join(dirpath, name + ".pydoc")
        if os.path.isfile(filepath):
            return load_doc_file(filepath)
    raise IOError("No documentation found for %s" % name)


def load_all_docs():
    """Load all documentations."""
    if not os.path.isdir(defines.docpath):
        return {}
    docs = {}
    for dirname in os.listdir(defines.docpath):
        dirpath = os.path.join(defines.docpath, dirname)
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


def load_sampler(name, cache={}):
    """Find and load a Sampler."""
    if isinstance(cache, dict):
        if name not in cache:
            cache[name] = load_sampler(name, False)
        return cache[name]
    filename = os.path.join(defines.samplerpath, name, "info.py")
    if os.path.isfile(filename):
        return load_sampler_file(filename)
    raise IOError("Sampler %s not found" % name)


def load_all_samplers():
    """Load all Samplers."""
    if not os.path.isdir(defines.samplerpath):
        return {}
    samplers = {}
    for dirname in os.listdir(defines.samplerpath):
        filename = os.path.join(defines.samplerpath, dirname, "info.py")
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


def load_backend(name, cache={}):
    """Load a backend."""
    if isinstance(cache, dict):
        if name not in cache:
            cache[name] = load_backend(name, False)
        return cache[name]
    filename = os.path.join(defines.backendpath, name + ".py")
    if os.path.isfile(filename):
        return load_backend_file(filename)
    raise IOError("Backend %s not found" % name)


def load_all_backends():
    """Load all backends."""
    if not os.path.isdir(defines.backendpath):
        return {}
    backends = {}
    for filename in os.listdir(defines.backendpath):
        if filename[-3:] != ".py":
            continue
        filepath = os.path.join(defines.backendpath, filename)
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
    with open(defines.papinamespath) as fin:
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
    errfile = "%s.%s" % (filename[:-4], defines.error_extension)
    if os.path.isfile(errfile) and os.path.getsize(errfile):
        report.error = True
    return report


def load_metric_file(filename):
    """Load a metric from a file."""
    name = os.path.basename(filename)[:-3]
    module = imp.load_source(name, filename)
    metric = module.metric
    return metric


def load_metric(name, cache={}):
    """Load a metric."""
    if isinstance(cache, dict):
        if name not in cache:
            cache[name] = load_metric(name, False)
        return cache[name]
    filename = os.path.join(defines.metricpath, name + ".py")
    if os.path.isfile(filename):
        return load_metric_file(filename)
    raise IOError("Metric %s not found" % name)


def load_all_metrics():
    """Load all metrics."""
    if not os.path.isdir(defines.metricpath):
        return {}
    metrics = {}
    for filename in os.listdir(defines.metricpath):
        if filename[-3:] != ".py":
            continue
        filepath = os.path.join(defines.metricpath, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            metric = load_metric_file(filepath)
            metrics[metric.name] = metric
        except:
            pass
    return metrics


def get_counter_metric(counter, name=None, doc=None):
    """Create a metric for a PAPI counter."""
    if name is None:
        name = counter

    def metric(data, **kwargs):
        return data.get(counter)
    metric.name = name
    metric.__doc__ = doc
    return metric
