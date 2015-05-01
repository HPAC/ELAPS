#!/usr/bin/env python
"""Unittest for symbolic.py."""
from __future__ import division, print_function

from symbolic import *

import unittest
import random
import math
import __builtin__


class TestSymbolic(unittest.TestCase):

    """Common setup for all symbolic tests."""

    def setUp(self):
        """Set up 3 symbolic variables and 3 random numbers."""
        self.A = Symbol("A")
        self.B = Symbol("B")
        self.C = Symbol("C")
        self.n1 = self.n2 = self.n3 = random.randint(1, 100)
        while self.n2 == self.n1:
            self.n2 = random.randint(1, 100)
        while self.n3 in (self.n1, self.n2):
            self.n3 = random.randint(1, 100)


class TestSymbol(TestSymbolic):

    """Tests for Symbol."""

    def test_substitute(self):
        """Test for substitute()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(A.substitute(A=n1), n1)
        self.assertEqual(A(A=n1), n1)
        self.assertEqual(A.substitute(B=n1), A)

    def test_eq(self):
        """Test for ==."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(A, "A")

    def test_findsymbols(self):
        """Test for findsymbols()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(A.findsymbols(), set([A]))


class TestOperation(TestSymbolic):

    """Tests for Operation."""

    def setUp(self):
        """Set up an Operation."""
        TestSymbolic.setUp(self)
        self.op = Operation(self.A, self.B, self.n1)

    def test_substitute(self):
        """Test for substitute()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3
        op = self.op

        self.assertEqual(op.substitute(A=n2), Operation(n2, B, n1))

    def test_findsymbols(self):
        """Test for findsymbols()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3
        op = self.op

        self.assertEqual(op.findsymbols(), set([A, B]))


class TestMinus(TestSymbolic):

    """Tests for Minus."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(-A, Minus(A))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual((-(-A))(), A)

        self.assertEqual(Minus(n1)(), -n1)


class TestAbs(TestSymbolic):

    """Tests for Abs."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(abs(A), Abs(A))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(abs(abs(A))(), abs(A))
        self.assertEqual(abs(-A)(), abs(A))

        self.assertEqual(Abs(-n1)(), abs(n1))


class TestPlus(TestSymbolic):

    """Tests for Plus."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(n1 + A, Plus(n1, A))
        self.assertEqual(A + n1, Plus(A, n1))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(((A + B) + C)(), (A + (B + C))())
        self.assertEqual((n1 + A + n2)(), n1 + n2 + A)
        self.assertEqual((0 + A)(), A)

        self.assertEqual(Plus()(), 0)
        self.assertEqual(Plus(n1, n2)(), n1 + n2)


class TestProd(TestSymbolic):

    """Tests for Prod."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(n1 * A, Prod(n1, A))
        self.assertEqual(A * n1, Prod(A, n1))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(((A * B) * C)(), (A * (B * C))())

        self.assertEqual((n1 * A * n2)(), n1 * n2 * A)
        self.assertEqual((1 * A)(), A)

        self.assertEqual(Prod()(), 1)
        self.assertEqual(Prod(n1, n2)(), n1 * n2)


class TestDiv(TestSymbolic):

    """Tests for Div."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(n1 / A, Div(n1, A))
        self.assertEqual(A / n1, Div(A, n1))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual((A / (B / C))(), A * C / B)
        self.assertEqual(((A / B) / C)(), A / (B * C))
        self.assertEqual((A / n1)(), 1 / n1 * A)

        self.assertEqual(round(Div(n1, n2)(), 10), round(n1 / n2, 10))


class TestPower(TestSymbolic):

    """Tests for Power."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(A ** n1, Power(A, n1))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(((A ** B) ** C)(), A ** (B * C))
        self.assertEqual((A ** 2)(), A * A)

        self.assertEqual((A ** log(B, A))(), B)

        self.assertEqual(Power(n1, n2)(), n1 ** n2)


class TestLog(TestSymbolic):

    """Tests for Log."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(log(A, n1), Log(A, n1))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(log(A, A)(), 1)

        self.assertEqual(log(A ** B)(), (B * log(A))())

        self.assertEqual(Log(n1, n2 + 1)(), math.log(n1, n2 + 1))


class TestFloor(TestSymbolic):

    """Tests for Floor."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(floor(A), Floor(A))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(floor(floor(A))(), floor(A))

        self.assertEqual(Floor(n1)(), math.floor(n1))


class TestCeil(TestSymbolic):

    """Tests for Ceil."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(ceil(A), Ceil(A))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(ceil(ceil(A))(), ceil(A))

        self.assertEqual(Ceil(n1)(), math.ceil(n1))


class TestMin(TestSymbolic):

    """Tests for Min."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(min(A, B), Min(A, B))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(min(min(A, B), C)(), min(A, min(B, C))())
        self.assertEqual(Min(A)(), A)

        self.assertEqual(Min()(), float("-inf"))
        self.assertEqual(Min(n1, n2)(), __builtin__.min(n1, n2))


class TestMax(TestSymbolic):

    """Tests for Max."""

    def test_overload(self):
        """Test for overloading."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(max(A, B), Max(A, B))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(max(max(A, B), C)(), max(A, max(B, C))())
        self.assertEqual(Max(A)(), A)

        self.assertEqual(Max()(), float("inf"))
        self.assertEqual(Max(n1, n2)(), __builtin__.max(n1, n2))


class TestRange(TestSymbolic):

    """Tests for Range."""

    def setUp(self):
        """n1 < n2 < n3."""
        TestSymbolic.setUp(self)
        self.n1, self.n2, self.n3 = sorted((self.n1, self.n2, self.n3))

    def test_init(self):
        """Test for __init__()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertRaises(TypeError, Range, (n1, n2, "A"))
        self.assertRaises(Exception, Range, (n1, n2, n3, 4))

        # parser
        self.assertEqual(Range("%d" % n1), Range((n1, 1, n1)))
        self.assertEqual(Range("%d:%d" % (n1, n2)), Range((n1, 1, n2)))
        self.assertEqual(Range("%d:%d:%d" % (n1, n2, n3)), Range((n1, n2, n3)))

        self.assertEqual(Range("%d,%d:%d" % (n1, n2, n3)),
                         Range((n1, 1, n1), (n2, 1, n3)))

    def test_substitute(self):
        """Test for substitute()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(Range((A, n2, n3)).substitute(A=n1),
                         Range((n1, n2, n3)))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(Range((A * n1, n2, n3))(),
                         Range(((A * n1)(), n2, n3)))

        self.assertEqual(Range("1:10,1:-1")(), Range("1:10"))

    def test_findsymbols(self):
        """Test for findsymbols()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(Range((n1 + A, n2, n3)).findsymbols(), set([A]))

    def test_minmax(self):
        """Test for min() and max()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertRaises(TypeError, Range((A, n2, n3)).min)
        self.assertRaises(TypeError, Range((n1, A, n3)).max)
        self.assertEqual(Range().min(), float("inf"))
        self.assertEqual(Range().max(), float("-inf"))

        self.assertEqual(Range("1:2:8,-1:5").min(), -1)
        self.assertEqual(Range("1:2:8,-1:5").max(), 7)

    def test_iter(self):
        """Test for iter(R)."""
        self.assertEqual(list(Range("1:10,20:-2:0")),
                         range(1, 11) + range(20, -1, -2))

    def test_len(self):
        """Test for len(R)."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertRaises(TypeError, len, Range((A, n2, n3)))

        self.assertEqual(len(Range("1:10,20:-2:0")), 21)

        self.assertEqual(len(Range((n1, n2, n3))), len(range(n1, n3 + 1, n2)))


class TestSum(TestSymbolic):

    """Tests for Sum."""

    def test_init(self):
        """Test for __init__()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertRaises(TypeError, Sum, A, A=[n1], B=[n2])
        self.assertRaises(TypeError, Sum, A)
        self.assertRaises(TypeError, Sum, A, A=n1)

        self.assertEqual(Sum(A, n1, A=range(n2)), Sum(A + n1, A=range(n2)))

    def test_substitute(self):
        """Test for substitute()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        inst = Sum(A + B, A=Range((A, C, n1)))

        self.assertEqual(inst.substitute(A=n2),
                         Sum(A + B, A=Range((n2, C, n1))))
        self.assertEqual(inst.substitute(B=n2),
                         Sum(A + n2, A=Range((A, C, n1))))
        self.assertEqual(inst.substitute(C=n2),
                         Sum(A + B, A=Range((A, n2, n1))))

    def test_simplify(self):
        """Test for simplify()."""
        A, B, C, n1, n2, n3 = self.A, self.B, self.C, self.n1, self.n2, self.n3

        self.assertEqual(Sum(A * n1, A=Range((B, n2, n3)))(),
                         Sum((A * n1)(), A=Range((B, n2, n3))))
        self.assertEqual(Sum(A, A=Range((B * n1, n2, n3)))(),
                         Sum(A, A=Range((B * n1, n2, n3))()))

        self.assertEqual(Sum(A, B=range(n1))(), n1 * A)
        self.assertEqual(Sum(A + B, A=range(n1))(),
                         sum(A + B for A in range(n1))())


if __name__ == "__main__":
    unittest.main()
