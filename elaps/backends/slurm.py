#!/usr/bin/env python
"""Backend for running ELAPS:Mat jobs through SLURM."""
from __future__ import division, print_function

import subprocess
import re


class Backend(object):

    """Backend to run ELAPS:Mat jobs through an SLURM scheduler."""

    name = "slurm"

    def __init__(self, header="#!/bin/bash -l\n#SBATCH --output=/dev/null\n"):
        """Initialize the backend."""
        self.jobs = []
        self.header = header

    def submit(self, script, nt=1, jobname="", header="", **options):
        """Submit a job."""
        p = subprocess.Popen(["sbatch"], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        header = self.header + header
        header += "#SBATCH -J " + str(jobname) + "\n"
        (out, err) = p.communicate(header + script)
        match = re.search("Submitted batch job (\d+)", out)
        if not match:
            raise IOError(err)
        jobid = int(match.groups()[0])
        self.jobs.append(jobid)
        return jobid

    def poll(self, jobid):
        """Poll a job's status."""
        out = subprocess.Popen(["squeue", "--job", str(jobid)],
                               stdout=subprocess.PIPE).communicate()[0]
        if out:
            return out[:-1]
        return "UNKNOWN"

    def kill(self, jobid):
        """Kill a job."""
        subprocess.check_output(["scancel", str(jobid)])
