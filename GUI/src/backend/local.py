#!/usr/bin/env python
from __future__ import division, print_function

from backend import Backend

import subprocess
import thrading


class BackendLocal(Backend):
    def __init__(self):
        Backend.__init__(self)
        self.jobs = {}
        self.scripts = {}
        self.lastsubmitted = None

    def _run(self, jobid, waitid=None):
        if waitid:
            self.jobs[waitid].wait()
        p = self.jobs[jobid]
        p.stdin.write(self.scripts[jobid])
        del self.scripts[jobid]
        p.stdin.close()

    def submit(self, script):
        p = subprocess.Popen(["bash"], stdin=subprocess.PIPE)
        jobid = p.pid
        self.jobs[jobid] = p
        self.scripts[jobid] = script
        t = thrading.Thread(target=self._run, args=(jobid, self.lastsubmitted))
        t.start()
        self.lastsubmitted = jobid
        return jobid

    def poll(self, jobid):
        if jobid in self.scripts:
            return "PEND"
        returncode = self.jobs[jobid].poll()
        if returncode is None:
            return "RUN"
        if returncode != 0:
            return "EXIT"
        return "DONE"

    def wait(self, jobid):
        returncode = self.jobs[jobid].wait()
        if returncode != 0:
            return "EXIT"
        return "DONE"

    def kill(self, jobid):
        self.jobs[jobid].terminate()
