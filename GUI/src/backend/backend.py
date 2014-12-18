#!/usr/bin/env python
from __future__ import division, print_function


class Backend(object):
    def __init__(self):
        pass

    def submit(self, options, script):
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'submit'")

    def poll(self, jobid):
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'poll'")

    def wait(self, jobid):
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'wait'")

    def kill(self, jobid):
        raise NotImplementedError(self.__class__.__name__
                                  + " does not implement 'kill'")
