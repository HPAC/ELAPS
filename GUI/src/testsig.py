#!/usr/bin/env python
from __future__ import division, print_function

from signature import Signature


def main():
    sig = Signature(file="../signatures/blas/3/dsymm_.pysig")
    print(sig)
    print(repr(sig))
    call = sig.create_call()
    print(call)
    call.m = 10
    call.n = 20
    print(call)
    call.complete()
    print(call)
    print(tuple(call))
    print(repr(call))


if __name__ == "__main__":
    main()
