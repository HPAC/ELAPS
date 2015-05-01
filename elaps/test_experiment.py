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
            "name": "samplername",
            "system_name": "system",
            "blas_name": "blas",
            "backend_name": "",
            "backend_header": "",
            "backend_prefix": "",
            "backend_suffix": "",
            "backend_footer": "",
            "ncores": 2,
            "threads_per_core": 1,
            "omp_enabled": True,
            "papi_enabled": True,
            "papi_counters_max": 2,
            "papi_counters_avail": ("C1", "C2", "C3"),
            "kernels": {"dgemm": (
                'dgemm', 'char*', 'char*', 'int*', 'int*', 'int*', 'double*',
                'double*', 'int*', 'double*', 'int*', 'double*', 'double*',
                'int*'
            )},
            "nt_max": random.randint(1, 10),
            "exe": "x"
        }
        self.i = symbolic.Symbol("i")
        self.j = symbolic.Symbol("j")
        self.k = symbolic.Symbol("k")

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
        i = self.i

        sig = Signature("name", Dim("m"), Dim("n"),
                        iData("A", "m * n"), iData("B", "n * n"))
        ex = Experiment()
        ex.call = sig(10, 20, "X", "Y")
        ex.range = [i, range(random.randint(1, 10))]
        ex.update_data()
        ex.vary_set("X", offset="10 * i")

        self.assertEqual(ex.data["X"]["vary"]["offset"], 10 * i)

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
        i = self.i
        j = self.j
        k = self.k

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
        ex.range = [i, [1, 2], 3]
        self.assertRaises(TypeError, ex.check_sanity, True)
        ex.range = [1, [1, 2]]
        self.assertRaises(TypeError, ex.check_sanity, True)
        ex.range = None
        ex.range = [i, 1]
        self.assertRaises(TypeError, ex.check_sanity, True)
        ex.range = [j, range(random.randint(1, 10))]
        ex.sumrange = [j, [1, 2]]
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.range = [i, [1, 2, 3]]
        ex.sumrange = [j, [k, 2]]
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.sumrange = [j, [i, 2]]
        ex.check_sanity(True)
        ex.sumrange = None

        # threads
        ex.nthreads = ex.sampler["nt_max"] + random.randint(1, 10)
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.nthreads = k
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.range = [k, [1, 2]]
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
        ex.call[1] = k
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
        ex.data["X"]["vary"]["with"].add(symbolic.Symbol("a"))
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.data["X"]["vary"]["with"] = set((k,))
        ex.data["X"]["vary"]["along"] = 2
        self.assertRaises(IndexError, ex.check_sanity, True)
        ex.data["X"]["vary"]["along"] = 1
        ex.data["X"]["vary"]["offset"] = symbolic.Symbol("a")
        self.assertRaises(ValueError, ex.check_sanity, True)
        ex.data["X"]["vary"]["offset"] = 10


class TestExperimentSetters(TestExperiment):

    """Tests for the Experiment set_* routines."""

    def setUp(self):
        """Set up a default experiment."""
        TestExperiment.setUp(self)
        i = self.i
        self.ex = Experiment(
            sampler=self.sampler,
            range=[i, range(100, 2001, 100)],
            nreps=10,
            calls=[
                Signature(
                    "dgemm",
                    Trans("transA"), Trans("transB"),
                    Dim("m"), Dim("n"), Dim("k"),
                    dScalar(),
                    dData("A", "ldA * (k if transA == 'N' else m)"),
                    Ld("ldA", "m if transA == 'N' else k"),
                    dData("B", "ldB * (n if transB == 'N' else k)"),
                    Ld("ldB", "k if transB == 'N' else n"),
                    dScalar("beta"),
                    dData("C", "ldC * n"), Ld("ldC", "m"),
                    complexity="2 * m * n * k"
                )("N", "N", i, i, i, 1, "A", i, "B", i, 1, "C", i)
            ]
        )

    def test_set_sampler(self):
        """Test for set_sampler()."""
        sampler = self.sampler
        ex = self.ex

        # working
        ex.set_sampler(sampler)

        # attribute checks
        del sampler["ncores"]
        self.assertRaises(KeyError, ex.set_sampler, sampler)
        sampler["ncores"] = 1

        # papi not available
        ex.papi_counters = ["C1", "C2"]
        sampler["papi_enabled"] = False
        self.assertRaises(ValueError, ex.set_sampler, sampler)
        ex.set_sampler(sampler, force=True)
        self.assertEqual(len(ex.papi_counters), 0)
        sampler["papi_enabled"] = True

        # counter count
        ex.papi_counters = ["C1", "C2", "C3"]
        self.assertRaises(ValueError, ex.set_sampler, sampler)
        ex.set_sampler(sampler, force=True)
        self.assertEqual(ex.papi_counters, ["C1", "C2"])

        # counters not available
        ex.papi_counters = ["C1", "C4"]
        self.assertRaises(ValueError, ex.set_sampler, sampler)
        ex.set_sampler(sampler, force=True)
        self.assertEqual(ex.papi_counters, ["C1"])

        # thread count
        ex.nthreads = sampler["nt_max"] + 1
        self.assertRaises(ValueError, ex.set_sampler, sampler)
        ex.set_sampler(sampler, force=True)
        self.assertEqual(ex.nthreads, sampler["nt_max"])

        # kernel availability
        ex.calls.append(Signature("unknown")())
        self.assertRaises(KeyError, ex.set_sampler, sampler)
        ex.set_sampler(sampler, force=True)
        self.assertEqual(len(ex.calls), 1)

        # kernel compatibility
        ex.calls.append(["dgemm", 1, 2, 3])
        self.assertRaises(ValueError, ex.set_sampler, sampler)
        ex.set_sampler(sampler, force=True)
        self.assertEqual(len(ex.calls), 1)

        # check_only
        ex.sampler = None
        ex.set_sampler(sampler, check_only=True)
        self.assertEqual(ex.sampler, None)

    def test_set_papi_counters(self):
        """Test for set_papi_counters()."""
        ex = self.ex

        # working
        ex.set_papi_counters(["C1"])

        # type
        self.assertRaises(TypeError, ex.set_papi_counters, "string")

        # enabled
        ex.sampler["papi_enabled"] = False
        self.assertRaises(ValueError, ex.set_papi_counters, ["C1"])
        ex.set_papi_counters(["C1"], force=True)
        self.assertEqual(ex.papi_counters, [])
        ex.sampler["papi_enabled"] = True

        # availability
        self.assertRaises(ValueError, ex.set_papi_counters, ["C1", "D1"])
        ex.set_papi_counters(["C1", "D1"], force=True)
        self.assertEqual(ex.papi_counters, ["C1"])

        # length
        self.assertRaises(ValueError, ex.set_papi_counters, ["C1", "C2", "C3"])
        ex.set_papi_counters(["C1", "C2", "C3"], force=True)
        self.assertEqual(ex.papi_counters, ["C1", "C2"])

        # check_only
        ex.papi_counters = []
        ex.set_papi_counters(["C1", "C2"], check_only=True)
        self.assertEqual(ex.papi_counters, [])

    def test_set_nthreads(self):
        """Test for set_nthreads()."""
        ex = self.ex
        nt_max = ex.sampler["nt_max"]

        # working
        ex.set_nthreads(2)
        self.assertEqual(ex.nthreads, 2)
        ex.set_nthreads("1")
        self.assertEqual(ex.nthreads, 1)
        ex.set_nthreads("i")
        self.assertEqual(ex.nthreads, symbolic.Symbol("i"))

        # type
        self.assertRaises(TypeError, ex.set_nthreads, None)

        # bound
        self.assertRaises(ValueError, ex.set_nthreads, nt_max + 1)
        ex.set_nthreads(nt_max + 1, force=True)
        self.assertEqual(ex.nthreads, nt_max)

        # var
        self.assertRaises(NameError, ex.set_nthreads, "j")

        # check_only
        ex.set_nthreads(1, check_only=True)
        self.assertEqual(ex.nthreads, nt_max)


class TestExperimentCmds(unittest.TestCase):

    """Tests for Experiment.generate_cmds()."""

    def setUp(self):
        """Set up a signature and experiment with call."""
        self.m = m = random.randint(1, 100)
        self.n = n = random.randint(1, 100)
        self.sig = sig = Signature("name", Dim("m"), Dim("n"),
                                   sData("A", "ldA * n"), Ld("ldA", "m"),
                                   dData("B", "ldB * m"), Ld("ldB", "m"),
                                   cData("C", "ldC * n"), Ld("ldC", "n"))
        self.ex = ex = Experiment()
        ex.calls = [sig(m, n, "X", None, "Y", None, "Z", None)]
        ex.infer_lds()
        ex.update_data()
        self.i = symbolic.Symbol("i")
        self.j = symbolic.Symbol("j")

    def test_cmd_order(self):
        """Test for generate_cmds()."""
        ex = self.ex
        m = self.m
        n = self.n

        ex.call.ldA = ldA = random.randint(100, 200)
        ex.call.ldB = ldB = random.randint(100, 200)
        ex.call.ldC = ldC = random.randint(100, 200)
        cmds = ex.generate_cmds()
        cmds = [cmd for cmd in cmds if cmd and cmd[0][0] != "#"]
        self.assertEqual(cmds, [
            ["smalloc", "X", ldA * n],
            ["dmalloc", "Y", ldB * m],
            ["cmalloc", "Z", ldC * n],
            ["name", m, n, "X", ldA, "Y", ldB, "Z", ldC],
            ["go"]
        ])

    def test_data_norange(self):
        """Test data commands without range."""
        ex = self.ex
        m = self.m
        n = self.n

        nreps = random.randint(1, 10)
        lensumrange = random.randint(1, 10)

        ex.nreps = nreps
        ex.sumrange = ["j", range(lensumrange)]
        ex.data["X"]["vary"]["with"].add("rep")
        ex.data["Y"]["vary"]["with"].add("j")
        ex.data["Y"]["vary"]["along"] = 0
        ex.data["Z"]["vary"]["with"].update(["rep", "j"])
        ex.infer_lds()

        cmds = ex.generate_cmds()

        self.assertIn(["smalloc", "X", nreps * m * n], cmds)
        idx = random.randint(0, nreps - 1)
        self.assertIn(["soffset", "X", idx * m * n, "X_%d" % idx], cmds)

        self.assertIn([
            "dmalloc", "Y", lensumrange * m * m + (lensumrange - 1) * m
        ], cmds)
        idx = random.randint(0, lensumrange - 1)
        self.assertIn(["doffset", "Y", idx * m, "Y_%d" % idx], cmds)

        self.assertIn(["cmalloc", "Z", nreps * lensumrange * n * n], cmds)
        idxrep = random.randint(0, nreps - 1)
        idxrange = random.randint(0, lensumrange - 1)
        self.assertIn(["coffset", "Z",
                       (idxrep * lensumrange + idxrange) * n * n,
                       "Z_%d_%d" % (idxrep, idxrange)], cmds)

    def test_data_range(self):
        """Test data commands when range is set."""
        ex = self.ex
        m = self.m
        n = self.n

        lenrange = random.randint(1, 10)
        nreps = random.randint(1, 10)

        ex.range = ["i", range(lenrange)]
        ex.nreps = nreps

        ex.data["X"]["vary"]["along"] = 0
        ex.data["X"]["vary"]["with"].add("rep")
        ex.infer_lds()

        cmds = ex.generate_cmds()

        self.assertIn(["smalloc", "X", nreps * m * n + (nreps - 1) * m], cmds)
        rangeidx = random.randint(0, lenrange - 1)
        repidx = random.randint(0, nreps - 1)
        self.assertIn(["soffset", "X", repidx * m,
                       "X_%d_%d" % (rangeidx, repidx)], cmds)

    def test_data_dep(self):
        """Test data commands with depedencies in data."""
        ex = self.ex
        j = self.j
        i = self.i
        n = self.n

        lenrange = random.randint(1, 10)
        lensumrange = random.randint(1, 10)
        ex.range = [i, range(lenrange)]
        ex.sumrange = [j, range(lensumrange)]
        ex.call.m = j
        ex.data["X"]["vary"]["with"].add(j)

        ex.infer_lds()

        cmds = ex.generate_cmds()

        rangeidx = random.randint(0, lenrange - 1)
        sumrangeidx = random.randint(0, lensumrange - 1)
        offset = n * sum(range(sumrangeidx))
        self.assertIn(["soffset", "X", offset,
                       "X_%d_%d" % (rangeidx, sumrangeidx)], cmds)

    def test_data_along(self):
        """Test along = 1."""
        ex = self.ex
        m = self.m
        n = self.n

        nreps = random.randint(1, 10)
        ex.nreps = nreps
        ex.data["X"]["vary"]["with"].add("rep")
        ex.data["X"]["vary"]["along"] = 1
        ex.infer_lds()

        cmds = ex.generate_cmds()

        self.assertIn(["smalloc", "X", nreps * m * n], cmds)
        repidx = random.randint(0, nreps - 1)
        self.assertIn(["soffset", "X", repidx * m * n, "X_%d" % repidx], cmds)

    def test_data_offset(self):
        """Test offset."""
        ex = self.ex
        m = self.m
        n = self.n

        nreps = random.randint(1, 10)
        ex.nreps = nreps
        ex.data["X"]["vary"]["with"].add("rep")
        offset = random.randint(1, 100)
        ex.data["X"]["vary"]["offset"] = offset
        ex.infer_lds()

        cmds = ex.generate_cmds()

        self.assertIn(["smalloc", "X", nreps * m * n + (nreps - 1) * offset],
                      cmds)

    def test_calls(self):
        """Test for generate call commands."""
        ex = self.ex
        m = self.m
        n = self.n

        nreps = random.randint(1, 10)
        ex.nreps = nreps
        ex.data["X"]["vary"]["with"].add("rep")
        ex.infer_lds()

        cmds = ex.generate_cmds()

        idx = random.randint(0, nreps - 1)
        self.assertIn(["name", m, n, "X_%d" % idx, m, "Y", m, "Z", n], cmds)

    def test_omp(self):
        """Test for omp in genrated call commands."""
        ex = self.ex
        j = self.j

        nreps = random.randint(1, 10)
        ncalls = random.randint(1, 10)
        ex.calls = ncalls * [ex.call]
        ex.nreps = nreps
        ex.calls_parallel = True

        cmds = ex.generate_cmds()

        self.assertEqual(cmds.count(["{omp"]), nreps)
        self.assertEqual(cmds.count(["}"]), nreps)

        lensumrange = random.randint(1, 10)
        ex.sumrange = [j, range(lensumrange)]
        ex.sumrange_parallel = True

        cmds = ex.generate_cmds()

        self.assertEqual(cmds.count(["{omp"]), nreps)
        self.assertEqual(cmds.count(["}"]), nreps)

    def test_basecall(self):
        """Test for BasicCall calls (i.e., no Signature)."""
        ex = self.ex
        i = self.i

        sig = ("name", "char*", "int*", "double*", "double*")
        ex.call = BasicCall(sig, "N", "100", "1.5", "[10000]")
        ex.update_data()
        cmds = ex.generate_cmds()
        self.assertIn(["name", "N", 100, 1.5, "[10000]"], cmds)

        # now with a range
        lenrange = random.randint(1, 10)
        ex.range = [i, range(lenrange)]
        ex.call = BasicCall(sig, "N", "i", "1.5", "[i * i]")
        cmds = ex.generate_cmds()
        idx = random.randint(0, lenrange - 1)
        self.assertIn(["name", "N", idx, 1.5, "[%d]" % (idx * idx)], cmds)


class TestExperimentSubmit(TestExperimentCmds):

    """Tests for Experiment.submit_prepate()."""

    def setUp(self):
        """Generate filenames."""
        TestExperimentCmds.setUp(self)
        self.ex.sampler = self.sampler = {
            "backend_name": "",
            "backend_header": "",
            "backend_prefix": "prefix{nt}",
            "backend_suffix": "",
            "backend_footer": "",
            "kernels": {},
            "nt_max": random.randint(2, 10),
            "exe": "executable"
        }
        self.filebase = "test_experiment.py_tmp"

    def tearDown(self):
        """Delete remporary files."""
        for filename in glob.glob(self.filebase + "*"):
            os.remove(filename)

    def test_files(self):
        """Test file creation."""
        ex = self.ex
        filebase = self.filebase

        open(filebase + ".eer", "w").close()

        ex.submit_prepare(filebase)

        self.assertTrue(os.path.isfile(filebase + ".sh"))
        self.assertTrue(os.path.isfile(filebase + ".calls"))
        self.assertFalse(os.path.isfile(filebase + ".elr"))
        self.assertFalse(os.path.isfile(filebase + ".err"))

    def test_threadrange(self):
        """Test files generated for #threads range."""
        ex = self.ex
        i = self.i
        filebase = self.filebase

        lenrange = random.randint(2, 10)
        ex.range = [i, range(1, lenrange + 1)]
        ex.nthreads = i

        script = ex.submit_prepare(filebase)

        for nt in ex.range[1]:
            self.assertTrue(os.path.isfile("%s.%d.calls" % (filebase, nt)))

        idx = random.randint(1, lenrange)
        self.assertIn("prefix%d" % idx, script)
        self.assertIn("prefix%d" % idx, script)
        self.assertEqual(script.count("executable"), lenrange + 1)

    def test_ompthreads(self):
        """Test setting OMP_NUM_THREADS."""
        ex = self.ex
        sampler = self.sampler
        filebase = self.filebase
        j = self.j

        lensumrange = random.randint(2, 10)
        ex.sumrange = [j, range(1, lensumrange + 1)]
        ex.sumrange_parallel = True

        script = ex.submit_prepare(filebase)

        val = min(lensumrange, sampler["nt_max"])
        self.assertIn("OMP_NUM_THREADS=%d" % val, script)


if __name__ == "__main__":
    unittest.main()
