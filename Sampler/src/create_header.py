#!/usr/bin/env python
from __future__ import division, print_function

import os


def main():
    print("#ifndef KERNELS_H")
    print("#define KERNELS_H")
    for f in os.environ["KERNEL_HEADERS"].split():
        print("#include \"" + f + "\"")
    print("#endif /* KERNELS_H */")


if __name__ == "__main__":
    main()
