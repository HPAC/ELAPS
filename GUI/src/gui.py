#!/usr/bin/env python
from __future__ import division, print_function

import sys
import os

from PyQt4 import QtCore, QtGui


class GUI(QtGui.QApplication):
    def __init__(self):
        # QtGui.QApplication.__init__(self, sys.argv)

        pathprefix = ""
        if os.getcwd().endswith("src/"):
            pathprefix = "../"
        self.systems = {}
        for path, dirs, files in os.walk(pathprefix + "../Sampler/build/"):
            if "info.py" in files and "sampler.x" in files:
                with open(path + "/info.py") as fin:
                    system = eval(fin.read())
                system["sampler"] = path + "/sampler.x"
                self.systems[system["name"]] = system
        print(self.systems)


def main():
    gui = GUI()

if __name__ == "__main__":
    main()
