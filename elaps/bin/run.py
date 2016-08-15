#!/usr/bin/env python
"""Execute ELAPS:Experiments."""
from __future__ import division, print_function

from .. import defines
from .. import io as elapsio

import argparse


def main():
    """Main entry point."""
    # parser args
    parser = argparse.ArgumentParser(
        description="Run ELAPS Experiments (.ele, .elr)"
    )
    attr = parser.add_argument_group("Experiment attributes")
    attr.add_argument("--note")
    attr.add_argument("--sampler")
    attr.add_argument("--papi_counters")
    attr.add_argument("--nthreads", type=int)
    attr.add_argument("--nreps", type=int)
    parser.add_argument(
        "experiment", nargs="+", help="ELAPS Experiment (.%s) or Report (.%s)" %
        (defines.experiment_extension, defines.report_extension)
    )
    args = parser.parse_args()

    # collect attributes from args
    replace = {}
    for attr in ("note", "nthreads", "nreps"):
        if getattr(args, attr):
            replace[attr] = getattr(args, attr)
    if args.sampler:
        replace["sampler"] = elapsio.load_sampler(args.sampler)
    if args.papi_counters:
        replace["papi_counters"] = args.papi_counters.split(",")

    jobs = []
    for filename in args.experiment:
        # load experiment
        try:
            ex = elapsio.load_experiment(filename)
        except:
            print("ERROR: Can't load %r" % filename, file=sys.stderr)
            continue
        print("Loaded %r" % filename)

        for key, value in replace.items():
            setattr(ex, key, value)

        if "sampler" not in replace:
            ex.sampler = elapsio.load_sampler(ex.sampler["name"])

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
