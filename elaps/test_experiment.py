#!/usr/bin/env python
"""Unittest for experiment.py."""
from __future__ import division, print_function

from signature import *
from experiment import *

import unittest
import random


class TestExperiment(unittest.TestCase):

    """Tests for Experiment."""

    def test_init(self):
        """Test for __init__() and attribute access."""
        ex = Experiment(note="Test")
        self.assertEqual(ex["note"], "Test")
        self.assertEqual(ex.note, "Test")

    def test_setattr(self):
        """Test for __setattr__()."""
        ex = Experiment()

        with self.assertRaises(TypeError):
            ex.note = 1234
        with self.assertRaises(TypeError):
            ex.sampler = []
        with self.assertRaises(TypeError):
            ex.range = (1, 2, 3)
        with self.assertRaises(TypeError):
            ex.sumrange = (1, 2)

        ex.range = ("i", range(10))
        with self.assertRaises(TypeError):
            ex.nthreads = "j"
        ex.nthreads = "i"

        ex.sumrange_parallel = True
        self.assertTrue(ex.calls_parallel)

    def test_repr(self):
        """Test for __repr__()."""
        ex = Experiment(note="1234", range=("i", range(10)))
        self.assertEqual(eval(repr(ex)), ex)

    def test_data_update(self):
        """Test for data_update()."""
        sig = Signature("name", Dim("m"), Dim("n"),
                        cData("A", "ldA * n"), Ld("ldA", "m"))
        ex = Experiment(calls=[sig(100, 1000, "X", 2000)])

        self.assertRaises(KeyError, ex.data_update, "B")

        ex.data_update()

        self.assertDictContainsSubset({
            "size": 2000 * 1000,
            "type": cData,
            "dims": [100, 1000],
            "lds": [2000, 1000]
        }, ex.data["X"])

        # initial vary setup
        self.assertEqual(ex.data["X"]["vary"],
                         {"with": set(), "along": 0, "offset": 0})

        # vary is not touched
        ex.data["X"]["vary"]["with"].add("rep")
        ex.call.m = 500
        ex.data_update("X")

        self.assertIn("rep", ex.data["X"]["vary"]["with"])

    def test_infer_lds(self):
        """Test for infer_ld[s]()."""
        sig = Signature("name", Dim("m"), Dim("n"),
                        cData("A", "ldA * n"), Ld("ldA", "m"), Info())
        ex = Experiment(calls=[sig(100, 1000, "X", 2000, 0)])

        ex.infer_ld(0, 4)

        self.assertEqual(ex.call.ldA, 100)

        self.assertRaises(TypeError, ex.infer_ld, 0, 3)

        # now setting along and rep
        ex.nreps = 8
        ex.data["X"]["vary"]["along"] = 0
        ex.data["X"]["vary"]["with"].add("rep")

        ex.infer_lds()

        self.assertEqual(ex.call.ldA, 8 * 100)
        self.assertEqual(ex.data["X"]["lds"], [8 * 100, 1000])

        # range
        ex.sumrange = ("i", range(10))
        ex.data["X"]["vary"]["with"].add("i")

        ex.infer_lds()

        self.assertEqual(ex.call.ldA, 8 * 100 * 10)

    def test_infer_lwork(self):
        """Test for infer_lwork[s]()."""
        sig = Signature("name", Dim("m"), Dim("n"),
                        dWork("W", "lWork"), Lwork("lWork", "m * n"))
        ex = Experiment(calls=[sig(100, 1000, "V", 2000)])

        ex.infer_lwork(0, 4)

        self.assertEqual(ex.call.lWork, 100 * 1000)

    def test_apply_connections(self):
        """Test for apply_connections()."""
        sig = Signature("name", Dim("m"), Dim("n"),
                        iData("A", "m * n"), iData("B", "n * n"))
        call = sig(10, 20, "X", "Y")
        ex = Experiment(calls=[call.copy()])

        ex.apply_connections(0, 1)
        self.assertEqual(call, ex.calls[0])

        ex.calls[0].B = "X"
        ex.apply_connections(0, 2)
        self.assertNotEqual(call, ex.calls[0])
        self.assertEqual(ex.calls[0][1], 20)

        # two calls
        ex.calls = [sig(10, 20, "X", "Y"), sig(30, 40, "Z", "X")]

        ex.apply_connections(1, 2)

        self.assertEqual(ex.calls[0].m, ex.calls[1][2])
        self.assertEqual(ex.calls[0].n, ex.calls[1][2])

        # acces .call as an attribute when only one call
        with self.assertRaises(AttributeError):
            ex.call

        with self.assertRaises(AttributeError):
            ex.calls = []
            print(ex.call)

    def test_check_sanity(self):
        """test for check_sanity()."""
        pass

    def test_submit_prepare(self):
        """test for generate_cmds()."""
        pass


if __name__ == "__main__":
    unittest.main()
