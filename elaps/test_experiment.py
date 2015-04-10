#!/usr/bin/env python
"""Unittest for experiment.py."""
from __future__ import division, print_function

from signature import *
import symbolic
from experiment import *

import unittest
import random
import os
import glob


class TestExperiment(unittest.TestCase):

    """Tests for Experiment."""

    def setUp(self):
        """Set up an empty sampler."""
        self.sampler = {
            "backend_name": "",
            "backend_header": "",
            "backend_prefix": "",
            "backend_suffix": "",
            "backend_footer": "",
            "kernels": {},
            "nt_max": random.randint(1, 10),
            "exe": "x"
        }

    def test_init(self):
        """Test for __init__() and attribute access."""
        ex = Experiment(note="Test")
        self.assertEqual(ex["note"], "Test")
        self.assertEqual(ex.note, "Test")

    def test_repr(self):
        """Test for __repr__()."""
        ex = Experiment(note="1234", range=("i", range(10)))
        self.assertEqual(eval(repr(ex)), ex)

    def test_update_data(self):
        """Test for update_data()."""
        sig = Signature("name", Dim("m"), Dim("n"),
                        cData("A", "ldA * n"), Ld("ldA", "m"))
        ex = Experiment(calls=[sig(100, 1000, "X", 2000)])

        self.assertRaises(KeyError, ex.update_data, "B")

        ex.update_data()

        self.assertDictContainsSubset({
            "size": 2000 * 1000,
            "type": cData,
            "dims": [100, 1000],
            "lds": [2000, 1000]
        }, ex.data["X"])

        # initial vary setup
        self.assertEqual(ex.data["X"]["vary"],
                         {"with": set(), "along": 1, "offset": 0})

        # vary is not touched
        ex.data["X"]["vary"]["with"].add("rep")
        ex.call.m = 500
        ex.update_data("X")

        self.assertIn("rep", ex.data["X"]["vary"]["with"])

        ex.call.A = None
        ex.update_data()

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
        ex.sumrange = ["i", range(10)]
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

    def test_vary_set(self):
        """Test for vary_set()."""
        sig = Signature("name", Dim("m"), Dim("n"),
                        iData("A", "m * n"), iData("B", "n * n"))
        ex = Experiment()
        ex.call = sig(10, 20, "X", "Y")
        ex.range = ["i", range(random.randint(1, 10))]
        ex.update_data()
        ex.vary_set("X", offset="10 * i")

        self.assertEqual(ex.data["X"]["vary"]["offset"], 10 *
                         symbolic.Symbol("i"))

    def test_check_arg_value(self):
        """test for check_arg_value()."""
        ex = Experiment(
            sampler=self.sampler,
            calls=[Signature("name", Dim("m"))(5)]
        )
        ex.call[0] = "name2"
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.call[0] = "name"
        ex.call.append(6)
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.call.pop()
        ex.call[-1] = None
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.call[-1] = 100
        ex.check_sanity(True)

    def test_check_sanity(self):
        """test for check_sanity()."""
        ex = Experiment(
            sampler=self.sampler,
            calls=[Signature("name", Dim("m"))(5)]
        )
        ex.update_data()
        ex.check_sanity(True)
        self.assertTrue(ex.check_sanity())

        # instance checking
        ex.note = 1
        self.assertRaises(TypeError, ex.check_sanity, True)
        self.assertFalse(ex.check_sanity())
        ex.note = ""

        # sampler
        del self.sampler["exe"]
        self.assertRaises(KeyError, ex.check_sanity, True)
        self.sampler["exe"] = "x"

        # ranges
        ex.range = ["i", [1, 2], 3]
        self.assertRaises(TypeError, ex.check_sanity, True)
        ex.range = [1, [1, 2]]
        self.assertRaises(TypeError, ex.check_sanity, True)
        ex.range = None
        ex.range = ["i", 1]
        self.assertRaises(TypeError, ex.check_sanity, True)
        ex.range = ["j", range(random.randint(1, 10))]
        ex.sumrange = ["j", [1, 2]]
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.range = ["i", [1, 2, 3]]
        ex.sumrange = ["j", [symbolic.Symbol("k"), 2]]
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.sumrange = ["j", [symbolic.Symbol("i"), 2]]
        ex.check_sanity(True)
        ex.sumrange = None

        # threads
        ex.nthreads = ex.sampler["nt_max"] + random.randint(1, 10)
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.nthreads = "k"
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.range = ["k", [1, 2]]
        ex.check_sanity(True)

        # calls
        ex.calls = []
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.call = ["name", 5]
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.call = BasicCall(("name", "int *"), 5)
        self.assertTrue(ex.check_sanity(True))

        # symbols
        ex.call[1] = symbolic.Symbol("a")
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.call[1] = symbolic.Symbol("k")
        ex.check_sanity(True)

        # data
        sig = Signature("name", Dim("m"), Dim("n"),
                        sData("A", "ldA * n"), Ld("ldA", "m"),
                        dData("B", "ldB * m"), Ld("ldB", "m"),
                        cData("C", "ldC * n"), Ld("ldC", "n"))
        ex.call = sig(2, 3, "X", 4, "Y", 5, "Z", 6)
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.update_data()
        ex.check_sanity(True)

        # vary
        ex.data["X"]["vary"]["with"].add("a")
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.data["X"]["vary"]["with"] = set("k")
        ex.data["X"]["vary"]["along"] = 2
        self.assertRaises(IndexError, ex.check_sanity, True)
        ex.data["X"]["vary"]["along"] = 1
        ex.data["X"]["vary"]["offset"] = symbolic.Symbol("a")
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.data["X"]["vary"]["offset"] = 10


class TestExperimentCmds(unittest.TestCase):

    """Tests for Experiment.generate_cmds()."""

    def setUp(self):
        """Set up a signature and experiment with call."""
        self.m = random.randint(1, 100)
        self.n = random.randint(1, 100)
        self.sig = Signature("name", Dim("m"), Dim("n"),
                             sData("A", "ldA * n"), Ld("ldA", "m"),
                             dData("B", "ldB * m"), Ld("ldB", "m"),
                             cData("C", "ldC * n"), Ld("ldC", "n"))
        self.ex = Experiment()
        self.ex.calls = [self.sig(self.m, self.n,
                                  "X", None, "Y", None, "Z", None)]
        self.ex.infer_lds()
        self.ex.update_data()

    def test_cmd_order(self):
        """Test for generate_cmds()."""
        self.ex.call.ldA = ldA = random.randint(100, 200)
        self.ex.call.ldB = ldB = random.randint(100, 200)
        self.ex.call.ldC = ldC = random.randint(100, 200)
        cmds = self.ex.generate_cmds()
        cmds = [cmd for cmd in cmds if cmd and cmd[0][0] != "#"]
        self.assertEqual(cmds, [
            ["smalloc", "X", ldA * self.n],
            ["dmalloc", "Y", ldB * self.m],
            ["cmalloc", "Z", ldC * self.n],
            ["name", self.m, self.n, "X", ldA, "Y", ldB, "Z", ldC],
            ["go"]
        ])

    def test_data_norange(self):
        """Test data commands without range."""
        nreps = random.randint(1, 10)
        lensumrange = random.randint(1, 10)

        self.ex.nreps = nreps
        self.ex.sumrange = ["j", range(lensumrange)]
        self.ex.data["X"]["vary"]["with"].add("rep")
        self.ex.data["Y"]["vary"]["with"].add("j")
        self.ex.data["Y"]["vary"]["along"] = 0
        self.ex.data["Z"]["vary"]["with"].update(["rep", "j"])
        self.ex.infer_lds()

        cmds = self.ex.generate_cmds()

        self.assertIn(["smalloc", "X",
                       nreps * self.m * self.n], cmds)
        idx = random.randint(0, nreps - 1)
        self.assertIn(["soffset", "X", idx * self.m * self.n, "X_%d" % idx],
                      cmds)

        self.assertIn([
            "dmalloc", "Y",
            lensumrange * self.m * self.m + (lensumrange - 1) * self.m
        ], cmds)
        idx = random.randint(0, lensumrange - 1)
        self.assertIn(["doffset", "Y", idx * self.m, "Y_%d" % idx], cmds)

        self.assertIn(["cmalloc", "Z", nreps * lensumrange * self.n * self.n],
                      cmds)
        idxrep = random.randint(0, nreps - 1)
        idxrange = random.randint(0, lensumrange - 1)
        self.assertIn(["coffset", "Z",
                       (idxrep * lensumrange + idxrange) * self.n * self.n,
                       "Z_%d_%d" % (idxrep, idxrange)], cmds)

    def test_data_range(self):
        """Test data commands when range is set."""
        lenrange = random.randint(1, 10)
        nreps = random.randint(1, 10)

        self.ex.range = ["i", range(lenrange)]
        self.ex.nreps = nreps

        self.ex.data["X"]["vary"]["along"] = 0
        self.ex.data["X"]["vary"]["with"].add("rep")
        self.ex.infer_lds()

        cmds = self.ex.generate_cmds()

        self.assertIn(["smalloc", "X",
                       nreps * self.m * self.n + (nreps - 1) * self.m], cmds)
        rangeidx = random.randint(0, lenrange - 1)
        repidx = random.randint(0, nreps - 1)
        self.assertIn(["soffset", "X", repidx * self.m,
                       "X_%d_%d" % (rangeidx, repidx)], cmds)

    def test_data_dep(self):
        """Test data commands with depedencies in data."""
        lenrange = random.randint(1, 10)
        lensumrange = random.randint(1, 10)
        self.ex.range = ["i", range(lenrange)]
        self.ex.sumrange = ["j", range(lensumrange)]
        self.ex.call.m = self.ex.ranges_parse("j")
        self.ex.data["X"]["vary"]["with"].add("j")

        self.ex.infer_lds()

        cmds = self.ex.generate_cmds()

        rangeidx = random.randint(0, lenrange - 1)
        sumrangeidx = random.randint(0, lensumrange - 1)
        offset = sum(self.n * j for j in range(sumrangeidx))
        self.assertIn(["soffset", "X", offset,
                       "X_%d_%d" % (rangeidx, sumrangeidx)], cmds)

    def test_data_along(self):
        """Test along = 1."""
        nreps = random.randint(1, 10)
        self.ex.nreps = nreps
        self.ex.data["X"]["vary"]["with"].add("rep")
        self.ex.data["X"]["vary"]["along"] = 1
        self.ex.infer_lds()

        cmds = self.ex.generate_cmds()

        self.assertIn(["smalloc", "X", nreps * self.m * self.n], cmds)
        repidx = random.randint(0, nreps - 1)
        self.assertIn(["soffset", "X", repidx * self.m * self.n,
                       "X_%d" % repidx], cmds)

    def test_data_offset(self):
        """Test offset."""
        nreps = random.randint(1, 10)
        self.ex.nreps = nreps
        self.ex.data["X"]["vary"]["with"].add("rep")
        offset = random.randint(1, 100)
        self.ex.data["X"]["vary"]["offset"] = offset
        self.ex.infer_lds()

        cmds = self.ex.generate_cmds()

        self.assertIn(["smalloc", "X",
                       nreps * self.m * self.n + (nreps - 1) * offset], cmds)

    def test_calls(self):
        """Test for generate call commands."""
        nreps = random.randint(1, 10)
        self.ex.nreps = nreps
        self.ex.data["X"]["vary"]["with"].add("rep")
        self.ex.infer_lds()

        cmds = self.ex.generate_cmds()

        idx = random.randint(0, nreps - 1)
        self.assertIn(["name", self.m, self.n, "X_%d" % idx, self.m,
                       "Y", self.m, "Z", self.n], cmds)

    def test_omp(self):
        """Test for omp in genrated call commands."""
        nreps = random.randint(1, 10)
        ncalls = random.randint(1, 10)
        self.ex.calls = ncalls * [self.ex.call]
        self.ex.nreps = nreps
        self.ex.calls_parallel = True

        cmds = self.ex.generate_cmds()

        self.assertEqual(cmds.count(["{omp"]), nreps)
        self.assertEqual(cmds.count(["}"]), nreps)

        lensumrange = random.randint(1, 10)
        self.ex.sumrange = ["j", range(lensumrange)]
        self.ex.sumrange_parallel = True

        cmds = self.ex.generate_cmds()

        self.assertEqual(cmds.count(["{omp"]), nreps)
        self.assertEqual(cmds.count(["}"]), nreps)

    def test_basecall(self):
        """Test for BasicCall calls (i.e., no Signature)."""
        sig = ("name", "char*", "int*", "double*", "double*")
        self.ex.call = BasicCall(sig, "N", "100", "1.5", "[10000]")
        self.ex.update_data()
        cmds = self.ex.generate_cmds()
        self.assertIn(["name", "N", 100, 1.5, "[10000]"], cmds)

        # now with a range
        lenrange = random.randint(1, 10)
        self.ex.range = ["i", range(lenrange)]
        self.ex.call = BasicCall(sig, "N", "i", "1.5", "[i * i]")
        cmds = self.ex.generate_cmds()
        idx = random.randint(0, lenrange - 1)
        self.assertIn(["name", "N", idx, 1.5, "[%d]" % (idx * idx)], cmds)


class TestExperimentSubmit(TestExperimentCmds):

    """Tests for Experiment.submit_prepate()."""

    def setUp(self):
        """Generate filenames."""
        TestExperimentCmds.setUp(self)
        self.sampler_ntmax = random.randint(2, 10)
        self.ex.sampler = {
            "backend_name": "",
            "backend_header": "",
            "backend_prefix": "prefix{nt}",
            "backend_suffix": "",
            "backend_footer": "",
            "kernels": {},
            "nt_max": self.sampler_ntmax,
            "exe": "executable"
        }
        self.filebase = "test_experiment.py_tmp"

    def tearDown(self):
        """Delete remporary files."""
        for filename in glob.glob(self.filebase + "*"):
            os.remove(filename)

    def test_files(self):
        """Test file creation."""
        open(self.filebase + ".eer", "w").close()

        self.ex.submit_prepare(self.filebase)

        self.assertTrue(os.path.isfile(self.filebase + ".sh"))
        self.assertTrue(os.path.isfile(self.filebase + ".calls"))
        self.assertFalse(os.path.isfile(self.filebase + ".elr"))
        self.assertFalse(os.path.isfile(self.filebase + ".err"))

    def test_threadrange(self):
        """Test files generated for #threads range."""
        lenrange = random.randint(2, 10)
        self.ex.range = ["i", range(1, lenrange + 1)]
        self.ex.nthreads = "i"

        script = self.ex.submit_prepare(self.filebase)

        for nt in self.ex.range[1]:
            self.assertTrue(os.path.isfile("%s.%d.calls" %
                                           (self.filebase, nt)))

        idx = random.randint(1, lenrange)
        self.assertIn("prefix%d" % idx, script)
        self.assertIn("prefix%d" % idx, script)
        self.assertEqual(script.count("executable"), lenrange + 1)

    def test_ompthreads(self):
        """Test setting OMP_NUM_THREADS."""
        lensumrange = random.randint(2, 10)
        self.ex.sumrange = ["j", range(1, lensumrange + 1)]
        self.ex.sumrange_parallel = True

        script = self.ex.submit_prepare(self.filebase)

        val = min(lensumrange, self.sampler_ntmax)
        self.assertIn("OMP_NUM_THREADS=%d" % val, script)


if __name__ == "__main__":
    unittest.main()
