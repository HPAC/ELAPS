#!/usr/bin/env python
from __future__ import division, print_function

import sys


def main():
    print("#ifndef KERNELS_H")
    print("#define KERNELS_H")
    for f in sys.argv[1:]:
        print("#include \"" + f + "\"")
    print("#endif /* KERNELS_H */")


if __name__ == "__main__":
    main()
