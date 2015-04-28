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
        self.assertEqual(self.A.substitute(A=self.n1), self.n1)
        self.assertEqual(self.A(A=self.n1), self.n1)
        self.assertEqual(self.A.substitute(B=self.n1), self.A)

    def test_eq(self):
        """Test for ==."""
        self.assertEqual(self.A, "A")

    def test_findsymbols(self):
        """Test for findsymbols()."""
        self.assertEqual(self.A.findsymbols(), set([self.A]))


class TestOperation(TestSymbolic):

    """Tests for Operation."""

    def setUp(self):
        """Set up an Operation."""
        TestSymbolic.setUp(self)
        self.op = Operation(self.A, self.B, self.n1)

    def test_substitute(self):
        """Test for substitute()."""
        self.assertEqual(self.op.substitute(A=self.n2),
                         Operation(self.n2, self.B, self.n1))

    def test_findsymbols(self):
        """Test for findsymbols()."""
        self.assertEqual(self.op.findsymbols(), set([self.A, self.B]))


class TestMinus(TestSymbolic):

    """Tests for Minus."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(-self.A, Minus(self.A))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual((-(-self.A))(), self.A)

        self.assertEqual(Minus(self.n1)(), -self.n1)


class TestAbs(TestSymbolic):

    """Tests for Abs."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(abs(self.A), Abs(self.A))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(abs(abs(self.A))(), abs(self.A))
        self.assertEqual(abs(-self.A)(), abs(self.A))

        self.assertEqual(Abs(-self.n1)(), abs(self.n1))


class TestPlus(TestSymbolic):

    """Tests for Plus."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(self.n1 + self.A, Plus(self.n1, self.A))
        self.assertEqual(self.A + self.n1, Plus(self.A, self.n1))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(((self.A + self.B) + self.C)(),
                         (self.A + (self.B + self.C))())
        self.assertEqual((self.n1 + self.A + self.n2)(),
                         self.n1 + self.n2 + self.A)
        self.assertEqual((0 + self.A)(), self.A)

        self.assertEqual(Plus()(), 0)
        self.assertEqual(Plus(self.n1, self.n2)(), self.n1 + self.n2)


class TestProd(TestSymbolic):

    """Tests for Prod."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(self.n1 * self.A, Prod(self.n1, self.A))
        self.assertEqual(self.A * self.n1, Prod(self.A, self.n1))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(((self.A * self.B) * self.C)(),
                         (self.A * (self.B * self.C))())

        self.assertEqual((self.n1 * self.A * self.n2)(),
                         self.n1 * self.n2 * self.A)
        self.assertEqual((1 * self.A)(), self.A)

        self.assertEqual(Prod()(), 1)
        self.assertEqual(Prod(self.n1, self.n2)(), self.n1 * self.n2)


class TestDiv(TestSymbolic):

    """Tests for Div."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(self.n1 / self.A, Div(self.n1, self.A))
        self.assertEqual(self.A / self.n1, Div(self.A, self.n1))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual((self.A / (self.B / self.C))(),
                         self.A * self.C / self.B)
        self.assertEqual(((self.A / self.B) / self.C)(),
                         self.A / (self.B * self.C))
        self.assertEqual((self.A / self.n1)(), 1 / self.n1 * self.A)

        self.assertEqual(round(Div(self.n1, self.n2)(), 10),
                         round(self.n1 / self.n2, 10))


class TestPower(TestSymbolic):

    """Tests for Power."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(self.A ** self.n1, Power(self.A, self.n1))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(((self.A ** self.B) ** self.C)(),
                         self.A ** (self.B * self.C))
        self.assertEqual((self.A ** 2)(), self.A * self.A)

        self.assertEqual((self.A ** log(self.B, self.A))(), self.B)

        self.assertEqual(Power(self.n1, self.n2)(), self.n1 ** self.n2)


class TestLog(TestSymbolic):

    """Tests for Log."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(log(self.A, self.n1), Log(self.A, self.n1))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(log(self.A, self.A)(), 1)

        self.assertEqual(log(self.A ** self.B)(), (self.B * log(self.A))())

        self.assertEqual(Log(self.n1, self.n2 + 1)(),
                         math.log(self.n1, self.n2 + 1))


class TestFloor(TestSymbolic):

    """Tests for Floor."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(floor(self.A), Floor(self.A))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(floor(floor(self.A))(), floor(self.A))

        self.assertEqual(Floor(self.n1)(), math.floor(self.n1))


class TestCeil(TestSymbolic):

    """Tests for Ceil."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(ceil(self.A), Ceil(self.A))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(ceil(ceil(self.A))(), ceil(self.A))

        self.assertEqual(Ceil(self.n1)(), math.ceil(self.n1))


class TestMin(TestSymbolic):

    """Tests for Min."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(min(self.A, self.B), Min(self.A, self.B))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(min(min(self.A, self.B), self.C)(),
                         min(self.A, min(self.B, self.C))())
        self.assertEqual(Min(self.A)(), self.A)

        self.assertEqual(Min()(), float("-inf"))
        self.assertEqual(Min(self.n1, self.n2)(),
                         __builtin__.min(self.n1, self.n2))


class TestMax(TestSymbolic):

    """Tests for Max."""

    def test_overload(self):
        """Test for overloading."""
        self.assertEqual(max(self.A, self.B), Max(self.A, self.B))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(max(max(self.A, self.B), self.C)(),
                         max(self.A, max(self.B, self.C))())
        self.assertEqual(Max(self.A)(), self.A)

        self.assertEqual(Max()(), float("inf"))
        self.assertEqual(Max(self.n1, self.n2)(),
                         __builtin__.max(self.n1, self.n2))


class TestRange(TestSymbolic):

    """Tests for Range."""

    def setUp(self):
        """n1 < n2 < n3."""
        TestSymbolic.setUp(self)
        self.n1, self.n2, self.n3 = sorted((self.n1, self.n2, self.n3))

    def test_init(self):
        """Test for __init__()."""
        self.assertRaises(TypeError, Range, (self.n1, self.n2, "A"))
        self.assertRaises(Exception, Range, (self.n1, self.n2, self.n3, 4))

        # parser
        self.assertEqual(Range("%d" % self.n1), Range((self.n1, 1, self.n1)))
        self.assertEqual(Range("%d:%d" % (self.n1, self.n2)),
                         Range((self.n1, 1, self.n2)))
        self.assertEqual(Range("%d:%d:%d" % (self.n1, self.n2, self.n3)),
                         Range((self.n1, self.n2, self.n3)))

        self.assertEqual(Range("%d,%d:%d" % (self.n1, self.n2, self.n3)),
                         Range((self.n1, 1, self.n1), (self.n2, 1, self.n3)))

    def test_substitute(self):
        """Test for substitute()."""
        self.assertEqual(
            Range((self.A, self.n2, self.n3)).substitute(A=self.n1),
            Range((self.n1, self.n2, self.n3))
        )

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(Range((self.A * self.n1, self.n2, self.n3))(),
                         Range(((self.A * self.n1)(), self.n2, self.n3)))

        self.assertEqual(Range("1:10,1:-1")(), Range("1:10"))

    def test_findsymbols(self):
        """Test for findsymbols()."""
        self.assertEqual(
            Range((self.n1 + self.A, self.n2, self.n3)).findsymbols(),
            set([self.A])
        )

    def test_minmax(self):
        """Test for min() and max()."""
        self.assertRaises(TypeError, Range((self.A, self.n2, self.n3)).min)
        self.assertRaises(TypeError, Range((self.n1, self.A, self.n3)).max)
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
        self.assertRaises(TypeError, len, Range((self.A, self.n2, self.n3)))

        self.assertEqual(len(Range("1:10,20:-2:0")), 21)

        self.assertEqual(len(Range((self.n1, self.n2, self.n3))),
                         len(range(self.n1, self.n3 + 1, self.n2)))


class TestSum(TestSymbolic):

    """Tests for Sum."""

    def test_init(self):
        """Test for __init__()."""
        self.assertRaises(TypeError, Sum, self.A, A=[self.n1], B=[self.n2])
        self.assertRaises(TypeError, Sum, self.A)
        self.assertRaises(TypeError, Sum, self.A, A=self.n1)

        self.assertEqual(Sum(self.A, self.n1, A=range(self.n2)),
                         Sum(self.A + self.n1, A=range(self.n2)))

    def test_substitute(self):
        """Test for substitute()."""
        inst = Sum(self.A + self.B, A=Range((self.A, self.C, self.n1)))

        self.assertEqual(inst.substitute(A=self.n2),
                         Sum(self.A + self.B,
                             A=Range((self.n2, self.C, self.n1))))
        self.assertEqual(inst.substitute(B=self.n2),
                         Sum(self.A + self.n2,
                             A=Range((self.A, self.C, self.n1))))
        self.assertEqual(inst.substitute(C=self.n2),
                         Sum(self.A + self.B,
                             A=Range((self.A, self.n2, self.n1))))

    def test_simplify(self):
        """Test for simplify()."""
        self.assertEqual(Sum(self.A * self.n1,
                             A=Range((self.B, self.n2, self.n3)))(),
                         Sum((self.A * self.n1)(),
                             A=Range((self.B, self.n2, self.n3))))
        self.assertEqual(Sum(self.A,
                             A=Range((self.B * self.n1, self.n2, self.n3)))(),
                         Sum(self.A,
                             A=Range((self.B * self.n1, self.n2, self.n3))()))

        self.assertEqual(Sum(self.A, B=range(self.n1))(), self.n1 * self.A)
        self.assertEqual(Sum(self.A + self.B, A=range(self.n1))(),
                         sum(A + self.B for A in range(self.n1))())


if __name__ == "__main__":
    unittest.main()
