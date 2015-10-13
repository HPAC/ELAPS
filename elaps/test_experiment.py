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
                'double*', 'int*', 'double*', 'int*', 'double*', 'float*',
                'int*'
            )},
            "nt_max": random.randint(1, 10),
            "exe": "x"
        }
        self.i = symbolic.Symbol("i")
        self.j = symbolic.Symbol("j")
        self.k = symbolic.Symbol("k")
        self.ns = [random.randint(1, 100) for _ in range(5)]

    def test_init(self):
        """Test for __init__() and attribute access."""
        ex = Experiment(note="Test")
        self.assertEqual(ex.note, "Test")

    def test_repr(self):
        """Test for __repr__()."""
        ex = Experiment(note="1234", range=("i", range(10)))
        self.assertEqual(eval(repr(ex)), ex)

    def test_infer_lds(self):
        """Test for infer_ld[s]()."""
        n1, n2, n3, n4, n5 = self.ns[:5]
        sig = Signature("name", Dim("m"), Dim("n"),
                        cData("A", "ldA * n"), Ld("ldA", "m"), Info())
        ex = Experiment(calls=[sig(n1, n2, "X", n1 + n3, 0)])

        ex.infer_ld(0, 4)

        self.assertEqual(ex.call.ldA, n1)

        self.assertRaises(TypeError, ex.infer_ld, 0, 3)

        # now setting along and rep
        ex.nreps = n4
        ex.vary["X"]["along"] = 0
        ex.vary["X"]["with"].add("rep")

        ex.infer_lds()

        self.assertEqual(ex.call.ldA, n1 * n4)

        # range
        ex.sumrange = ["i", range(n5)]
        ex.vary["X"]["with"].add("i")

        ex.infer_lds()

        self.assertEqual(ex.call.ldA, n1 * n4 * n5)

    def test_infer_lwork(self):
        """Test for infer_lwork[s]()."""
        n1, n2, n3 = self.ns[:3]
        sig = Signature("name", Dim("m"), Dim("n"),
                        dWork("W", "lWork"), Lwork("lWork", "m * n"))
        ex = Experiment(calls=[sig(n1, n2, "V", n1 * n2 + n3)])

        ex.infer_lwork(0, 4)

        self.assertEqual(ex.call.lWork, n1 * n2)

    def test_apply_connections_from(self):
        """Test for apply_connections_from()."""
        n1, n2, n3, n4 = self.ns[:4]
        sig = Signature("name", Dim("m"), Dim("n"),
                        iData("A", "m * n"), iData("B", "n * n"))
        call = sig(n1, n2, "X", "Y")
        ex = Experiment(calls=[call.copy()])

        # no connections
        ex.apply_connections_from(0, 1)
        self.assertEqual(call, ex.calls[0])

        # one call
        ex.calls[0].B = "X"
        ex.apply_connections_from(0, 2)
        self.assertNotEqual(call, ex.calls[0])
        self.assertEqual(ex.calls[0][1], n2)

        # two calls
        ex.calls = [sig(n1, n2, "X", "Y"), sig(n3, n4, "Z", "X")]

        ex.apply_connections_from(1, 2)

        self.assertEqual(ex.calls[0].m, n4)
        self.assertEqual(ex.calls[0].n, n4)

    def test_apply_connections_to(self):
        """Test for apply_connections_to()."""
        n1, n2, n3, n4 = self.ns[:4]
        sig = Signature("name", Dim("m"), Dim("n"),
                        iData("A", "m * n"), iData("B", "n * n"))
        call = sig(n1, n2, "X", "Y")
        ex = Experiment(calls=[call.copy()])

        # no connections
        ex.apply_connections_to(0, 1)
        self.assertEqual(call, ex.calls[0])

        # one call
        ex.calls[0].B = "X"
        ex.apply_connections_to(0, 2)
        self.assertNotEqual(call, ex.calls[0])
        self.assertEqual(ex.calls[0][1], n1)

        # two calls
        ex.calls = [sig(n1, n2, "X", "Y"), sig(n3, n4, "Z", "X")]

        ex.apply_connections_to(1, 2)

        self.assertEqual(ex.calls[1][2], n2)

    def test_check_sanity(self):
        """test for check_sanity()."""
        ex = Experiment(
            sampler=self.sampler,
            calls=[("dgemm", "N", "N", 1, 1, 1, 1, "A", 1, "B", 1, 1, "C", 1)]
        )

        # working
        ex.check_sanity(True)

        # error error
        ex.sampler = None
        self.assertRaises(TypeError, ex.check_sanity, True)

    def test_get_operand(self):
        """Test for get_operand()."""
        n1, n2, n3, n4 = self.ns[:4]
        sig = Signature("name", Dim("m"), Dim("n"),
                        sData("A", "ldA * n"), Ld("ldA", "m"))
        ex = Experiment(calls=[sig(n1, n2, "X", n1 + n3)])

        op = ex.get_operand("X")
        self.assertEqual(op["type"], sData)
        self.assertEqual(op["size"], (n1 + n3) * n2)
        self.assertEqual(op["dims"], (n1, n2))
        self.assertEqual(op["lds"], (n1 + n3, n2))


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
                    sData("C", "ldC * n"), Ld("ldC", "m"),
                    flops="2 * m * n * k"
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

        # PAPI not available
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
        ex, i = self.ex, self.i
        nt_max = ex.sampler["nt_max"]

        # working
        ex.set_nthreads(nt_max)
        self.assertEqual(ex.nthreads, nt_max)
        ex.set_nthreads("1")
        self.assertEqual(ex.nthreads, 1)
        ex.set_nthreads("i")
        self.assertEqual(ex.nthreads, i)

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

    def test_set_range_var(self):
        """Test for set_range_var()."""
        ex, i, j = self.ex, self.i, self.j

        # working
        ex.set_range_var("j")
        self.assertEqual(ex.range[0], j)

        # string
        self.assertRaises(ValueError, ex.set_range_var, "")
        ex.set_range_var("", force=True)
        self.assertEqual(ex.range[0], i)

        # type
        self.assertRaises(TypeError, ex.set_range_var, 1)
        ex.set_range_var(1, force=True)
        self.assertEqual(ex.range[0], i)

        # conflict
        ex.sumrange = [j, [1]]
        self.assertRaises(ValueError, ex.set_range_var, "j")
        ex.set_range_var("j", force=True)
        self.assertEqual(ex.range[0], i)
        ex.sumrange = None

        # range not set
        ex.range = None
        self.assertRaises(ValueError, ex.set_range_var, "i")
        ex.set_range_var("i", force=True)
        self.assertEqual(ex.range[0], i)

        # check_only
        ex.set_range_var("j", check_only=True)
        self.assertEqual(ex.range[0], i)

    def test_set_range_vals(self):
        """Test for set_range_vals()."""
        ex = self.ex
        defrange = symbolic.Range("100:100:2000")
        onerange = symbolic.Range("1")

        # working
        ex.set_range_vals(defrange)
        self.assertEqual(ex.range[1], defrange)
        ex.set_range_vals("100:100:2000")
        self.assertEqual(ex.range[1], defrange)

        # empty
        self.assertRaises(ValueError, ex.set_range_vals, "")
        ex.set_range_vals("", force=True)
        self.assertEqual(ex.range[1], onerange)

        # type
        self.assertRaises(TypeError, ex.set_range_vals, 1234)
        ex.set_range_vals(1234, force=True)
        self.assertEqual(ex.range[1], onerange)

        # length > 0
        self.assertRaises(ValueError, ex.set_range_vals, [])
        ex.set_range_vals([], force=True)
        self.assertEqual(ex.range[1], onerange)

        # range not set
        ex.range = None
        self.assertRaises(ValueError, ex.set_range_vals, defrange)
        ex.set_range_vals(defrange, force=True)
        self.assertEqual(ex.range[1], defrange)

        # check_only
        ex.set_range_vals(onerange, check_only=True)
        self.assertEqual(ex.range[1], defrange)

    def test_set_range(self):
        """Test for set_range()."""
        ex = self.ex

        # working
        ex.set_range(["i", "100:100:2000"])

        # disabling
        ex.set_range(None)
        self.assertEqual(ex.calls[0].m, 2000)

        # check_only
        ex.set_range(["i", "100:100:2000"], check_only=True)
        self.assertEqual(ex.range, None)

    def test_set_nreps(self):
        """Test for set_nreps()."""
        ex = self.ex

        # working
        ex.set_nreps(10)
        self.assertEqual(ex.nreps, 10)
        ex.set_nreps("20")
        self.assertEqual(ex.nreps, 20)

        # empty
        self.assertRaises(ValueError, ex.set_nreps, "")
        ex.set_nreps("", force=True)
        self.assertEqual(ex.nreps, 1)

        # type
        self.assertRaises(TypeError, ex.set_nreps, None)
        ex.set_nreps(None, force=True)
        self.assertEqual(ex.nreps, 1)

        # > 0
        self.assertRaises(ValueError, ex.set_nreps, 0)
        ex.set_nreps(0, force=True)
        self.assertEqual(ex.nreps, 1)

        # check_only
        ex.set_nreps(10, check_only=True)
        self.assertEqual(ex.nreps, 1)

    def test_set_sumrange_var(self):
        """Test for set_sumrange_var()."""
        ex, j = self.ex, self.j
        ex.set_sumrange(["j", "1:100"])

        # working
        ex.set_sumrange_var("j")
        self.assertEqual(ex.sumrange[0], j)

        # string
        self.assertRaises(ValueError, ex.set_sumrange_var, "")
        ex.set_sumrange_var("", force=True)
        self.assertEqual(ex.sumrange[0], j)

        # type
        self.assertRaises(TypeError, ex.set_sumrange_var, 1)
        ex.set_sumrange_var(1, force=True)
        self.assertEqual(ex.sumrange[0], j)

        # conflict
        self.assertRaises(ValueError, ex.set_sumrange_var, "i")
        ex.set_sumrange_var("i", force=True)
        self.assertEqual(ex.sumrange[0], j)
        ex.sumrange = None

        # range not set
        ex.sumrange = None
        self.assertRaises(ValueError, ex.set_sumrange_var, "j")
        ex.set_sumrange_var("j", force=True)
        self.assertEqual(ex.sumrange[0], j)

        # check_only
        ex.set_sumrange_var("k", check_only=True)
        self.assertEqual(ex.sumrange[0], j)

    def test_set_sumrange_vals(self):
        """Test for set_sumrange_vals()."""
        ex = self.ex
        defrange = symbolic.Range("1:100")
        onerange = symbolic.Range("1")
        ex.set_sumrange(["j", "1:100"])

        # working
        ex.set_sumrange_vals(defrange)
        self.assertEqual(ex.sumrange[1], defrange)
        ex.set_sumrange_vals("1:100")
        self.assertEqual(ex.sumrange[1], defrange)

        # empty
        self.assertRaises(ValueError, ex.set_sumrange_vals, "")
        ex.set_sumrange_vals("", force=True)
        self.assertEqual(ex.sumrange[1], onerange)

        # type
        self.assertRaises(TypeError, ex.set_sumrange_vals, 1234)
        ex.set_sumrange_vals(1234, force=True)
        self.assertEqual(ex.sumrange[1], onerange)

        # length > 0
        self.assertRaises(ValueError, ex.set_sumrange_vals, [])
        ex.set_sumrange_vals([], force=True)
        self.assertEqual(ex.sumrange[1], onerange)

        # sumrange not set
        ex.sumrange = None
        self.assertRaises(ValueError, ex.set_sumrange_vals, defrange)
        ex.set_sumrange_vals(defrange, force=True)
        self.assertEqual(ex.sumrange[1], defrange)

        # check_only
        ex.set_sumrange_vals(onerange, check_only=True)
        self.assertEqual(ex.sumrange[1], defrange)

    def test_set_sumrange(self):
        """Test for set_sumrange()."""
        ex, j = self.ex, self.j

        # working
        ex.set_sumrange(["j", "1:100"])

        # disabling
        ex.set_arg(0, "m", "j + 100")
        ex.vary["A"]["with"].add(j)
        ex.set_sumrange(None)
        self.assertEqual(ex.calls[0].m, 200)
        self.assertEqual(ex.vary["A"]["with"], set())

        # check_only
        ex.set_range(["j", "1:100"], check_only=True)
        self.assertEqual(ex.sumrange, None)

    def test_set_sumrange_parallel(self):
        """Test for set_sumrange_parallel()."""
        ex = self.ex

        # working
        ex.set_sumrange_parallel()
        self.assertTrue(ex.sumrange_parallel)

        # availability
        ex.set_sumrange_parallel(False)
        ex.sampler["omp_enabled"] = False
        self.assertRaises(ValueError, ex.set_sumrange_parallel)
        ex.set_sumrange_parallel(force=True)
        self.assertFalse(ex.sumrange_parallel)
        ex.sampler["omp_enabled"] = True

        # check only
        ex.set_sumrange_parallel(check_only=True)
        self.assertFalse(ex.sumrange_parallel)

    def test_set_calls_parallel(self):
        """Test for set_calls_parallel()."""
        ex = self.ex

        # working
        ex.set_calls_parallel()
        self.assertTrue(ex.calls_parallel)

        # availability
        ex.set_calls_parallel(False)
        ex.sampler["omp_enabled"] = False
        self.assertRaises(ValueError, ex.set_calls_parallel)
        ex.set_calls_parallel(force=True)
        self.assertFalse(ex.calls_parallel)
        ex.sampler["omp_enabled"] = True

        # check only
        ex.set_calls_parallel(check_only=True)
        self.assertFalse(ex.calls_parallel)

    def test_set_arg(self):
        """Test for set_arg()."""
        ex, i = self.ex, self.i

        # working
        ex.set_arg(0, 5, 1000)
        self.assertEqual(ex.calls[0][5], 1000)
        ex.set_arg(0, "m", "7 * i")
        self.assertEqual(ex.calls[0].m, 7 * i)

        # wrong callid
        self.assertRaises(IndexError, ex.set_arg, 1, 5, 100)

        # arg 0
        self.assertRaises(IndexError, ex.set_arg, 0, 0, "name")

        # flag
        self.assertRaises(ValueError, ex.set_arg, 0, 1, "C")
        ex.set_arg(0, 1, "C", force=True)
        self.assertEqual(ex.calls[0][1], "N")

        # data: working
        ex.set_arg(0, "A", "D")
        self.assertIn("D", ex.operands)

        # data: type
        self.assertRaises(TypeError, ex.set_arg, 0, "A", "C")
        self.assertRaises(TypeError, ex.set_arg, 0, "A", 1234)

        # sizes
        ex.set_arg(0, "m", 100)
        ex.set_arg(0, "n", 100)
        ex.set_arg(0, "k", 200)
        self.assertRaises(ValueError, ex.set_arg, 0, "A", "B")
        ex.set_arg(0, "k", 100)
        ex.set_arg(0, "A", "B")

        # type
        self.assertRaises(TypeError, ex.set_arg, 0, "ldA", None)

        # min
        self.assertRaises(ValueError, ex.set_arg, 0, "ldA", 10)
        ex.set_arg(0, "ldA", 10, force=True)
        self.assertEqual(ex.calls[0].ldA, 100)

        # minsig
        ex.set_call(1, ("dgemm", "N", "N", 10, 10, 10, 1, "[100]", 10, "[100]",
                        10, 1, "[100]", 10))
        self.assertRaises(TypeError, ex.set_arg, 1, 1, 100)

    def test_set_call(self):
        """Test for set_call()."""
        ex = self.ex
        ex.sampler["kernels"]["name"] = ("name",)
        call = Signature("name")()

        # working (no sig)
        ex.set_call(1, call)
        self.assertEqual(ex.calls[1], call)
        ex.remove_call(1)

        # callid
        self.assertRaises(IndexError, ex.set_call, 10, call)
        ex.set_call(10, call, force=True)
        self.assertEqual(ex.calls[1], call)

        # None
        ex.set_call(1, None)
        self.assertEqual(len(ex.calls), 1)

        # available
        self.assertRaises(ValueError, ex.set_call, 1, Signature("name2")())
        ex.set_call(1, Signature("name2")(), force=True)
        self.assertEqual(len(ex.calls), 1)

        # type
        self.assertRaises(TypeError, ex.set_call, 1, 100)
        ex.set_call(1, ("name",))
        self.assertEqual(ex.calls[1], BasicCall(("name",)))

        # argument error
        call = ex.calls[0].sig()
        self.assertRaises(TypeError, ex.set_call, 1, call)
        self.assertEqual(ex.calls[1], BasicCall(("name",)))

        # check_only
        ex.set_call(1, ex.calls[0], check_only=True)
        self.assertEqual(ex.calls[1], BasicCall(("name",)))

    def test_add_call(self):
        """Test for add_call()."""
        ex = self.ex
        ex.sampler["kernels"]["name"] = ("name",)

        # working
        ex.add_call(Signature("name")())
        self.assertEqual(ex.calls[1], BasicCall(("name",)))

    def test_remove_call(self):
        """Test for remove_call()."""
        ex = self.ex
        call = ex.calls[0]

        # working
        ex.remove_call(0)
        self.assertEqual(ex.calls, [])
        ex.add_call(call)

        # index
        self.assertRaises(IndexError, ex.remove_call, 10)
        ex.remove_call(10, force=True)
        self.assertEqual(ex.calls, [])
        ex.add_call(call)

        # check_only
        ex.remove_call(0, check_only=True)
        self.assertEqual(len(ex.calls), 1)

    def test_set_calls(self):
        """Test for set_calls()."""
        ex = self.ex
        calls = ex.calls[:]

        # working
        ex.set_calls(calls)

        # type
        self.assertRaises(TypeError, ex.set_calls, "asdf")

        # check_only
        ex.set_calls([], check_only=True)
        self.assertEquals(ex.calls, calls)

    def test_set_vary_with(self):
        """Test for set_vary_with()."""
        ex, j = self.ex, self.j
        ex.set_sumrange([j, "1:100"])

        # working:
        ex.set_vary_with("A", ["rep"])
        self.assertEqual(ex.vary["A"]["with"], set(["rep"]))

        # index
        self.assertRaises(IndexError, ex.set_vary_with, "X", ["rep"])

        # type
        self.assertRaises(TypeError, ex.set_vary_with, "A", 100)

        # values
        self.assertRaises(ValueError, ex.set_vary_with, "A", [j, "a"])
        ex.set_vary_with("A", [j, "a"], force=True)
        self.assertEqual(ex.vary["A"]["with"], set([j]))

        # check_only
        ex.set_vary_with("A", [], check_only=True)
        self.assertEqual(ex.vary["A"]["with"], set([j]))

    def test_add_vary_with(self):
        """Test for add_vary_with()."""
        ex = self.ex

        # working
        ex.add_vary_with("A", "rep")
        self.assertEqual(ex.vary["A"]["with"], set(["rep"]))

        # index
        self.assertRaises(IndexError, ex.add_vary_with, "X", "rep")

        # type
        self.assertRaises(ValueError, ex.add_vary_with, "A", 10)

        # check_only
        ex.set_sumrange(["j", "1:100"])
        ex.add_vary_with("A", "j", check_only=True)
        self.assertEqual(ex.vary["A"]["with"], set(["rep"]))

    def test_remove_vary_with(self):
        """Test for remove_vary_with()."""
        ex, j = self.ex, self.j

        # working
        ex.add_vary_with("A", "rep")
        ex.remove_vary_with("A", "rep")
        self.assertEqual(ex.vary["A"]["with"], set())

        # index
        self.assertRaises(IndexError, ex.remove_vary_with, "X", "rep")

        # type
        self.assertRaises(ValueError, ex.remove_vary_with, "A", 10)

        # check_only
        ex.set_sumrange(["j", "1:100"])
        ex.add_vary_with("A", "j")
        ex.remove_vary_with("A", "j", check_only=True)
        self.assertEqual(ex.vary["A"]["with"], set([j]))

    def test_set_vary_along(self):
        """Test for set_vary_with()."""
        ex, j = self.ex, self.j
        ex.set_sumrange([j, "1:100"])

        # working:
        ex.set_vary_with("A", ["rep"])
        self.assertEqual(ex.vary["A"]["with"], set(["rep"]))

        # index
        self.assertRaises(IndexError, ex.set_vary_with, "X", ["rep"])

        # type
        self.assertRaises(TypeError, ex.set_vary_with, "A", 100)

        # values
        self.assertRaises(ValueError, ex.set_vary_with, "A", [j, "a"])
        ex.set_vary_with("A", [j, "a"], force=True)
        self.assertEqual(ex.vary["A"]["with"], set([j]))

        # check_only
        ex.set_vary_with("A", [], check_only=True)
        self.assertEqual(ex.vary["A"]["with"], set([j]))

    def test_set_vary_offset(self):
        """Test for set_vary_offset()."""
        ex, i, j = self.ex, self.i, self.j

        # working
        ex.set_vary_offset("B", 1000)
        self.assertEqual(ex.vary["B"]["offset"], 1000)
        ex.set_vary_offset("B", "10 * i")
        self.assertEqual(ex.vary["B"]["offset"], 10 * i)

        # index
        self.assertRaises(IndexError, ex.set_vary_offset, "X", 10)

        # type
        self.assertRaises(TypeError, ex.set_vary_offset, "B", None)

        # symbols
        self.assertRaises(ValueError, ex.set_vary_offset, "B", j + 100)

        # check_only
        ex.set_vary_offset("B", 100, check_only=True)
        self.assertEqual(ex.vary["B"]["offset"], 10 * i)

    def test_set_vary(self):
        """Test for set_vary()."""
        ex = self.ex

        # working
        ex.set_vary("C", offset=1000)
        self.assertEqual(ex.vary["C"]["offset"], 1000)

        # index
        self.assertRaises(IndexError, ex.set_vary, "X")

        # check_only
        ex.set_vary("A", offset=100, check_only=True)
        self.assertEqual(ex.vary["A"]["offset"], 0)


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
        ex.vary["X"]["with"].add("rep")
        ex.vary["Y"]["with"].add("j")
        ex.vary["Y"]["along"] = 0
        ex.vary["Z"]["with"].update(["rep", "j"])
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

        ex.vary["X"]["along"] = 0
        ex.vary["X"]["with"].add("rep")
        ex.infer_lds()

        cmds = ex.generate_cmds()

        self.assertIn(["smalloc", "X", nreps * m * n + (nreps - 1) * m], cmds)
        rangeidx = random.randint(0, lenrange - 1)
        repidx = random.randint(0, nreps - 1)
        self.assertIn(["soffset", "X", repidx * m,
                       "X_%d_%d" % (rangeidx, repidx)], cmds)

    def test_data_dep(self):
        """Test data commands with dependencies in data."""
        ex = self.ex
        j = self.j
        i = self.i
        n = self.n

        lenrange = random.randint(1, 10)
        lensumrange = random.randint(1, 10)
        ex.range = [i, range(lenrange)]
        ex.sumrange = [j, range(lensumrange)]
        ex.call.m = j
        ex.vary["X"]["with"].add(j)

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
        ex.vary["X"]["with"].add("rep")
        ex.vary["X"]["along"] = 1
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
        ex.vary["X"]["with"].add("rep")
        offset = random.randint(1, 100)
        ex.vary["X"]["offset"] = offset
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
        ex.vary["X"]["with"].add("rep")
        ex.infer_lds()

        cmds = ex.generate_cmds()

        idx = random.randint(0, nreps - 1)
        self.assertIn(["name", m, n, "X_%d" % idx, m, "Y", m, "Z", n], cmds)

    def test_omp(self):
        """Test for omp in generated call commands."""
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

    def test_basiccall(self):
        """Test for BasicCall calls (i.e., no Signature)."""
        ex = self.ex
        i = self.i

        sig = ("name", "char*", "int*", "double*", "double*")
        ex.call = BasicCall(sig, "N", 100, 1.5, [10000])
        cmds = ex.generate_cmds()
        self.assertIn(["name", "N", 100, 1.5, [10000]], cmds)

        # now with a range
        lenrange = random.randint(1, 10)
        ex.range = [i, range(lenrange)]
        ex.call = BasicCall(sig, "N", i - 1, 1.5, [i * i])
        cmds = ex.generate_cmds()
        idx = random.randint(0, lenrange - 1)
        self.assertIn(["name", "N", idx - 1, 1.5, [idx * idx]], cmds)


class TestExperimentSubmit(TestExperimentCmds):

    """Tests for Experiment.submit_prepare()."""

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
        """Delete temporary files."""
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
