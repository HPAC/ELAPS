#!/usr/bin/env python
"""Unittest for io.py."""

import glob
import unittest

try:
    import elaps
except:
    import os
    import sys
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

from elaps.io import *
from elaps.signature import Signature, Dim, sData
from elaps.experiment import Experiment


class TestLoaders(unittest.TestCase):

    """Tests for loaders."""

    def setUp(self):
        """Test file creation."""
        self.filebase = "test_loaders.py_tmp"

    def tearDown(self):
        """Delete temporary files."""
        for filename in glob.glob(self.filebase + "*"):
            os.remove(filename)

    def test_load_signature_file(self):
        """Test for load_signature_file()."""
        sig = Signature("adsf", Dim("m"), sData("A", "m * m"))
        filename = self.filebase + ".pysig"

        write_signature(sig, filename)
        self.assertEqual(load_signature_file(filename), sig)

    def test_load_signature(self):
        """Test for write/load_signature()."""
        sig = load_signature("dtrsm")
        self.assertIsInstance(sig, Signature)

    def test_load_expeirment(self):
        """Test for write/load_experiment()."""
        ex = Experiment(note="adsf")
        filename = self.filebase + ".ees"
        write_experiment(ex, filename)
        self.assertEqual(load_experiment(filename), ex)

    def test_load_doc_file(self):
        """Test for load_doc_file()."""
        doc = {"adsf": "routine doc", "arg1": "argdoc"}
        filename = self.filebase + ".pydoc"
        with open(filename, "w") as fout:
            fout.write(repr(doc))
        self.assertEqual(load_doc_file(filename), doc)

    def test_load_doc(self):
        """Test for load_doc()."""
        doc = load_doc("dtrsm")
        self.assertEqual(doc[0][0], "dtrsm")

    def test_load_backend(self):
        """Test for load_experiment()."""
        backend = load_backend("local")
        self.assertTrue(hasattr(backend, "submit"))

    def test_load_report(self):
        """Test for load_report()."""
        ex = Experiment(calls=[Signature("name")()], sampler={
            "backend_name": "",
            "backend_header": "",
            "backend_prefix": "prefix{nt}",
            "backend_suffix": "",
            "backend_footer": "",
            "kernels": {},
            "nt_max": 10,
            "exe": "executable"
        })
        filename = self.filebase + ".eer"

        with open(filename, "w") as fout:
            fout.write("%r\n1\n2\n3" % ex)

        load_report(filename)

    def test_load_metric(self):
        """Test for load_metric()."""
        metric = load_metric("efficiency")
        self.assertTrue(hasattr(metric, "name"))

    def test_papinames(self):
        """Test for load_papinames()."""
        papinames = load_papinames()
        self.assertIn("PAPI_TOT_CYC", papinames)


if __name__ == "__main__":
    unittest.main()
