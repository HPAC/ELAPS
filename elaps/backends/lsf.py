#!/usr/bin/env python
"""Backend for running ELAPS:Mat jobs through LSF."""
from __future__ import division, print_function

import subprocess
import re


class Backend(object):

    """Backend to run ELAPS:Mat jobs through an LSF scheduler."""

    name = "lsf"

    def __init__(self, header="#!/bin/bash -l\n#BSUB -o /dev/null\n"):
        """Initialize the backend."""
        self.jobs = []
        self.header = header

    def submit(self, script, nt=1, jobname="", header="", **options):
        """Submit a job."""
        p = subprocess.Popen(["bsub"], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        header = self.header + header
        header += "#BSUB -J " + str(jobname) + "\n"
        (out, err) = p.communicate(header + script)
        match = re.search("Job <(\d+)> is submitted to queue <.*>\.", out)
        if not match:
            raise IOError(err)
        jobid = int(match.groups()[0])
        self.jobs.append(jobid)
        return jobid

    def poll(self, jobid):
        """Poll a job's status."""
        out = subprocess.check_output(["bjobs", "-o", "stat", "-noheader",
                                       str(jobid)])
        if out:
            return out[:-1]
        return "UNKNOWN"

    def kill(self, jobid):
        """Kill a job."""
        subprocess.check_output(["bkill", str(jobid)])
