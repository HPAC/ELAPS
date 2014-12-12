#!/usr/bin/env python
from __future__ import division, print_function

from symbolic import Symbol


def main():
    A = Symbol("A")
    B = Symbol("B")
    C = Symbol("C")
    print(A, B, C)
    D = 2 * A + B * C * A
    print(D)
    E = D.substitute(A=5)
    print(E)
    F = E.simplify()
    print(F)

if __name__ == "__main__":
    main()
