#!/usr/bin/env python
"""Dynamic include header."""
from __future__ import division, print_function

import os


def main():
    """Generate C kernel include directives."""
    print("#ifndef KERNELS_H")
    print("#define KERNELS_H")
    print()
    for var in ("BLAS_UNDERSCORE", "BLAS_COMPLEX_FUNCTIONS_AS_ROUTINES",
                "LAPACK_UNDERSCORE", "LAPACK_COMPLEX_FUNCTIONS_AS_ROUTINES"):
        print("#define", var, os.environ[var])
    print()
    for f in os.environ["KERNEL_HEADERS"].split():
        print("#include \"" + f + "\"")
    print()
    print("#endif /* KERNELS_H */")


if __name__ == "__main__":
    main()
