#!/usr/bin/env python
"""Backend for running ELAPS:Mat jobs locally."""
from __future__ import division, print_function

from backend import Backend

import subprocess
import threading


class local(Backend):

    """Backend to run ELAPS:Mat jobs locally in the background."""

    def __init__(self):
        """Initialize the backend."""
        Backend.__init__(self)
        self.jobs = {}
        self.scripts = {}
        self.lastsubmitted = None

    def _run(self, jobid, waitid=None):
        """Delayed start of a job."""
        if waitid:
            self.jobs[waitid].wait()
        p = self.jobs[jobid]
        p.stdin.write(self.scripts[jobid])
        del self.scripts[jobid]
        p.stdin.close()

    def submit(self, script, nt=1, header="", **options):
        """Submit a job."""
        p = subprocess.Popen(["bash"], stdin=subprocess.PIPE)
        jobid = p.pid
        self.jobs[jobid] = p
        header += "export OPM_NUM_THREADS=%d\n" % nt
        self.scripts[jobid] = header + script
        t = threading.Thread(target=self._run,
                             args=(jobid, self.lastsubmitted))
        t.daemon = True
        t.start()
        self.lastsubmitted = jobid
        return jobid

    def poll(self, jobid):
        """Poll a job's status."""
        if jobid in self.scripts:
            return "PEND"
        returncode = self.jobs[jobid].poll()
        if returncode is None:
            return "RUN"
        if returncode != 0:
            return "EXIT"
        return "DONE"

    def wait(self, jobid):
        """Wait for a job to comple."""
        returncode = self.jobs[jobid].wait()
        if returncode != 0:
            return "EXIT"
        return "DONE"

    def kill(self, jobid):
        """Kill a job."""
        self.jobs[jobid].terminate()
