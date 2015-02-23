#!/usr/bin/env python
"""Backend sekeleton for ELAPS:Mat jobs."""
from __future__ import division, print_function


class Backend(object):

    """Base class for backends for ELAPS:Mat jobs."""

    def submit(self, script, **options):
        """Submit a job."""
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'submit'")

    def poll(self, jobid):
        """Poll a job's state."""
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'poll'")

    def wait(self, jobid):
        """Wait for a job to complete."""
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'wait'")

    def kill(self, jobid):
        """Kill a job."""
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'kill'")
