#!/usr/bin/env python
from __future__ import division, print_function

from backend import Backend

import subprocess
import re


class lsf(Backend):
    def __init__(self, header=("#!/bin/bash -l\n"
                               "#BSUB -W 2:00\n")):
                               # "#BSUB -o /dev/null\n"
        Backend.__init__(self)
        self.jobs = []
        self.header = header

    def submit(self, script, nt=1, jobname="", header="", **options):
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
        out = subprocess.check_output(["bjobs", "-o", "stat", "-noheader",
                                       str(jobid)])
        if out:
            return out[:-1]
        return "UNKNOWN"

    def kill(self, jobid):
        subprocess.check_output(["bkill", str(jobid)])
