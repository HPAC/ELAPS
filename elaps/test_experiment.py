#!/usr/bin/env python
"""Unittest for experiment.py."""
from __future__ import division, print_function

from experiment import *

import unittest
import random

class TestExperiment(unittest.TestCase):

    """Tests for Experiment."""

    def test_init(self):
        """Test for __init__() and attribute access"""
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

    def


if __name__ == "__main__":
    unittest.main()
