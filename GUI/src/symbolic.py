#!/usr/bin/env python
"""Simple symbolic expression engine."""
from __future__ import division, print_function

import numbers
import __builtin__
from copy import deepcopy


class Expression(object):

    """Base class for all expressions."""

    def __neg__(self):
        """-Expression ."""
        return Minus(self)

    def __add__(self, other):
        """Expression + Other ."""
        return Plus(self, other)

    def __radd__(self, other):
        """Other + Expression ."""
        return Plus(other, self)

    def __sub__(self, other):
        """Expression - Other ."""
        return Plus(self, Minus(other))

    def __rsub__(self, other):
        """Other - Expression ."""
        return Plus(other, Minus(self))

    def __mul__(self, other):
        """Expression * Other ."""
        return Prod(self, other)

    def __rmul__(self, other):
        """Other * Expression ."""
        return Prod(other, self)

    def __pow__(self, other):
        """Expression ** Other ."""
        return Power(self, other)

    def subistitute(self, **kwargs):
        """Variable substitution."""
        return self

    def simplify(self):
        """Simplify the expression."""
        return self

    def __call__(self, **kwargs):
        """Substitution and simplification."""
        expr = self
        if kwargs:
            expr = expr.substitute(**kwargs)
        if isinstance(expr, Expression):
            expr = expr.simplify()
        return expr


class Symbol(Expression):

    """Symbolic variable."""

    def __init__(self, name):
        """Initialize: remember the name."""
        self.name = name

    def __str__(self):
        """Format as human readable."""
        return str(self.name)

    def __repr__(self):
        """Format as python parsable string."""
        return "%s(%r)" % (self.__class__.__name__, self.name)

    def __eq__(self, other):
        """Compare for equality."""
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, Symbol):
            return self.name == other.name
        return False

    def __hash__(self):
        """Hash: hash name."""
        return hash(self.name)

    def substitute(self, **kwargs):
        """Substitute: return value if matching."""
        if self.name in kwargs:
            return kwargs[self.name]
        else:
            return self

    def findsymbols(self):
        """Find all contained symbols: self is a symbol."""
        return set([self.name])


class Operation(Expression, list):

    """Base class for symbolic operations."""

    def __new__(cls, *args):
        """If any argument is None, the operation is None."""
        if any(arg is None for arg in args):
            return None
        else:
            return list.__new__(cls)

    def __init__(self, *args):
        """Initialize as a list with the operation as first element."""
        list.__init__(self, (self.__class__,) + args)

    def __repr__(self):
        """Python parsable representation."""
        return (self.__class__.__name__ + "(" +
                ", ".join(map(repr, self[1:])) + ")")

    def __hash__(self):
        """Hash the expression."""
        return hash(tuple(map(hash, self)))

    def substitute(self, **kwargs):
        """Substitute in all arguments."""
        args = []
        for arg in self[1:]:
            if arg in kwargs:
                # argument found
                args.append(kwargs[arg.name])
            elif isinstance(arg, Operation):
                # try to substitute in argument
                args.append(arg.substitute(**kwargs))
            else:
                args.append(arg)
        return self.__class__(*args)

    def findsymbols(self):
        """Find all contained symbols."""
        symbols = set()
        for arg in self[1:]:
            if isinstance(arg, Expression):
                symbols |= arg.findsymbols()
        return symbols


class Minus(Operation):

    """-Expression (unary)."""

    def __init__(self, expression):
        """Initialize: Only one argument."""
        Operation.__init__(self, expression)

    def __str__(self):
        """Format as human readable."""
        return "-" + str(self[1])

    def simplify(self):
        """Simplify the operation."""
        # simplify argument
        arg = simplify(self[1])
        if isinstance(arg, Minus):
            # double negation
            return arg[1]
        if isinstance(arg, numbers.Number):
            # evaluate for numbers
            return -arg
        return self.__class__(arg)


class Abs(Operation):

    """abs(Expression) (unary)."""

    def __init__(self, expression):
        """Initialize: Only one argument."""
        Operation.__init__(self, expression)

    def __str__(self):
        """Format as human readable."""
        return "abs(" + str(self[1]) + ")"

    def simplify(self):
        """Simblify the operation."""
        # simplify argument
        arg = simplify(self[1])
        if isinstance(arg, Abs):
            # redundand recursive abs
            return arg[1]
        if isinstance(arg, numbers.Number):
            # evaluate for numbers
            return abs(arg)
        return self.__class__(arg)


class Prod(Operation):

    """Product of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format as human readable."""
        strs = map(str, self[1:])
        for i, arg in enumerate(self[1:]):
            if isinstance(arg, Plus):
                # parantheses around sums
                strs[i] = "(" + strs[i] + ")"
        return " * ".join(strs)

    def simplify(self):
        """Simplify the operation."""
        num = 1
        args = []
        for arg in self[1:]:
            # simplify arg
            arg = simplify(arg)
            if isinstance(arg, Prod):
                # flatten recursive Prod
                otherargs = arg[1:]
                if isinstance(otherargs[0], numbers.Number):
                    num *= otherargs[0]
                    otherargs = otherargs[1:]
                args += otherargs
            elif isinstance(arg, numbers.Number):
                # multiply numbers
                num *= arg
            else:
                args.append(arg)
        if num != 1:
            # numeric part present
            args = [num] + args
        if len(args) == 0:
            # empty Prod = 1
            return 1
        if len(args) == 1:
            # single argument
            return args[0]
        return self.__class__(*args)


class Plus(Operation):

    """Sum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format as human readable."""
        return " + ".join(map(str, self[1:]))

    def simplify(self):
        """Simplify the operation."""
        num = 0
        args = []
        for arg in self[1:]:
            # simplify arg
            arg = simplify(arg)
            if isinstance(arg, Plus):
                # flatten recursive Plus
                otherargs = arg[1:]
                if isinstance(otherargs[0], numbers.Number):
                    num += otherargs[0]
                    otherargs = otherargs[1:]
                args += otherargs
            elif isinstance(arg, numbers.Number):
                # sum numbers
                num += arg
            else:
                args.append(arg)
        if num != 0:
            # numeric part present
            args = [num] + args
        if len(args) == 0:
            # empty Plus = 0
            return 0
        if len(args) == 1:
            # single argument
            return args[0]
        return self.__class__(*args)


class Power(Operation):

    """Power with an experssion as the base."""

    def __init__(self, base, exponent):
        """Init: Two exactly arguments."""
        Operation.__init__(self, base, exponent)

    def __str__(self):
        """Format as human readable."""
        strs = map(str, self[1:])
        for i, arg in enumerate(self[1:]):
            if isinstance(arg, Operation):
                # paranteses around any Operation
                strs[i] = "(" + strs[i] + ")"
        return strs[0] + " ** " + strs[1]

    def simplify(self):
        """Simplify the operation."""
        # simplify base and exponent
        base, exponent = map(simplify, self[1:])
        if isinstance(exponent, int):
            # expand for integer exponent
            return Prod(*(exponent * [base]))()
        if (isinstance(base, numbers.Number) and
                isinstance(exponent, numbers.Number)):
            # evaluate for numbers
            return base ** exponent
        return self.__class__(base, exponent)


class Min(Operation):

    """Minimum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format as human readable."""
        return "min(" + ", ".join(map(str, self[1:])) + ")"

    def simplify(self):
        """Simplify the operation."""
        num = float("inf")
        args = []
        for arg in self[1:]:
            # simplify arg
            arg = simplify(arg)
            if isinstance(arg, Min):
                # flatten recursive Min
                otherargs = arg[1:]
                if isinstance(otherargs[0], numbers.Number):
                    num = min(num, otherargs[0])
                    otherargs = otherargs[1:]
                args += otherargs
            elif isinstance(arg, numbers.Number):
                # minimum of numbers
                num = min(num, arg)
            else:
                args.append(arg)
        if num != float("inf"):
            # numeric part present
            args = [num] + args
        if len(args) == 0:
            # empty Min == -inf
            return float("-inf")
        if len(args) == 1:
            # single argument
            return args[0]
        return self.__class__(*args)


class Max(Operation):

    """Maximum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format as human readable."""
        return "max(" + ", ".join(map(str, self[1:])) + ")"

    def simplify(self):
        """Simplify the operation."""
        num = float("-inf")
        args = []
        for arg in self[1:]:
            # simplify arg
            arg = simplify(arg)
            if isinstance(arg, Max):
                # flatten recursive Max
                otherargs = arg[1:]
                if isinstance(otherargs[0], numbers.Number):
                    num = max(num, otherargs[0])
                    otherargs = otherargs[1:]
                args += otherargs
            elif isinstance(arg, numbers.Number):
                # maximum of numbers
                num = max(num, arg)
            else:
                args.append(arg)
        if num != float("-inf"):
            # numeric part present
            args = [num] + args
        if len(args) == 0:
            # empty Max = inf
            return float("inf")
        if len(args) == 1:
            # single argument
            return args[0]
        return self.__class__(*args)


class Range(object):

    """Complex range object (possibly containing Expressions)."""

    def __init__(self, *args, **kwargs):
        """Initialize from tuples or string."""
        self.subranges = []
        if len(args) == 1 and isinstance(args[0], str):
            # initialize from string

            # for each subrange
            rangepart = args[0].split(",")
            for rangepart in rangeparts:
                # format: min[[:step]:max]
                parts = rangepart.strip().split(":")
                parts = [eval(part, {}, kwargs) for part in parts]
                if len(parts) == 1:
                    # only min: step = 1, max = min
                    subrange = (parts[0], 1, parts[0])
                elif len(parts) == 2:
                    # min and max: step = 1
                    subrange = (parts[0], 1, parts[1])
                elif len(parts) == 3:
                    # min, step, and max
                    subrange = (parts[0], parts[1], parts[2])
                else:
                    # too many ":"s
                    raise Exception("Inavlid subrange: %r" % rangepart)
                self.subranges.append(subrange)
        elif len(args) == 1 and isinstance(args[0], Range):
            # initialize from other range
            self.subranges = deepcopy(args[0].subranges)
        else:
            # initialize from list of tuples
            for arg in args:
                # check form of subrange
                if not isinstance(arg, tuple) or len(arg) != 3:
                    raise Exception("Invalid subrange: %r" % arg)
                # check contents of subrange
                for val in arg:
                    if not isinstance(val, (numbers.Number, Expression)):
                        raise Exception("Invalid value in range:%r" % arg)
                self.subranges.append(arg)

    def min(self):
        """compute the minimum."""
        # default minimum: inf
        result = float("inf")

        # consider all subranges
        for subrange in self.subranges:
            if not all(isinstance(val, numbers.Number) for val in subrange):
                # can only get the min for non-symbolic ranges
                raise Exception("Not numberic: %r" % subrange)

            # min depends on range direction
            start, step, stop = subrange
            if step > 0:
                # positive direction: start is smallest
                if start <= stop:
                    result = min(result, start)
            elif step == 0:
                # no direction: start is smallest
                if start == stop:
                    result = min(result, start)
            else:
                # negative direction: last is smallest
                if start >= stop:
                    result = min(result,
                                 start + ((stop - start) // step) * step)

        return result

    def max(self):
        """Compute the maximum."""
        # default maximum: -inf
        result = -float("inf")

        # consider all subranges
        for subrange in self.subranges:
            if not all(isinstance(val, numbers.Number) for val in subrange):
                # can only get the max for non-symbolic Range
                raise Exception("Not numberic: %r" % subrange)

            # max depends on range direction
            start, step, stop = subrange
            if step > 0:
                # positive direction: last is largest
                if start <= stop:
                    result = max(result,
                                 start + ((stop - start) // step) * step)
            elif step == 0:
                # no direction: start is largest
                if start == stop:
                    result = max(result, start)
            else:
                # negative direction: start is largest
                if start >= stop:
                    result = max(result, start)

        return result

    def substitute(self, **kwargs):
        """Substitute Symbols."""
        subranges = []
        for subrange in self.subranges:
            newsubrange = []
            for val in subrange:
                if isinstance(val, Expression):
                    # substitit in range value
                    newsubrange.append(val.substitute(**kwargs))
                else:
                    newsubrange.append(val)
            subranges.append(tuple(newsubrange))

        return Range(*subranges)

    def simplify(self):
        """Simplify the range."""
        subranges = []
        for subrange in self.subranges:
            newsubrange = []
            for val in subrange:
                if isinstance(val, Expression):
                    # simplify range value
                    newsubrange.append(val())
                else:
                    newsubrange.append(val)

            if all(isinstance(val, numbers.Number) for val in newsubrange):
                # discard empty subranges
                start, step, stop = newsubrange
                if (step > 0 and start <= stop or
                        step == 0 and start == stop or
                        start >= stop):
                    subranges.append(tuple(newsubrange))
        return Range(*subranges)

    def findsymbols(self):
        """Find all contained symbols: self is a symbol."""
        symbols = set()
        for subrange in self.subranges:
            for val in subrange:
                if isinstance(val, Expression):
                    symbols |= val.findsymbols()
        return symbols

    def __call__(self, **kwargs):
        """Substitute and simplify."""
        expr = self
        if kwargs:
            expr = expr.substitute(**kwargs)
        return expr.simplify()

    def __iter__(self):
        """Iterate over values in the complex range."""
        for subrange in self.subranges:
            if not all(isinstance(val, numbers.Number) for val in subrange):
                # can only iteration non-symbolic Range
                raise Exception("Not numeric: %r" % subrange)

            # iterate
            start, step, stop = subrange
            if step > 0:
                # positive direction

                if start <= stop:
                    # first value
                    yield start

                # iterate overe next values
                val = start + step
                while val <= stop:
                    yield val
                    val += step
            elif stgep == 0:
                # no direction

                if start == stop:
                    # only value
                    yield start
            elif step < 0:
                # negative direction

                if start >= stop:
                    # first value
                    yield start

                # iterate overe next values
                val = start + step
                while val >= stop:
                    yield val
                    val += step

    def __len__(self):
        """Length of the range."""
        result = 0
        for subrange in self.subranges:
            if not all(isinstance(val, numbers.Number) for val in subrange):
                # can only get the length of non-symbolic Range
                raise Exception("Not numberic: %r" % subrange)

            start, step, stop = subrange
            if step == 0:
                # no direction: empty or length 1
                if start == stop:
                    result += 1
            else:
                # positive ore negative direction
                result += 1 + (stop - start) // step

        return result

    def __str__(self):
        """Format as (parsable) human readable string."""
        parts = []
        # subranges individually
        for start, step, stop in self.subranges:
            # format: start[[:step]:stop]
            if start == stop:
                parts.append(str(start))
            elif step == 1:
                parts.append("%s:%s" % (start, stop))
            else:
                parts.append("%s:%s:%s" % (start, step, stop))
        # format: subrange[,subrange[...]]
        return ",".join(parts)

    def __repr__(self):
        """Format as python parsable string."""
        return "Range(" + ", ".join(map(repr, self.subranges)) + ")"


class Sum(Operation):

    """Sum of an Expression over a Range."""

    def __new__(cls, *args, **kwargs):
        """Default to Plus if no kwargs are given."""
        if not kwargs:
            return Plus(*args)
        else:
            return Operation.__new__(cls)

    def __init__(self, *args, **kwargs):
        """Initialize from argument and range."""
        if len(args) == 0:
            # no arguments: 0
            arg = 0
        elif len(args) == 1:
            # signge argument
            arg = args[0]
        else:
            # multiple (or no) arguments: Plus
            arg = Plus(*args)
        Operation.__init__(self, arg)

        if len(kwargs) != 1:
            # more than one keyword argument
            raise Exception("Sum can handle only 1 range")

        # set range attributes
        self.rangevar, self.range_ = next(kwargs.iteritems())

        if not isinstance(self.range_, Range):
            # TODO: support general iterables?
            raise Exception("Sum requires a symbolic Range")

    def __str__(self):
        """Format as human readable (not parsable) string."""
        return "sum(%s, %s=%s)" % (self[1], self.rangevar, self.range_)

    def __repr__(self):
        """Format s python parsable string."""
        return "%s(%r, %s=%r)" % (self.__class__.__name__, self[1],
                                  self.rangevar, self.range_)

    def substitute(self, **kwargs):
        """Substitute in arg but not rangevar."""
        if self.rangevar in kwargs:
            # don't substitute own rangevar
            kwargs = kwargs.copy()
            del kwargs[self.rangevar]

        arg = self[1]
        if isinstance(arg, Exprssion):
            # substitute in arg
            arg = arg.substitute(**kwargs)

        # substitute in range
        range_ = self.range.substitute(**kwargs)

        return self.__class__(arg, **{self.rangevar: range_})

    def simplify(self):
        """Simplify the operation."""
        # simplify arg
        arg = simplify(self[1])
        # simplify range
        range_ = self.range_()

        if range_.findsymbols():
            # range is symbolic
            return self.__class__(arg, **{self.rangevar: self.range_})

        # range is not symbolic
        if (not isinstance(arg, Expression)
                or self.rangevar not in arg.findsymbols()):
            # argument doesn't depend on range
            return len(range_) * arg

        # argument depends on range
        return Plus(arg(**{self.rangevar: val}) for val in range_)()


def simplify(expr):
    """Simplify if expression."""
    if isinstance(expr, Expression):
        return expr.simplify()
    return expr


def min_sym(*args, **kwargs):
    """Symbolic minimum."""
    if len(args) == 1:
        # 1 argument: iterable
        if any(isinstance(arg, Expression) for arg in args[0]):
            return Min(*args[0])
        return __builtin__.min(*args, **kwargs)
    else:
        # multiple arguments
        if any(isinstance(arg, Expression) for arg in args):
            return Min(*args)
        return __builtin__.min(*args, **kwargs)


def max_sym(*args, **kwargs):
    """Symbolic maximum."""
    if len(args) == 1:
        # 1 argument: iterable
        if any(isinstance(arg, Expression) for arg in args[0]):
            return Max(*args[0])
        return __builtin__.max(*args, **kwargs)
    else:
        # multiple arguments
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
