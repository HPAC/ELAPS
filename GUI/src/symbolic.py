#!/usr/bin/env python
from __future__ import division, print_function

import numbers
import __builtin__


class Expression(object):
    def __neg__(self):
        return Minus(self)

    def __add__(self, other):
        return Plus(self, other)

    def __radd__(self, other):
        return Plus(other, self)

    def __sub__(self, other):
        return Plus(self, Minus(other))

    def __rsub__(self, other):
        return Plus(other, Minus(self))

    def __mul__(self, other):
        return Prod(self, other)

    def __rmul__(self, other):
        return Prod(other, self)

    def __pow__(self, other):
        return Power(self, other)

    def subistitute(self, **kwargs):
        return self

    def simplify(self):
        return self

    def __call__(self, **kwargs):
        expr = self.substitute(**kwargs)
        if isinstance(expr, Expression):
            return expr.simplify()
        return expr


class Symbol(Expression):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self.name) + ")"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, Symbol):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def substitute(self, **kwargs):
        if self.name in kwargs:
            return kwargs[self.name]
        else:
            return self


class Operation(Expression, list):
    def __new__(cls, *args):
        if any(arg is None for arg in args):
            return None
        else:
            return list.__new__(cls)

    def __init__(self, *args):
        list.__init__(self, (self.__class__,) + args)

    def __repr__(self):
        return (self.__class__.__name__ + "(" +
                ", ".join(map(repr, self[1:])) + ")")

    def __hash__(self):
        return hash(tuple(map(hash, self)))

    def substitute(self, **kwargs):
        args = []
        for arg in self[1:]:
            if arg in kwargs:
                args.append(kwargs[arg.name])
            elif isinstance(arg, Operation):
                args.append(arg.substitute(**kwargs))
            else:
                args.append(arg)
        return self.__class__(*args)


class Minus(Operation):
    def __init__(self, expression):
        Operation.__init__(self, expression)

    def __str__(self):
        return "-" + str(self[1])

    def simplify(self):
        arg = self[1]
        if isinstance(arg, Operation):
            arg = arg.simplify()
        if isinstance(arg, Minus):
            return arg[1]
        if isinstance(arg, numbers.Number):
            return -arg
        return self.__class__(arg)


class Abs(Operation):
    def __init__(self, expression):
        Operation.__init__(self, expression)

    def __str__(self):
        return "abs(" + str(self[1]) + ")"

    def simplify(self):
        arg = self[1]
        if isinstance(arg, Operation):
            arg = arg.simplify()
        if isinstance(arg, Abs):
            return arg[1]
        if isinstance(arg, numbers.Number):
            return abs(arg)
        return self.__class__(arg)


class Prod(Operation):
    def __init__(self, *args):
        Operation.__init__(self, *args)

    def __str__(self):
        strs = map(str, self[1:])
        for i, arg in enumerate(self[1:]):
            if isinstance(arg, Plus):
                strs[i] = "(" + strs[i] + ")"
        return " * ".join(strs)

    def simplify(self):
        num = 1
        args = []
        for arg in self[1:]:
            if isinstance(arg, Operation):
                arg = arg.simplify()
            if isinstance(arg, Prod):
                otherargs = arg[1:]
                if isinstance(otherargs[0], numbers.Number):
                    num *= otherargs[0]
                    otherargs = otherargs[1:]
                args += otherargs
            elif isinstance(arg, numbers.Number):
                num *= arg
            else:
                args.append(arg)
        if num != 1:
            args = [num] + args
        if len(args) == 0:
            return 1
        if len(args) == 1:
            return args[0]
        return self.__class__(*args)


class Plus(Operation):
    def __init__(self, *args):
        Operation.__init__(self, *args)

    def __str__(self):
        return " + ".join(map(str, self[1:]))

    def simplify(self):
        num = 0
        args = []
        for arg in self[1:]:
            if isinstance(arg, Operation):
                arg = arg.simplify()
            if isinstance(arg, Plus):
                otherargs = arg[1:]
                if isinstance(otherargs[0], numbers.Number):
                    num += otherargs[0]
                    otherargs = otherargs[1:]
                args += otherargs
            elif isinstance(arg, numbers.Number):
                num += arg
            else:
                args.append(arg)
        if num != 0:
            args = [num] + args
        if len(args) == 0:
            return 0
        if len(args) == 1:
            return args[0]
        return self.__class__(*args)


class Power(Operation):
    def __init__(self, base, exponent):
        Operation.__init__(self, base, exponent)

    def __str__(self):
        strs = map(str, self[1:])
        for i, arg in enumerate(self[1:]):
            if not isinstance(arg, (Symbol, numbers.Number)):
                strs[i] = "(" + strs[i] + ")"
        return strs[0] + " ** " + strs[1]

    def simplify(self):
        base = self[1]
        if isinstance(base, Operation):
            base = base.simplify()
        exponent = self[2]
        if isinstance(exponent, Operation):
            exponent = exponent.simplify()
        if isinstance(exponent, int):
            return Prod(*(exponent * [base])).simplify()
        if isinstance(base, numbers.Number) and isinstance(exponent,
                                                           numbers.Number):
            return base ** exponent
        return self.__class__(base, exponent)


class Min(Operation):
    def __init__(self, *args):
        Operation.__init__(self, *args)

    def __str__(self):
        return "min(" + ", ".join(map(str, self[1:])) + ")"

    def simplify(self):
        num = float("inf")
        args = []
        for arg in self[1:]:
            if isinstance(arg, Operation):
                arg = arg.simplify()
            if isinstance(arg, Min):
                otherargs = arg[1:]
                if isinstance(otherargs[0], numbers.Number):
                    num = min(num, otherargs[0])
                    otherargs = otherargs[1:]
                args += otherargs
            elif isinstance(arg, numbers.Number):
                num = min(num, arg)
            else:
                args.append(arg)
        if num != float("inf"):
            args = [num] + args
        if len(args) == 0:
            return float("-inf")
        if len(args) == 1:
            return args[0]
        return self.__class__(*args)


class Max(Operation):
    def __init__(self, *args):
        Operation.__init__(self, *args)

    def __str__(self):
        return "max(" + ", ".join(map(str, self[1:])) + ")"

    def simplify(self):
        num = float("-inf")
        args = []
        for arg in self[1:]:
            if isinstance(arg, Operation):
                arg = arg.simplify()
            if isinstance(arg, Max):
                otherargs = arg[1:]
                if isinstance(otherargs[0], numbers.Number):
                    num = max(num, otherargs[0])
                    otherargs = otherargs[1:]
                args += otherargs
            elif isinstance(arg, numbers.Number):
                num = max(num, arg)
            else:
                args.append(arg)
        if num != float("-inf"):
            args = [num] + args
        if len(args) == 0:
            return float("inf")
        if len(args) == 1:
            return args[0]
        return self.__class__(*args)


def min_sym(*args, **kwargs):
    if len(args) == 1:
        if any(isinstance(arg, Expression) for arg in args[0]):
            return Min(*args[0])
        return __builtin__.min(*args, **kwargs)
    else:
        if any(isinstance(arg, Expression) for arg in args):
            return Min(*args)
        return __builtin__.min(*args, **kwargs)


def max_sym(*args, **kwargs):
    if len(args) == 1:
        if any(isinstance(arg, Expression) for arg in args[0]):
            return Max(*args[0])
        return __builtin__.max(*args, **kwargs)
    else:
        if any(isinstance(arg, Expression) for arg in args):
            return Max(*args)
        return __builtin__.max(*args, **kwargs)

env = {
    "min": min_sym,
    "max": max_sym,
}

eval_replace = {
    "min(": "min_sym(",
    "max(": "max_sym(",
}
