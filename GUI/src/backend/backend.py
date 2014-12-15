#!/usr/bin/env python
from __future__ import division, print_function


class Backend(object):
    def __init__(self):
        pass

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
