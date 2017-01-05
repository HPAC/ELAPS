"""Utility routines to load ELAPS objects."""

import os
import imp
from collections import defaultdict

from elaps import defines
from elaps import symbolic
from elaps import signature
from elaps import experiment
from elaps import report


def write_signature(sig, filepath):
    """Write a Signature."""
    with open(filepath, "w") as fout:
        fout.write(repr(sig))


def load_signature_string(string, name=None):
    """Load a Signature from a string."""
    sig = eval(string, signature.__dict__)
    if not isinstance(sig, signature.Signature):
        raise TypeError("Excpected a Signature but loaded a %s" % type(sig))
    if name and str(sig[0]) != name:
        raise IOError("Routine mismatch for Signature %s" % name)
    return sig


def load_signature_file(filepath, name=None):
    """Load a Signature from a file."""
    with open(filepath) as fin:
        return load_signature_string(fin.read(), name)


def load_signature(name, _cache={}):
    """Find and load a Signature."""
    if name not in _cache:
        filename = name + ".pysig"
        for dirpath, dirnames, filenames in os.walk(defines.sigpath):
            if filename in filenames:
                filepath = os.path.join(defines.sigpath, dirpath, filename)
                _cache[name] = load_signature_file(filepath, name)
                break
        else:
            raise IOError("No signature found for %s" % name)
    return _cache[name]


def load_all_signatures():
    """Load all Signatures."""
    sigs = {}
    for dirpath, dirnames, filenames in os.walk(defines.sigpath):
        for filename in filenames:
            if not filename[-6:] == ".pysig":
                continue
            name = filename[:-6]
            filepath = os.path.join(defines.sigpath, dirpath, filename)
            sigs[name] = load_signature_file(filepath, name)
    return sigs


def write_experiment(experiment, filepath):
    """Write an Experiment."""
    with open(filepath, "w") as fout:
        fout.write(repr(experiment))


def load_experiment_string(string, _globals={}):
    """Load a Experiment from a string."""
    if not _globals:
        _globals.update(symbolic.__dict__)
        _globals.update(signature.__dict__)
        _globals.update(experiment.__dict__)
    ex = eval(string, _globals)
    if not isinstance(ex, experiment.Experiment):
        raise TypeError("not an Experiment")
    try:
        ex.sampler["backend"] = None
        ex.sampler["backend"] = load_backend(ex.sampler["backend_name"])
    except:
        pass
    return ex


def load_experiment(filepath):
    """Load an Experiment."""
    with open(filepath) as fin:
        if filepath[-4:] == "." + defines.experiment_extension:
            return load_experiment_string(fin.read())
        return load_experiment_string(fin.readline())


def load_doc_file(filepath):
    """Load a documentation."""
    with open(filepath) as fin:
        return eval(fin.read(), {})


def load_doc(name, _cache={}):
    """Load documentation for name."""
    if name not in _cache:
        filename = name + ".pydoc"
        for dirpath, dirnames, filenames in os.walk(defines.docpath):
            if filename in filenames:
                filepath = os.path.join(defines.docpath, dirpath, filename)
                _cache[name] = load_doc_file(filepath)
                break
        else:
            raise IOError("No documentation found for %s" % name)
    return _cache[name]


def load_all_docs():
    """Load all documentations."""
    docs = {}
    for dirpath, dirnames, filenames in os.walk(defines.sigpath):
        for filename in filenames:
            if not filename[-6:] == ".pydoc":
                continue
            name = filename[:-6]
            filepath = os.path.join(defines.docpath, dirpath, filename)
            docs[name] = load_doc_file(filepath)
    return docs


def load_sampler_file(filepath):
    """Load a Sampler from a file."""
    with open(filepath) as fin:
        sampler = eval(fin.read(), {})
    try:
        sampler["backend"] = load_backend(sampler["backend_name"])
    except:
        sampler["backend"] = None
    return sampler


def load_sampler(name, _cache={}):
    """Find and load a Sampler."""
    if name not in _cache:
        filepath = os.path.join(defines.samplerpath, name, "info.py")
        if os.path.isfile(filepath):
            _cache[name] = load_sampler_file(filepath)
        else:
            raise IOError("Sampler %s not found" % name)
    return _cache[name]


def load_all_samplers():
    """Load all Samplers."""
    samplers = {}
    for dirname in os.listdir(defines.samplerpath):
        filepath = os.path.join(defines.samplerpath, dirname, "info.py")
        exepath = os.path.join(defines.samplerpath, dirname, "sampler.x")
        if os.path.isfile(filepath) and os.path.isfile(exepath):
            try:
                samplers[dirname] = load_sampler_file(filepath)
            except:
                pass
    return samplers


def load_backend_file(filepath):
    """Load a backend from a file."""
    name = os.path.basename(filepath)[:-3]
    module = imp.load_source(name, filepath)
    return module.Backend()


def load_backend(name, _cache={}):
    """Load a backend."""
    if name not in _cache:
        filepath = os.path.join(defines.backendpath, name + ".py")
        if not os.path.isfile(filepath):
            raise IOError("Backend %s not found" % name)
        _cache[name] = load_backend_file(filepath)
    return _cache[name]


def load_all_backends():
    """Load all backends."""
    backends = {}
    for filename in os.listdir(defines.backendpath):
        if filename[-3:] != ".py":
            continue
        name = filename[:-3]
        filepath = os.path.join(defines.backendpath, filename)
        try:
            backends[name] = load_backend_file(filepath)
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
                              eval(fin.read(), {}))


def load_report(filepath, discard_first_repetitions=False):
    """Load a Report from a file."""
    with open(filepath) as fin:
        experiment = load_experiment_string(fin.readline())
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
    rep = report.Report(experiment, rawdata)
    if discard_first_repetitions:
        return rep.discard_first_repetitions()
    errfile = "%s.%s" % (filepath[:-4], defines.error_extension)
    if os.path.isfile(errfile) and os.path.getsize(errfile):
        rep.error = True
    return rep


def load_metric_file(filepath):
    """Load a metric from a file."""
    name = os.path.basename(filepath)[:-3]
    module = imp.load_source(name, filepath)
    metric = module.metric
    return metric


def load_metric(name, _cache={}):
    """Load a metric."""
    if name not in _cache:
        filepath = os.path.join(defines.metricpath, name + ".py")
        if os.path.isfile(filepath):
            _cache[name] = load_metric_file(filepath)
        else:
            raise IOError("Metric %s not found" % name)
    return _cache[name]


def load_all_metrics():
    """Load all metrics."""
    metrics = {}
    for filename in os.listdir(defines.metricpath):
        if filename[-3:] != ".py":
            continue
        filepath = os.path.join(defines.metricpath, filename)
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
