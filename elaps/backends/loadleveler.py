#!/usr/bin/env python
"""Backend for running Experiments through LoadLeveler."""
from __future__ import division, print_function

import os
import subprocess
import re


class Backend(object):

    """Backend to run ELAPS:Mat jobs through a LoadLeveler scheduler."""

    name = "loadleveler"

    def __init__(self, header="#!/bin/bash\n#@ comment=\"ELAPS Experiment\"\n"):
        """Initialize the backend."""
        self.jobs = []
        self.header = header

    def submit(self, script, nt=1, jobname="", header="", **options):
        """Submit a job."""
        p = subprocess.Popen(["llsubmit", "-"], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        header = self.header + header
        header += "#@ job_name=\"%s\"\n" % jobname
        (out, err) = p.communicate(header + script)
        match = re.search("llsubmit: The job \"(.+)\" has been submitted.", out)
        if not match:
            raise IOError(err)
        jobid = match.groups()[0]
        self.jobs.append(jobid)
        return jobid

    def poll(self, jobid):
        """Poll a job's status."""
        out = subprocess.Popen(["llq", "-j", str(jobid)],
                               stdout=subprocess.PIPE).communicate()[0]
        if "1 waiting" in out:
            return "PEND"
        if "1 pending" in out:
            return "PEND"
        if "1 running" in out:
            return "RUN"
        return "DONE"

    def kill(self, jobid):
        """Kill a job."""
        with open(os.devnull, "wb") as devnull:
            subprocess.call(["llcancel", str(jobid)], stdout=devnull)
