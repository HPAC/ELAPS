#!/usr/bin/env python
"""Result for an ELAPS:Experiment."""
from __future__ import division, print_function

import signature
from experiment import Experiment

from math import sqrt
from collections import Iterable
from copy import deepcopy

stat_funs = {
    "min": min,
    "med": lambda l: (sum(sorted(l)[((len(l) - 1) // 2):(len(l) // 2 + 1)]) /
                      (2 - len(l) % 2)),
    "max": max,
    "avg": lambda l: sum(l) / len(l),
    "std": lambda l: sqrt(max(sum(x ** 2 for x in l) / len(l) -
                              (sum(l) / len(l)) ** 2, 0)),
}


def apply_stat(stat_name, data):
    """Apply a statistic to the data."""
    if stat_name not in stat_funs:
        raise KeyError("unknown statistic %r" % stat_name)

    if isinstance(data, dict):
        # return a dict
        return dict((key, apply_stat(stat_name, values))
                    for key, values in data.items())

    if isinstance(data, Iterable):
        # apply to list
        return stat_funs[stat_name](list(data))

    # apply to single value
    return stat_funs[stat_name]([data])


class Report(object):

    """ELAPS:Report, result of an ELAPS:Experiment."""

    def __init__(self, experiment, rawdata):
        """Initialize report."""
        if not isinstance(experiment, Experiment):
            raise TypeError("first argument must be Experiment (not %s)" %
                            type(experiment).__name__)
        self.experiment = experiment
        try:
            self.rawdata = tuple(map(tuple, rawdata))
        except:
            raise TypeError("invalid rawdata format")
        self.fulldata_fromraw()
        self.data_fromfull()

    def fulldata_fromraw(self):
        """Initialize fulldata from rawdata."""
        self.error = False
        self.truncated = False
        ex = self.experiment
        rawdata = list(self.rawdata)

        def getints(data, count=1):
            try:
                values = data.pop(0)
            except:
                self.truncated = True
                return None
            try:
                if all(isinstance(value, int) for value in values):
                    if len(values) == count:
                        return tuple(values)
            except:
                pass
            self.error = True
            return getints(data, count)

        self.starttime = None
        values = getints(rawdata, 1)
        if values is not None:
            self.starttime = values[0]

        nvalues = len(ex.papi_counters) + 1

        # full structured data
        range_data = {}
        for range_val in ex.range_vals:
            # discard randomization results
            if ex.range_randomize_data:
                for name in ex.operands:
                    getints(data, 1)

            # results for each repetition
            rep_data = []
            for rep in range(ex.nreps):
                if ex.sumrange_parallel:
                    # only one result per repetition
                    values = getints(rawdata, nvalues)
                    if values:
                        rep_data.append(values)
                    continue
                # results for each sumrange iteration
                sumrange_data = {}
                for sumrange_val in ex.sumrange_vals_at(range_val):
                    if ex.calls_parallel:
                        # only one result per sumrange
                        values = getints(rawdata, nvalues)
                        if values:
                            sumrange_data[sumrange_val] = values
                        continue
                    # results for each call
                    call_data = []
                    for call in ex.calls:
                        # one result per call
                        values = getints(rawdata, nvalues)
                        if values:
                            call_data.append(values)
                    if call_data:
                        sumrange_data[sumrange_val] = tuple(call_data)
                if sumrange_data:
                    rep_data.append(sumrange_data)
            if rep_data:
                range_data[range_val] = tuple(rep_data)
        self.fulldata = range_data

        self.endtime = None
        values = getints(rawdata, 1)
        if values is not None:
            self.endtime = values[0]

    def data_fromfull(self):
        """Initialize data from fulldata."""
        ex = self.experiment

        # reduced data
        range_data = {}
        for range_val in ex.range_vals:

            if range_val not in self.fulldata:
                # missing full range_val data
                continue
            rep_fdata = self.fulldata[range_val]

            # results for each repetition
            # complextiy evaluation
            flops = len(ex.calls) * [0]
            for sumrange_val in ex.sumrange_vals_at(range_val):
                for callid, call in enumerate(ex.calls):
                    if not isinstance(call, signature.Call):
                        flops[callid] = None
                        continue
                    call_flops = next(ex.ranges_eval(
                        call.complexity(), range_val, sumrange_val
                    ))
                    if call_flops is None:
                        flops[callid] = None
                    else:
                        flops[callid] += call_flops
            if any(call_flops is None for call_flops in flops):
                totalflops = None
            else:
                totalflops = sum(flops)
            flops = dict(enumerate(flops))
            flops[None] = totalflops

            # get repetition data
            data_keys = map(intern, ["cycles"] + ex.papi_counters)
            nvalues = len(data_keys)
            rep_data = []
            for rep, sumrange_fdata in enumerate(rep_fdata):
                if ex.sumrange_parallel:
                    # only one result per repetition
                    tuple_data = {None: sumrange_fdata}
                elif ex.calls_parallel:
                    # only one result per sumrange iteration
                    sumrange_data = nvalues * [0]
                    for sumrange_val, calls_fdata in sumrange_fdata.items():
                        for id_ in range(nvalues):
                            sumrange_data[id_] += calls_fdata[id_]
                    tuple_data = {None: tuple(sumrange_data)}
                else:
                    # one result for each call
                    sumrange_data = [nvalues * [0] for call in ex.calls]
                    for sumrange_val, calls_fdata in sumrange_fdata.items():
                        for callid, call_fdata in enumerate(calls_fdata):
                            for id_ in range(nvalues):
                                sumrange_data[callid][id_] +=\
                                    call_fdata[id_]
                    tuple_data = dict(
                        (callid, tuple(sumrange_data[callid]))
                        for callid in range(len(ex.calls))
                    )
                    tuple_data[None] = tuple(
                        sum(sumrange_data[callid][id_]
                            for callid in range(len(ex.calls)))
                        for id_ in range(nvalues)
                    )
                dict_data = {}
                for callid in tuple_data:
                    dict_data[callid] = dict(zip(data_keys,
                                                 tuple_data[callid]))
                    if flops[callid] is not None:
                        dict_data[callid][intern("flops")] = flops[callid]
                rep_data.append(dict_data)

            range_data[range_val] = tuple(rep_data)
        self.data = range_data

        self.callids = self.data.values()[0][0].keys()

    def __repr__(self):
        """Python parsable representation."""
        return "%s(%r, %r)" % (type(self).__name__, self.experiment,
                               self.rawdata)

    def copy(self):
        """Generate a copy."""
        report = Report(self.experiment.copy(), deepcopy(self.rawdata))
        report.fulldata = deepcopy(self.fulldata)
        report.data = deepcopy(self.data)
        return report

    def apply_metric(self, metric, callid=None):
        """Evaluate data with respect to a metric."""
        ex = self.experiment
        result = {}
        for range_val in ex.range_vals:
            nthreads = ex.nthreads
            if ex.range and nthreads == ex.range[0]:
                nthreads = range_val
            if ex.sumrange_parallel:
                nthreads *= len(ex.sumrange_vals_at(range_val)) * len(ex.calls)
            elif ex.calls_parallel:
                nthreads *= len(ex.calls)
            nthreads = min(nthreads, ex.sampler["nt_max"])

            rep_result = []
            for rep in range(ex.nreps):
                try:
                    metric_val = metric(
                        self.data[range_val][rep][callid], experiment=ex,
                        callid=callid, nthreads=nthreads
                    )
                    if metric_val is not None:
                        rep_result.append(metric_val)
                except:
                    pass
            if rep_result:
                result[range_val] = rep_result
        return result

    def discard_first_repetitions(self):
        """Discard the first repetitions."""
        report = self.copy()
        fulldata = report.fulldata
        nreps = self.experiment.nreps
        if nreps > 1:
            for range_val in fulldata:
                if len(fulldata[range_val]) == nreps:
                    # do not take away more than 1
                    fulldata[range_val] = fulldata[range_val][1:]
        report.data_fromfull()
        return report
