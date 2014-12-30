#!/usr/bin/env python
from __future__ import division, print_function


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


class Symbol(Expression):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

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

    def __call__(self, **kwargs):
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

    def __call__(self, **kwargs):
        return self.substitute(**kwargs).simplify()


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
        if isinstance(arg, (int, long, float, complex)):
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
        if istinstance(Arg, (int, long, float, complex)):
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
                args += arg[1:]
            elif isinstance(arg, (int, long, float, complex)):
                num *= arg
            else:
                args.append(arg)
        if num != 1:
            args = [num] + args
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
                args += arg[1:]
            elif isinstance(arg, (int, long, float, complex)):
                num += arg
            else:
                args.append(arg)
        if num != 0:
            args = [num] + args
        if len(args) == 1:
            return args[0]
        return self.__class__(*args)
