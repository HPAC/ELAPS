#!/usr/bin/env python
from __future__ import division, print_function

import sys
import re


def main():
    if len(sys.argv) != 6:
        print("usage: gcc -E kernel.h ", sys.argv[0],
              "cfg.h kernel.h sigs.c.ing calls.c.inc papi_max_counters",
              file=sys.stderr)
        return
    cfg_h = sys.argv[1]
    kernel_h = sys.argv[2]
    sigs_c_inc = sys.argv[3]
    calls_c_inc = sys.argv[4]
    papi_max_counters = int(sys.argv[5])

    # read and prepare kernels
    kernels = sys.stdin.read()

    # clean kernel.h
    for p, s in (
            ("#.*\n", ""),
            ("\n", ""),
            ("{[^{]*?}", ""),
            ("typedef .*?;", ""),
            (";extern ", ";"),
            ("\s+", " "),
            (", ", ","),
            (" ?\( ?", "("),
            (" \)", ")"),
            ("; ?", ";\n"),
            (" \*", "*"),
            ("\*\w+", "*")):
        kernels = re.sub(p, s, kernels)
    kernels = kernels.split("\n")[:-1]

    # create sigs.c.inc
    argtypes = {
        "char*": "CHARP",
        "int*": "INTP",
        "float*": "FLOATP",
        "double*": "DOUBLEP",
        "void*": "VOIDP",
    }
    argcmax = 0
    with open(sigs_c_inc, "w") as fout:
        for line in kernels:
            match = re.match("(?:extern )?\w+ (\w+)\(([^)]*)\);", line)
            if not match:
                print(line, file=sys.stdout)
            name, args = match.groups()
            if args:
                args = [argtypes[arg] for arg in args.split(",")]
            else:
                args = []
            argcmax = max(argcmax, len(args) + 1)
            print("{\"" + name + "\", (void *) " + name + ", { " +
                  ", ".join(args) + " } },", file=fout)

    # create calls.s.cin
    with open(calls_c_inc, "w") as fout:
        for argc in range(1, argcmax + 1):
            print("case " + str(argc) + ":", file=fout)
            print("\tCOUNTERS_START();", file=fout)
            voidlist = (argc - 1) * ["void *"]
            arglist = ["argv[" + str(n) + "]" for n in range(1, argc)]
            print("\t((void (*)(" + ",".join(voidlist) + ")) argv[0])(" +
                  ",".join(arglist) + ");", file=fout)
            print("\tCOUNTERS_END();", file=fout)
            print("\t break;", file=fout)

    # create cfg.h
    with open(cfg_h, "w") as fout:
        print("#ifndef SAMPLERCFG_H", file=fout)
        print("#define SAMPLERCFG_H", file=fout)
        print("#define KERNEL_H \"" + kernel_h + "\"", file=fout)
        print("#define SIGS_C_INC \"" + sigs_c_inc + "\"", file=fout)
        print("#define CALLS_C_INC \"" + calls_c_inc + "\"", file=fout)
        print("#define KERNEL_MAX_ARGS", argcmax, file=fout)
        if papi_max_counters > 0:
            print("#define PAPI", file=fout)
            print("#define MAX_COUNTERS", papi_max_counters, file=fout)
        print("#endif /* SAMPLERCFG_H */", file=fout)

if __name__ == "__main__":
    main()
