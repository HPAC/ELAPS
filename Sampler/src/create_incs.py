#!/usr/bin/env python
"""Create include files for the Sampler."""
from __future__ import division, print_function

import sys
import os
import re
from time import time
from __builtin__ import intern  # fix for pyflake error


def main():
    """Create include files for the Sampler."""
    if len(sys.argv) != 6:
        print("usage: gcc -E kernel.h | ", sys.argv[0],
              "cfg.h kernel.h sigs.c.ing calls.c.inc info.py",
              file=sys.stderr)
        return
    cfg_h = sys.argv[1]
    kernel_h = sys.argv[2]
    sigs_cpp_inc = sys.argv[3]
    calls_c_inc = sys.argv[4]
    info_py = sys.argv[5]
    papi_counters_max = int(os.environ["PAPI_COUNTERS_MAX"])

    # read and prepare kernels
    kernels = sys.stdin.read().strip()

    # clean kernel.h
    for p, s in (
            ("#.*\n\s*", ""),  # remove comments
            ("\s*\n\s*", ""),  # remove newlines (and surrounding spaces)
            ("\s+", " "),  # all spaces are " "
            ("{[^{]*?}", ""),  # remove anything between {} (no nesting)
            ("typedef .*?;", ""),  # remove typedefs
            (", ", ","),  # remove spaces after kommas
            (" ?\( ?", "("),  # remove spaces before openingparentheses
            (" \)", ")"),  # remove spaces before closing parentheses
            (" \*", "*"),  # remove spaces before asterisks
            ("\* ", "*"),  # remove spaces after asterisks
            ("\*", " *"),  # add spaces before asterisks
            ("\*\w+", "*"),  # remove variable names
            ("; ?", ";\n")):  # reintroduce newlines
        kernels = re.sub(p, s, kernels)
    kernels = kernels.split("\n")[:-1]

    # create sigs.cpp.inc
    argtypes = {
        "char *": "CHARP",
        "int *": "INTP",
        "float *": "FLOATP",
        "double *": "DOUBLEP",
        "void *": "VOIDP",
        "const char *": "CONST_CHARP",
        "const int *": "CONST_INTP",
        "const float *": "CONST_FLOATP",
        "const double *": "CONST_DOUBLEP",
        "const void *": "CONST_VOIDP",
    }
    argcmax = 0
    kernelsigs = []
    with open(sigs_cpp_inc, "w") as fout:
        for line in kernels:
            match = re.match("(?:extern )?\w+ (\w+)\(([^)]*)\);", line)
            if not match:
                print("Could not parse:", repr(line), file=sys.stderr)
                continue

            symbolname, args = match.groups()
            if args:
                args = map(intern, args.split(","))
            else:
                args = []
            name = symbolname
            if name[-1] == "_":
                name = name[:-1]
            kernelsigs.append((name,) + tuple(arg for arg in args))
            enumargs = [argtypes[arg] for arg in args]
            argcmax = max(argcmax, len(enumargs) + 1)
            print("{\"%s\", reinterpret_cast<void (*)()>(%s), { %s } }," %
                  (name, symbolname, ", ".join(enumargs)), file=fout)

    # create calls.s.cin
    with open(calls_c_inc, "w") as fout:
        for argc in range(1, argcmax + 1):
            print("case " + str(argc) + ":", file=fout)
            print("\tCOUNTERS_START", file=fout)
            voidlist = (argc - 1) * ["void *"]
            arglist = ["argv[" + str(n) + "]" for n in range(argc - 1)]
            print("\t((void (*)(" + ", ".join(voidlist) + ")) fptr)(" +
                  ", ".join(arglist) + ");", file=fout)
            print("\tCOUNTERS_END", file=fout)
            print("\tbreak;", file=fout)

    # create cfg.h
    with open(cfg_h, "w") as fout:
        print("#ifndef SAMPLERCFG_H", file=fout)
        print("#define SAMPLERCFG_H", file=fout)
        print("#define KERNEL_H \"" + kernel_h + "\"", file=fout)
        print("#define SIGS_CPP_INC \"" + sigs_cpp_inc + "\"", file=fout)
        print("#define CALLS_C_INC \"" + calls_c_inc + "\"", file=fout)
        print("#define KERNEL_MAX_ARGS", argcmax, file=fout)
        if papi_counters_max > 0:
            print("#define PAPI_ENABLED", file=fout)
            print("#define MAX_COUNTERS", papi_counters_max, file=fout)
        if os.environ["OPENMP"] == "1":
            print("#define OPENMP_ENABLED", file=fout)
        print("#endif /* SAMPLERCFG_H */", file=fout)

    # create info.py
    info = {
        "exe": os.path.abspath(os.path.join(
            os.environ["TARGET_DIR"], "sampler.x"
        )),
        "buildtime": time(),
        "name":  os.environ["NAME"],
        "backend_name": os.environ["BACKEND"],
        "backend_header": os.environ["BACKEND_HEADER"],
        "backend_prefix": os.environ["BACKEND_PREFIX"],
        "backend_suffix": os.environ["BACKEND_SUFFIX"],
        "backend_footer": os.environ["BACKEND_FOOTER"],
        "ncores": int(os.environ["NCORES"]),
        "threads_per_core": int(os.environ["THREADS_PER_CORE"]),
        "nt_max": (int(os.environ["NCORES"]) *
                   int(os.environ["THREADS_PER_CORE"])),
        "kernels": dict((sig[0], sig) for sig in kernelsigs),
        "papi_counters_max": papi_counters_max,
        "papi_enabled": papi_counters_max > 0,
        "omp_enabled": os.environ["OPENMP"] == "1",
        "cpu_model": os.environ["CPU_MODEL"],
        "frequency": float(os.environ["FREQUENCY_HZ"]),
    }
    if papi_counters_max:
        info["papi_counters_avail"] = tuple(
            os.environ["PAPI_COUNTERS_AVAIL"].split()
        )
    else:
        info["papi_counters_avail"] = tuple()
    if "DFLOPS_PER_CYCLE" in os.environ:
        info["dflops/cycle"] = int(os.environ["DFLOPS_PER_CYCLE"])
    if "SFLOPS_PER_CYCLE" in os.environ:
        info["sflops/cycle"] = int(os.environ["SFLOPS_PER_CYCLE"])
    info = info
    with open(info_py, "w") as fout:
        print(repr(info), file=fout)

if __name__ == "__main__":
    main()
