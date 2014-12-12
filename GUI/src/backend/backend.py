#!/usr/bin/env python
from __future__ import division, print_function


class Backend(object):
    PENDING = 1
    RUNNING = 2
    DONE = 3
    FAILED = 4

    def __init__(self):
        self.jobs = {}

    def submit(self, script):
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'submit'")

    def poll(self, script):
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'poll'")

    def wait(self, script):
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'wait'")

    def kill(self, script):
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'kill'")
