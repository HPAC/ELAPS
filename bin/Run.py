#!/usr/bin/env python
"""Execute ELAPS:Experiments."""
from __future__ import division, print_function

# set path to load the lib
import sys
import os
filepath = os.path.dirname(os.path.realpath(__file__))
rootpath = os.path.abspath(os.path.join(filepath, ".."))
sys.path.append(rootpath)

import elaps.io
import elaps.defines as defines


def main():
    """Main entry point."""
    jobs = []
    for filename in sys.argv[1:]:
        # load experiment
        try:
            ex = elaps.io.load_experiment(filename)
        except:
            print("ERROR: Can't load %r" % filename, file=sys.stderr)
            continue
        print("Loaded %r" % filename)

        # submit
        filebase = filename
        if (filename[-4] == "." and
                filename[-3:] in defines.experiment_extensions):
            filebase = filename[:-4]
        try:
            jobid = ex.submit(filebase)
        except:
            print("ERROR: Can't run %r" % filename, file=sys.stderr)
            continue
        print("Started %r" % filename)

        # wait for local experiments
        if ex.sampler["backend_name"] == "local":
            # TOTO: jobprogress
            ex.sampler["backend"].wait(jobid)
            print("Completed %r" % filename)

if __name__ == "__main__":
    main()
