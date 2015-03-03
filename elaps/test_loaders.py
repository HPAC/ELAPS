#!/usr/bin/env python
"""Unittest for loaders.py."""
from __future__ import division, print_function

from loaders import *
from signature import *
from experiment import Experiment

import unittest
import glob


class TestLoaders(unittest.TestCase):

    """Tests for loaders."""

    def setUp(self):
        """Test file creation."""
        self.filebase = "test_loaders.py_tmp"

    def tearDown(self):
        """Delete remporary files."""
        for filename in glob.glob(self.filebase + "*"):
            os.remove(filename)

    def test_load_signature_file(self):
        """Test for load_signature_file()."""
        sig = Signature("adsf", Dim("m"), sData("A", "m * m"))
        filename = self.filebase + ".pysig"
        with open(filename, "w") as fout:
            fout.write(repr(sig))
        self.assertEqual(load_signature_file(filename), sig)

    def test_load_signature(self):
        """Test for load_signature()."""
        sig = load_signature("dtrsm_")
        self.assertIsInstance(sig, Signature)

    def test_load_expeirment(self):
        """Test for load_experiment()."""
        ex = Experiment(note="adsf")
        filename = self.filebase + ".ees"
        with open(filename, "w") as fout:
            fout.write(repr(ex))
        self.assertEqual(load_experiment(filename), ex)


if __name__ == "__main__":
    unittest.main()
