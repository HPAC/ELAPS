#!/usr/bin/env python
"""Unittest for signature.py."""

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


class TestArgs(unittest.TestCase):

    """Tests for Arg classes."""

    def test_Name(self):
        """Test for Name."""
        self.assertEqual(Name("name"), "name")

    def test_Flag(self):
        """Test for Flag."""
        self.assertEqual(Flag("name", [1, 2]).default(), 1)

        self.assertTrue(issubclass(Trans, Flag))

    def test_Scalar(self):
        """Test for Scalar."""
        self.assertEqual(cScalar().format_sampler(2), "%s,%s" % (2., 0.))

        self.assertTrue(issubclass(iScalar, Scalar))

    def test_ArgWithMin(self):
        """Test for ArgWithMin."""
        self.assertEqual(ArgWithMin("name", "1234").minstr, "1234")

    def test_Data(self):
        """Test for Data."""
        self.assertEqual(cData("name").format_sampler(2), "[%s]" % 4)

        self.assertTrue(issubclass(sData, Data))

    def test_Ld(self):
        """Test for Ld."""
        pass

    def test_Inc(self):
        """Test for Inc."""
        pass

    def test_Work(self):
        """Test for Work."""
        self.assertTrue(issubclass(zWork, Work))

    def test_lWork(self):
        """Test for lWork."""
        pass

    def test_Info(self):
        """Test for Info."""
        pass

    def test_String(self):
        """Test for String."""
        pass


class TestSignature(unittest.TestCase):

    """ Tests for Signature."""

    def test_init(self):
        """Test for __init__()."""
        self.assertEqual(Signature("kernel")[0], Name("kernel"))

    def test_lambdas(self):
        """Test for lambda functions."""
        # flops
        sig = Signature("name", Dim("m"), Dim("n"), flops="m + n")
        self.assertEqual(sig.flops("name", 1234, 5678), 1234 + 5678)

        # min
        sig = Signature("name", Dim("m"), Dim("n"), Data("A", "m * n"))
        self.assertEqual(sig.A.min("name", 1234, 5678, None), 1234 * 5678)

        # attr
        sig = Signature("name", Dim("n"),
                        Scalar(attr="lower if n < 100 else None"))
        self.assertEqual(sig.alpha.properties("name", 5, None), ("lower",))
        self.assertEqual(sig.alpha.properties("name", 105, None), tuple())

        # failure checking
        self.assertRaises(NameError,
                          Signature, "name", Dim("m"), flops="n")

        self.assertRaises(NameError,
                          Signature, "name", Dim("m"), Data("X", "m * n"))

        self.assertRaises(NameError,
                          Signature, "name", Dim("m"),
                          Data("X", "m", "lower if n else None"))

    def test_dataargs(self):
        """Test for dataargs()."""
        sig = Signature("name", Dim("n"), Data("A"), Data("B"), Ld("x"),
                        Data("C"))
        self.assertEqual(sig.dataargs(), [2, 3, 5])

    def test_datatype(self):
        """Test for datatype()."""
        sig = Signature("name", Dim("n"), dData("A"), iData("B"), Ld("x"),
                        cData("C"))
        self.assertEqual(sig.datatype(), "double precision")


class TestCall(unittest.TestCase):

    """Tests for Call."""

    def setUp(self):
        """Set up a signature."""
        self.sig = Signature("name", Dim("n"), dData("A", "ldA * n + 5"),
                             Ld("ldA", "n + 3"), flops="n ** 4")

    def test_init(self):
        """Test for __init__()."""
        sig = self.sig

        self.assertRaises(TypeError, Call, "name", 1234)

        self.assertRaises(TypeError, sig, 1234)

        self.assertEqual(sig(1234, "X", 5), Call(sig, 1234, "X", 5))
        self.assertEqual(sig(), sig(1, None, None))

    def test_attr(self):
        """Test for __get/setattr__()."""
        sig = self.sig

        self.assertEqual(sig().A, None)

        call = sig()
        call.A = 2
        self.assertEqual(call, sig(1, 2, None))

    def test_argdict(self):
        """Test for argdict()."""
        sig = self.sig

        self.assertEqual(sig(2, 3, 4).argdict(),
                         {"name": "name", "n": 2, "A": 3, "ldA": 4})

    def test_complete(self):
        """Test for completing mechanism."""
        sig = self.sig

        call = sig()
        call[1] = 1234

        call2 = call.copy()
        call2.complete_once()
        self.assertEqual(call2, sig(1234, None, 1234 + 3))

        call2 = call.copy()
        call2.complete()
        self.assertEqual(call2, sig(1234, (1234 + 3) * 1234 + 5, 1234 + 3))

    def test_flops(self):
        """Test for flops()."""
        sig = self.sig

        call = sig()
        call.n = 1234
        self.assertEqual(call.flops(), 1234 ** 4)


if __name__ == "__main__":
    unittest.main()
