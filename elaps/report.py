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
    None: lambda l: l
}


def apply_stat(stat, data):
    """Apply a statistic to the data."""
    if stat in stat_funs:
        # named
        stat = stat_funs[stat]
    elif hasattr(stat, "__call__"):
        # function
        pass
    else:
        # unknown
        raise Exception("stat is of unknown format")

    if isinstance(data, dict):
        # return a dict
        return dict((key, apply_stat(stat, values))
                    for key, values in data.items())

    if isinstance(data, Iterable):
        # apply to list
        return stat(list(data))

    # apply to single value
    return stat([data])


class Report(object):

    """ELAPS:Report, result of an ELAPS:Experiment."""

    def __init__(self, experiment, rawdata, fulldata=None, data=None):
        """Initialize report."""
        if not isinstance(experiment, Experiment):
            raise TypeError("first argument must be Experiment (not %s)" %
                            type(experiment).__name__)
        self.experiment = experiment
        self.first_repetitions_discarded = None
        try:
            self.rawdata = tuple(map(tuple, rawdata))
        except:
            raise TypeError("invalid rawdata format")
        if fulldata:
            self.fulldata = fulldata
        else:
            self.fulldata_fromraw()
        if data:
            self.data = data
        else:
            self.data_fromfull()

    def fulldata_fromraw(self):
        """Initialize fulldata from rawdata.

        Structure of fulldata (no parallelism):
         -> dict[range_value | None]
         -> tuple[rep]
         -> dict[sumrange_value | None]
         -> tuple[callid]
         -> tuple[counterid]

        Structure of fulldata (calls_parallel):
         -> dict[range_value | None]
         -> tuple[rep]
         -> dict[sumrange_value | None]
         -> tuple[counterid]

        Structure of fulldata (sumrange_parallel):
         -> dict[range_value | None]
         -> tuple[rep]
         -> tuple[counterid]
        """
        ex = self.experiment
        self.error = False
        self.truncated = False

        def getints(count, iterator=iter(self.rawdata)):
            try:
                values = iterator.next()
            except:
                self.truncated = True
                return None
            try:
                if (all(isinstance(value, int) for value in values) and
                        len(values) == count):
                    return tuple(values)
            except:
                pass
            self.error = True
            return getints(count)

        self.starttime = None
        values = getints(1)
        if values is not None:
            self.starttime = values[0]

        nvalues = len(ex.papi_counters) + 1

        # full structured data
        self.fulldata = {}
        for range_val in ex.range_vals:
            # results for each repetition
            range_val_fdata = []
            for rep in range(ex.nreps):
                if ex.sumrange_parallel:
                    # only one result per repetition
                    values = getints(nvalues)
                    if values:
                        range_val_fdata.append(values)
                    continue

                # results for each sumrange iteration
                rep_fdata = {}
                for sumrange_val in ex.sumrange_vals_at(range_val):
                    if ex.calls_parallel:
                        # only one result per sumrange
                        values = getints(nvalues)
                        if values:
                            rep_fdata[sumrange_val] = values
                        continue

                    # results for each call
                    sumrange_val_fdata = []
                    for call in ex.calls:
                        # one result per call
                        values = getints(nvalues)
                        if values:
                            sumrange_val_fdata.append(values)
                    if sumrange_val_fdata:
                        rep_fdata[sumrange_val] = tuple(sumrange_val_fdata)
                if rep_fdata:
                    range_val_fdata.append(rep_fdata)
            if range_val_fdata:
                self.fulldata[range_val] = tuple(range_val_fdata)

        self.endtime = None
        values = getints(1)
        if values is not None:
            self.endtime = values[0]

    def data_fromfull(self):
        """Initialize data from fulldata.

        Structure of data (no parallelism):
         -> dict[range_val]
         -> tuple[rep]
         -> list[call]
         -> dict[counter]

        Structure of data (calls_parallel or sumrange_parallel):
         -> dict[range_val]
         -> tuple[rep]
         -> dict[counter]
        """
        ex = self.experiment
        counters = map(intern, ["cycles"] + ex.papi_counters)

        # reduced data
        self.data = {}
        for range_val in ex.range_vals:
            # results for each range value
            if range_val not in self.fulldata:
                # missing full range_val data
                continue
            range_val_fdata = self.fulldata[range_val]

            # flops evaluation
            flops = len(ex.calls) * [0]
            for sumrange_val in ex.sumrange_vals_at(range_val):
                for callid, call in enumerate(ex.calls):
                    if flops[callid] is None:
                        continue
                    if not isinstance(call, signature.Call):
                        flops[callid] = None
                        continue
                    call_flops = next(ex.ranges_eval(
                        call.flops(), range_val, sumrange_val
                    ))
                    if call_flops is None:
                        flops[callid] = None
                    else:
                        flops[callid] += call_flops

            # get repetition data
            range_val_data = []
            for rep, rep_fdata in enumerate(range_val_fdata):
                # results for each repetition
                if ex.sumrange_parallel:
                    # one result per repetition
                    rep_data = dict(zip(counters, rep_fdata))
                    if all(f is not None for f in flops):
                        rep_data[intern("flops")] = sum(flops)
                elif ex.calls_parallel:
                    # one result per sumrange iteration
                    rep_data = dict(zip(counters,
                                        map(sum, zip(*rep_fdata.values())))
                                    )
                    if all(f is not None for f in flops):
                        rep_data[intern("flops")] = sum(flops)
                else:
                    # one result per call
                    rep_data = tuple({c: 0 for c in counters}
                                     for call in ex.calls)
                    for sumrange_val_fdata in rep_fdata.values():
                        for callid, call_fdata in enumerate(
                            sumrange_val_fdata
                        ):
                            for counter, val in zip(counters, call_fdata):
                                rep_data[callid][counter] += val
                    for callid in range(len(ex.calls)):
                        if flops[callid] is not None:
                            rep_data[callid][intern("flops")] = flops[callid]
                range_val_data.append(rep_data)
            self.data[range_val] = tuple(range_val_data)

    def __repr__(self):
        """Python parsable representation."""
        return "%s(%r, %r)" % (type(self).__name__, self.experiment,
                               self.rawdata)

    def copy(self):
        """Generate a copy."""
        return Report(self.experiment, self.rawdata, self.fulldata, self.data)

    def evaluate(self, callselector, metric, stat=None):
        """Evaluate the report."""
        ex = self.experiment

        # set selector from callselector
        if callselector is None:
            # all calls
            if ex.sumrange_parallel or ex.calls_parallel:
                def callselector(x):
                    return x
            else:
                callselector = range(len(ex.calls))
        elif isinstance(callselector, int):
            # callid
            callselector = [callselector]
        if isinstance(callselector, list):
            # list of callids
            def selector(data):
                return sum(data[v] for v in callselector)
        elif hasattr(callselector, "__call__"):
            # function
            selector = callselector
        else:
            # unknown
            raise Exception("callselector is of unknown format")

        # set stat
        if stat in stat_funs:
            # named stat
            stat = stat_funs[stat]
        elif hasattr(stat, "__call__"):
            # function
            pass
        else:
            # unknown
            raise Exception("stat is of unknown format")

        result = {}
        for range_val, range_val_data in self.data.items():
            range_val_result = []

            # set up nthreads
            nthreads = ex.nthreads
            if ex.range and nthreads == ex.range[0]:
                nthreads = range_val
            if ex.sumrange_parallel:
                nthreads *= len(ex.sumrange_vals_at(range_val)) * len(ex.calls)
            elif ex.calls_parallel:
                nthreads *= len(ex.calls)
            nthreads = min(nthreads, ex.sampler["nt_max"])

            # compute results
            for rep, rep_data in enumerate(range_val_data):
                if not (ex.sumrange_parallel or ex.calls_parallel):
                    # transpose rep_data
                    rep_data = {k: [call_data[k] if k in call_data else None
                                    for call_data in rep_data]
                                for k in rep_data[0]}
                try:
                    selector_data = {k: selector(v)
                                     for k, v in rep_data.items()}
                    metric_val = metric(
                        selector_data, experiment=ex, selector=selector,
                        nthreads=nthreads
                    )
                except:
                    continue
                if metric_val is not None:
                    range_val_result.append(metric_val)
            if range_val_result:
                result[range_val] = stat(range_val_result)
        return result

    def discard_first_repetitions(self):
        """Discard the first repetitions."""
        if self.first_repetitions_discarded:
            return self.first_repetitions_discarded
        report = self.copy()
        nreps = self.experiment.nreps
        if nreps > 1:
            fulldata = {}
            for range_val, range_val_data in self.fulldata.iteritems():
                if len(range_val_data) > 1:
                    # do not take away last one
                    range_val_data = range_val_data[1:]
                fulldata[range_val] = range_val_data
            report.fulldata = fulldata
            report.data_fromfull()
        self.first_repetitions_discarded = report
        return report
