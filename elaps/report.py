#!/usr/bin/env python
"""Result for an ELAPS:Experiment."""
from __future__ import division, print_function

import symbolic
import signature


class Report(object):

    """ELAPS:Report, result of an ELAPS:Experiment."""

    def __init__(self, experiment, rawdata):
        """Initialize report."""
        self.experiment = experiment
        self.rawdata = tuple(map(tuple, rawdata))

        if len(rawdata) != experiment.nresults() + 2:
            raise Exception("Unexpected #results: %d (expecting %d)" %
                            (len(rawdata) - 2, experiment.nresults()))

        self.process_rawdata()

    def process_rawdata(self):
        """Initialize data."""
        ex = self.experiment
        rawdata = list(self.rawdata)
        self.starttime = rawdata.pop(0)[0]
        self.endtime = rawdata.pop()[0]

        # full structured data
        range_data = {}
        for range_val in ex.range_vals():
            # results for each repetition
            rep_data = []
            for rep in range(ex.nreps):
                if ex.sumrange_parallel:
                    # only one result per repetition
                    rep_data.append(tuple(rawdata.pop(0)))
                    continue
                # results for each sumrange iteration
                sumrange_data = {}
                for sumrange_val in ex.sumrange_vals(range_val):
                    if ex.calls_parallel:
                        # only one result per sumrange
                        sumrange_data[sumrange_val] = tuple(rawdata.pop(0))
                        continue
                    # results for each call
                    call_data = []
                    for call in ex.calls:
                        # one result per call
                        call_data.append(rawdata.pop(0))
                    sumrange_data[sumrange_val] = tuple(call_data)
                rep_data.append(sumrange_data)
            range_data[range_val] = tuple(rep_data)
        self.fulldata = range_data

        # reduced data
        range_data = {}
        for range_val in ex.range_vals():
            rep_fulldata = self.fulldata[range_val]
            # results for each repetition
            # complextiy evaluation
            flops = len(ex.calls) * [0]
            for sumrange_val in ex.sumrange_vals(range_val):
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
            flops = {key: val for key, val in enumerate(flops)}
            flops[None] = totalflops

            # get repetition data
            data_keys = map(intern, ["rdtsc"] + ex.papi_counters)
            rep_data = []
            for rep in range(ex.nreps):
                sumrange_fulldata = rep_fulldata[rep]
                if ex.sumrange_parallel:
                    # only one result per repetition
                    tuple_data = {None: sumrange_fulldata}
                elif ex.calls_parallel:
                    # only one result per sumrange iteration
                    sumrange_data = (1 + len(ex.papi_counters)) * [0]
                    for sumrange_val in ex.sumrange_vals(range_val):
                        calls_fulldata = sumrange_fulldata[sumrange_val]
                        for id_ in range(1 + len(ex.papi_counters)):
                            sumrange_data[id_] += calls_fulldata[id_]
                    tuple_data = {None: tuple(sumrange_data)}
                else:
                    # one result for each call
                    sumrange_data = [(1 + len(ex.papi_counters)) * [0]
                                     for call in ex.calls]
                    for sumrange_val in ex.sumrange_vals(range_val):
                        calls_fulldata = sumrange_fulldata[sumrange_val]
                        for callid in range(len(ex.calls)):
                            call_fulldata = calls_fulldata[callid]
                            for id_ in range(1 + len(ex.papi_counters)):
                                sumrange_data[callid][id_] +=\
                                    call_fulldata[id_]
                    tuple_data = {
                        callid: tuple(sumrange_data[callid])
                        for callid in range(len(ex.calls))
                    }
                    tuple_data[None] = tuple(
                        sum(sumrange_data[callid][id_]
                            for callid in range(len(ex.calls)))
                        for id_ in range(1 + len(ex.papi_counters))
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

    def apply_metric(self, metric):
        """Evaluate data with respect to a metric."""
        ex = self.experiment
        result = {}
        for range_val in ex.range_vals():
            nthreads = ex.nthreads
            if isinstance(ex.nthreads, str):
                nthreads = range_val
            if ex.sumrange_parallel:
                nthreads *= len(ex.sumrange_vals(range_val)) * len(ex.calls)
            elif ex.calls_parallel:
                nthreads *= len(ex.calls)
            nthreads = min(nthreads, ex.sampler["nt_max"])
            rep_result = []
            for rep in range(ex.nreps):
                calls_data = self.data[range_val][rep]
                calls_result = {}
                for callid, value in calls_data.items:
                    try:
                        call_results[callid] = metric(
                            value, experiment=ex, callid=callid,
                            nthreads=nthreads
                        )
                    except:
                        pass
                rep_results.append(calls_result)
            result[range_val] = rep_result
        return result

    def __repr__(self):
        """Python parsable representation."""
        return "%s(%r, %r)" % (type(self).__name__, self.experiment,
                               self.rawdata)
