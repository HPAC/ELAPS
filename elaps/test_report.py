#!/usr/bin/env python
"""Unittest for report.py."""
from __future__ import division, print_function

from signature import *
from experiment import Experiment
from report import Report

import unittest
import random


class TestReportInit(unittest.TestCase):

    """Tests for Report initialization."""

    def setUp(self):
        self.ex = Experiment(sampler={
            "backend_header": "",
            "backend_prefix": "prefix{nt}",
            "backend_suffix": "",
            "backend_footer": "",
            "kernels": {},
            "nt_max": 10,
            "exe": "executable"
        })

    def test_simple(self):
        """Test for simple Experiment."""
        val = random.randint(1, 1000)
        start_time = random.randint(1, 1000)
        end_time  = random.randint(1, 1000)

        self.ex.call = Signature("name")()
        rawdata = [[start_time], [val], [end_time]]

        report = Report(self.ex, rawdata)
        self.assertEqual(report.starttime, start_time)
        self.assertEqual(report.endtime, end_time)
        self.assertEqual(report.fulldata, {None: ({None: ((val,),)},)})
        self.assertEqual(report.data, {None: ({None: {"rdtsc": val},
                                               0: {"rdtsc": val}},)})

    def test_range(self):
        """Test for Experiment with range."""
        lenrange = random.randint(1, 10)
        range_vals = [random.randint(1, 1000) for _ in range(lenrange)]
        vals = {range_val: random.randint(1, 1000) for range_val in range_vals}

        self.ex.call = Signature("name")()
        self.ex.range = ["i", range_vals]
        rawdata = ([[0]] + [[vals[range_val]] for range_val in range_vals] +
                   [[-1]])

        report = Report(self.ex, rawdata)
        self.assertEqual(len(report.fulldata), lenrange)
        idx = random.choice(range_vals)
        self.assertEqual(report.fulldata[idx][0][None][0][0], vals[idx])
        self.assertEqual(report.data[idx][0][0]["rdtsc"], vals[idx])


    def test_reps(self):
        """Test for Experiment with repetitions."""
        nreps = random.randint(1, 10)
        vals = [random.randint(1, 1000) for _ in range(nreps)]

        self.ex.call = Signature("name")()
        self.ex.nreps = nreps
        rawdata = [[0]] + [[val] for val in vals] + [[-1]]

        report = Report(self.ex, rawdata)
        self.assertEqual(len(report.fulldata[None]), nreps)
        idx = random.randint(0, nreps - 1)
        self.assertEqual(report.fulldata[None][idx][None][0][0], vals[idx])
        self.assertEqual(report.data[None][idx][None]["rdtsc"], vals[idx])

    def test_sumrange(self):
        """Test for Experiment with sumrange."""
        lenrange = random.randint(1, 10)
        range_vals = [random.randint(1, 1000) for _ in range(lenrange)]
        vals = {range_val: random.randint(1, 1000) for range_val in range_vals}

        self.ex.call = Signature("name")()
        self.ex.sumrange = ["i", range_vals]
        rawdata = ([[0]] + [[vals[range_val]] for range_val in range_vals] +
                   [[-1]])

        report = Report(self.ex, rawdata)
        self.assertEqual(len(report.fulldata[None][0]), lenrange)
        idx = random.choice(range_vals)
        self.assertEqual(report.fulldata[None][0][idx][0][0], vals[idx])
        self.assertEqual(report.data[None][0][None]["rdtsc"],
                         sum(vals.values()))

    def test_calls(self):
        """Test for Experiment multiple calls."""
        ncalls = random.randint(1, 10)
        vals = [random.randint(1, 1000) for _ in range(ncalls)]

        self.ex.calls = [Signature("name")() for _ in range(ncalls)]
        rawdata = [[0]] + [[val] for val in vals] + [[-1]]

        report = Report(self.ex, rawdata)
        self.assertEqual(len(report.fulldata[None][0][None]), ncalls)
        idx = random.randint(0, ncalls - 1)
        self.assertEqual(report.fulldata[None][0][None][idx][0], vals[idx])
        self.assertEqual(report.data[None][0][None]["rdtsc"], sum(vals))

    def test_counters(self):
        """Test for Experiment with counters."""
        ncounters = random.randint(1, 10)
        vals = [random.randint(1, 1000) for _ in range(ncounters + 1)]
        names = ["counter%d" % counterid for counterid in range(ncounters)]

        self.ex.call = Signature("name")()
        self.ex.papi_counters = names
        rawdata = [[0], vals, [1]]

        report = Report(self.ex, rawdata)
        self.assertEqual(len(report.fulldata[None][0][None][0]), 1 + ncounters)
        idx = random.randint(0, ncounters)
        self.assertEqual(report.fulldata[None][0][None][0][idx], vals[idx])
        idx = random.randint(0, ncounters - 1)
        name = names[idx]
        self.assertEqual(report.data[None][0][None][name], vals[1 + idx])

    def test_complexity(self):
        """Test for Call with complexity."""
        lenrange = random.randint(1, 10)
        lensumrange = random.randint(1, 10)

        self.ex.range = ["i", range(lenrange)]
        self.ex.sumrange = ["j", range(lensumrange)]
        sig = Signature("name", Dim("m"), Dim("n"), complexity="m * n")
        self.ex.call = sig(self.ex.ranges_parse("i"), self.ex.ranges_parse("j"))
        rawdata = [[0]] + lenrange * lensumrange * [[0]] + [[1]]

        report = Report(self.ex, rawdata)
        range_idx = random.randint(0, lenrange - 1)
        self.assertEqual(report.data[range_idx][0][0]["flops"],
                         range_idx * sum(i for i in range(lensumrange)))


if __name__ == "__main__":
    unittest.main()
