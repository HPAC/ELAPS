#!/usr/bin/env python
"""Backend for running ELAPS:Mat jobs locally."""
from __future__ import division, print_function

import os
import subprocess
import threading


class Backend(object):

    """Backend to run ELAPS:Mat jobs locally in the background."""

    name = "local"

    def __init__(self):
        """Initialize the backend."""
        self.jobs = {}
        self.scripts = {}
        self.lastsubmitted = None

    def _run(self, jobid, waitid=None):
        """Delayed start of a job."""
        if waitid:
            self.jobs[waitid].wait()
        p = self.jobs[jobid]
        if p.poll() is not None:
            # job killed
            return
        p.stdin.write(self.scripts[jobid])
        del self.scripts[jobid]
        p.stdin.close()

    def submit(self, script, nt=1, header="", **options):
        """Submit a job."""
        p = subprocess.Popen(["bash"], stdin=subprocess.PIPE,
                             preexec_fn=os.setsid)
        jobid = p.pid
        self.jobs[jobid] = p
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
        try:
            os.killpg(os.getpgid(jobid), 15)
        except:
            pass
