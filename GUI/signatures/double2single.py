#!/usr/bin/env python
from __future__ import division, print_function

import os
import sys


def main():
    override = len(sys.argv) > 1

    for path, dirs, files in os.walk(os.path.join(".")):
        for dfilename in files:
            if dfilename[0] != "d" or dfilename[-6:] != ".pysig":
                continue
            sfilename = "s" + dfilename[1:]
            if not override and sfilename in files:
                # don't override existing sigs
                continue

            droutinename = dfilename[:-6]

            sroutinename = "s" + droutinename[1:]
            with open(os.path.join(path, dfilename)) as fin:
                dsigstr = fin.read()
            ssigstr = dsigstr

            ssigstr = ssigstr.replace(droutinename, sroutinename)
            ssigstr = ssigstr.replace("double precision", "single precision")
            ssigstr = ssigstr.replace("dScalar", "sScalar")
            ssigstr = ssigstr.replace("dData", "sData")

            with open(os.path.join(path, sfilename), "w") as fout:
                fout.write(ssigstr)

            print(dfilename, "->", sfilename)

if __name__ == "__main__":
    main()
