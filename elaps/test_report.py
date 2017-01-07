#!/usr/bin/env python
"""Unittest for report.py."""

import random
import unittest

try:
    import elaps
except:
    import os
    import sys
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

from elaps.signature import *
from elaps.experiment import Experiment
from elaps.report import Report


class TestReport(unittest.TestCase):

    """Tests for Report."""

    def setUp(self):
        """Set up Sampler for Experiment."""
        self.ex = Experiment(sampler={
            "backend_name": "",
            "backend_header": "",
            "backend_prefix": "prefix{nt}",
            "backend_suffix": "",
            "backend_footer": "",
            "kernels": {},
            "nt_max": 10,
            "exe": "executable"
        })
        self.i = symbolic.Symbol("i")
        self.j = symbolic.Symbol("j")

    def test_simple(self):
        """Test for simple Experiment."""
        ex = self.ex

        val = random.randint(1, 1000)
        start_time = random.randint(1, 1000)
        end_time = random.randint(1, 1000)

        ex.call = Signature("name")()
        rawdata = [[start_time], [val], [end_time]]

        report = Report(ex, rawdata)
        self.assertEqual(report.starttime, start_time)
        self.assertEqual(report.endtime, end_time)
        self.assertEqual(report.fulldata, {None: ({None: ((val,),)},)})
        self.assertEqual(report.data, {None: (({"cycles": val},),)})

        rawdata = [[0], [1]]
        report = Report(ex, rawdata)
        self.assertTrue(report.truncated)

    def test_range(self):
        """Test for Experiment with range."""
        ex, i = self.ex, self.i

        lenrange = random.randint(1, 10)
        range_vals = random.sample(range(1000), lenrange)
        vals = dict((range_val, random.randint(1, 1000))
                    for range_val in range_vals)

        ex.call = Signature("name")()
        ex.range = [i, range_vals]
        rawdata = ([[0]] + [[vals[range_val]] for range_val in range_vals] +
                   [[-1]])

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata), lenrange)
        idx = random.choice(range_vals)
        self.assertEqual(report.fulldata[idx][0][None][0][0], vals[idx])
        self.assertEqual(report.data[idx][0][0]["cycles"], vals[idx])

    def test_reps(self):
        """Test for Experiment with repetitions."""
        ex = self.ex

        nreps = random.randint(1, 10)
        vals = [random.randint(1, 1000) for _ in range(nreps)]

        ex.call = Signature("name")()
        ex.nreps = nreps
        rawdata = [[0]] + [[val] for val in vals] + [[-1]]

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata[None]), nreps)
        idx = random.randint(0, nreps - 1)
        self.assertEqual(report.fulldata[None][idx][None][0][0], vals[idx])
        self.assertEqual(report.data[None][idx][0]["cycles"], vals[idx])

    def test_noshuffle(self):
        """Test for Experiment without and without shuffling."""
        ex, i = self.ex, self.i

        lenrange = random.randint(1, 10)
        range_vals = random.sample(range(1000), lenrange)
        nreps = random.randint(1, 10)
        vals = dict((range_val,
                     [random.randint(1, 1000) for _ in range(nreps)]) for
                    range_val in range_vals)

        ex.call = Signature("name")()
        ex.range = [i, range_vals]
        ex.nreps = nreps
        rawdata = [[0]] + [[val] for range_val in range_vals
                           for val in vals[range_val]] + [[-1]]

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata), lenrange)
        self.assertEqual(len(report.fulldata[range_vals[0]]), nreps)

        rangeidx = random.choice(range_vals)
        repidx = random.randint(0, nreps - 1)
        self.assertEqual(report.fulldata[rangeidx][repidx][None][0][0],
                         vals[rangeidx][repidx])
        self.assertEqual(report.data[rangeidx][repidx][0]["cycles"],
                         vals[rangeidx][repidx])

    def test_shuffle(self):
        """Test for Experiment without and with shuffling."""
        ex, i = self.ex, self.i

        lenrange = random.randint(1, 10)
        range_vals = random.sample(range(1000), lenrange)
        nreps = random.randint(1, 10)
        vals = dict((range_val,
                     [random.randint(1, 1000) for _ in range(nreps)]) for
                    range_val in range_vals)

        ex.call = Signature("name")()
        ex.range = [i, range_vals]
        ex.nreps = nreps
        ex.shuffle = True
        rawdata = [[0]] + [[vals[range_val][rep]] for rep in range(nreps)
                           for range_val in range_vals] + [[-1]]

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata), lenrange)
        self.assertEqual(len(report.fulldata[range_vals[0]]), nreps)

        rangeidx = random.choice(range_vals)
        repidx = random.randint(0, nreps - 1)
        self.assertEqual(report.fulldata[rangeidx][repidx][None][0][0],
                         vals[rangeidx][repidx])
        self.assertEqual(report.data[rangeidx][repidx][0]["cycles"],
                         vals[rangeidx][repidx])

    def test_sumrange(self):
        """Test for Experiment with sumrange."""
        ex, i = self.ex, self.i

        lenrange = random.randint(1, 10)
        range_vals = random.sample(range(1000), lenrange)
        vals = dict((range_val, random.randint(1, 1000))
                    for range_val in range_vals)

        ex.call = Signature("name")()
        ex.sumrange = [i, range_vals]
        rawdata = ([[0]] + [[vals[range_val]] for range_val in range_vals] +
                   [[-1]])

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata[None][0]), lenrange)
        idx = random.choice(range_vals)
        self.assertEqual(report.fulldata[None][0][idx][0][0], vals[idx])
        self.assertEqual(report.data[None][0][0]["cycles"], sum(vals.values()))

    def test_sumrange_parallel(self):
        """Test for Experiment with parallel sumrange."""
        ex, i = self.ex, self.i

        lenrange = random.randint(1, 10)
        range_vals = [random.randint(1, 1000) for _ in range(lenrange)]
        val = random.randint(1, 1000)

        ex.call = Signature("name")()
        ex.sumrange = [i, range_vals]
        ex.sumrange_parallel = True
        rawdata = [[0], [val], [-1]]

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata[None][0]), 1)
        self.assertEqual(report.fulldata[None][0][0], val)
        self.assertEqual(report.data[None][0]["cycles"], val)

    def test_calls(self):
        """Test for Experiment multiple calls."""
        ex = self.ex

        ncalls = random.randint(1, 10)
        vals = [random.randint(1, 1000) for _ in range(ncalls)]

        ex.calls = [Signature("name")() for _ in range(ncalls)]
        rawdata = [[0]] + [[val] for val in vals] + [[-1]]

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata[None][0][None]), ncalls)
        idx = random.randint(0, ncalls - 1)
        self.assertEqual(report.fulldata[None][0][None][idx][0], vals[idx])

    def test_calls_parallel(self):
        """Test for Experiment parallel calls."""
        ex = self.ex

        ncalls = random.randint(1, 10)
        val = random.randint(1, 1000)

        ex.calls = [Signature("name")() for _ in range(ncalls)]
        ex.calls_parallel = True
        rawdata = [[0], [val], [-1]]

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata[None][0][None]), 1)
        self.assertEqual(report.fulldata[None][0][None][0], val)
        self.assertEqual(report.data[None][0]["cycles"], val)

    def test_counters(self):
        """Test for Experiment with counters."""
        ex = self.ex

        ncounters = random.randint(1, 10)
        vals = [random.randint(1, 1000) for _ in range(ncounters + 1)]
        names = ["counter%d" % counterid for counterid in range(ncounters)]

        ex.call = Signature("name")()
        ex.papi_counters = names
        rawdata = [[0], vals, [1]]

        report = Report(ex, rawdata)
        self.assertEqual(len(report.fulldata[None][0][None][0]), 1 + ncounters)
        idx = random.randint(0, ncounters)
        self.assertEqual(report.fulldata[None][0][None][0][idx], vals[idx])
        idx = random.randint(0, ncounters - 1)
        name = names[idx]
        self.assertEqual(report.data[None][0][0][name], vals[1 + idx])

    def test_flops(self):
        """Test for Call with flops."""
        ex, i, j = self.ex, self.i, self.j

        lenrange = random.randint(1, 10)
        lensumrange = random.randint(1, 10)

        ex.range = [i, range(lenrange)]
        ex.sumrange = [j, range(lensumrange)]
        sig = Signature("name", Dim("m"), Dim("n"), flops="m * n")
        ex.call = sig(i, j)
        rawdata = [[0]] + lenrange * lensumrange * [[0]] + [[1]]

        report = Report(ex, rawdata)
        range_idx = random.randint(0, lenrange - 1)
        self.assertEqual(report.data[range_idx][0][0]["flops"],
                         range_idx * sum(i for i in range(lensumrange)))

    def test_evaluate(self):
        """Test for evaluate()."""
        ex = self.ex

        val = random.randint(1, 1000)

        ex.call = Signature("name")()
        rawdata = [[0], [val], [1]]

        def metric(data, **kwargs):
            return data.get("cycles")

        report = Report(ex, rawdata)
        metricdata = report.evaluate(0, metric)
        self.assertEqual(metricdata, {None: [val]})

        # parallel
        ex.sumrange_parallel = True
        report = Report(ex, rawdata)
        metricdata = report.evaluate(None, metric)
        self.assertEqual(metricdata, {None: [val]})

    def test_discrard_frist_repetitions(self):
        """Test discard_first_repetitions()."""
        ex = self.ex

        nreps = random.randint(2, 10)
        vals = [random.randint(1, 1000) for _ in range(nreps)]

        ex.call = Signature("name")()
        ex.nreps = nreps
        rawdata = [[0]] + [[val] for val in vals] + [[1]]

        report = Report(ex, rawdata)

        report2 = report.discard_first_repetitions()
        self.assertEqual(report2.experiment, ex)
        self.assertEqual(report2.rawdata, report.rawdata)
        self.assertEqual(len(report2.fulldata[None]), nreps - 1)

if __name__ == "__main__":
    unittest.main()
