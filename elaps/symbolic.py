#!/usr/bin/env python
"""Simple symbolic expression engine."""
from __future__ import division, print_function

from numbers import Number
from collections import Iterable
import __builtin__
from copy import deepcopy


class Expression(object):

    """Base class for all expressions."""

    def __neg__(self):
        """-Expression ."""
        return Minus(self)

    def __abs__(self):
        """abs(Expression) ."""
        return Abs(self)

    def __add__(self, other):
        """Expression + Other ."""
        return Plus(self, other)

    def __radd__(self, other):
        """Other + Expression ."""
        return Plus(other, self)

    def __sub__(self, other):
        """Expression - Other ."""
        return Plus(self, -(other))

    def __rsub__(self, other):
        """Other - Expression ."""
        return Plus(other, -(self))

    def __mul__(self, other):
        """Expression * Other ."""
        return Prod(self, other)

    def __rmul__(self, other):
        """Other * Expression ."""
        return Prod(other, self)

    def __truediv__(self, other):
        """Expression / Other ."""
        return Div(self, other)

    def __rtruediv__(self, other):
        """Other / Expression ."""
        return Div(other, self)

    def __pow__(self, other):
        """Expression ** Other ."""
        return Power(self, other)

    def subistitute(self, **kwargs):
        """Variable substitution."""
        return self

    def simplify(self, **kwargs):
        """(Substitute and) simplify the expression."""
        return self.substitute(**kwargs)

    def __call__(self, **kwargs):
        """Substitution and simplification."""
        return self.simplify(**kwargs)


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
        return "%s(%r)" % (type(self).__name__, self.name)

    def __eq__(self, other):
        """Compare for equality."""
        if isinstance(other, Symbol):
            return self.name == other.name
        return self.name == other

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

    def __new__(cls, *args, **kwargs):
        """If any argument is None, the operation is None."""
        if any(arg is None for arg in args):
            return None
        else:
            return list.__new__(cls)

    def __init__(self, *args):
        """Initialize as a list with the operation as first element."""
        list.__init__(self, (type(self),) + args)

    def __repr__(self):
        """Python parsable representation."""
        return "%s(%s)" % (type(self).__name__, ", ".join(map(repr, self[1:])))

    def __hash__(self):
        """Hash the expression."""
        return hash(tuple(map(hash, self)))

    def __eq__(self, other):
        """Compare Operation."""
        return type(self) == type(other) and list.__eq__(self, other)

    def substitute(self, **kwargs):
        """Substitute in all arguments."""
        newargs = []
        for arg in self[1:]:
            if arg in kwargs:
                # argument found
                newargs.append(kwargs[arg.name])
            else:
                newargs.append(substitute(arg, **kwargs))
        return type(self)(*newargs)

    def simplify(self, **kwargs):
        """(Substitute in and) simplify the operation."""
        return type(self)(*(simplify(arg, **kwargs) for arg in self[1:]))

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

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        arg = Operation.simplify(self, **kwargs)[1]

        if isinstance(arg, Minus):
            # double negation
            return arg[1]

        return -arg


class Abs(Operation):

    """abs(Expression) (unary)."""

    def __init__(self, expression):
        """Initialize: Only one argument."""
        Operation.__init__(self, expression)

    def __str__(self):
        """Format as human readable."""
        return "abs(" + str(self[1]) + ")"

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        arg = Operation.simplify(self, **kwargs)[1]

        if isinstance(arg, Minus):
            # redundand -
            return simplify(abs(arg[1]))

        if isinstance(arg, Abs):
            # redundand recursive abs
            return arg[1]

        return abs(arg)


class Plus(Operation):

    """Sum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format as human readable."""
        return " + ".join(map(str, self[1:]))

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        args = Operation.simplify(self, **kwargs)[1:]

        num = 0
        newargs = []
        for arg in args:
            if isinstance(arg, Plus):
                # flatten recursive Plus
                otherargs = arg[1:]
                if isinstance(otherargs[0], Number):
                    num += otherargs[0]
                    otherargs = otherargs[1:]
                newargs += otherargs
            elif isinstance(arg, Number):
                # sum numbers
                num += arg
            else:
                newargs.append(arg)

        if num != 0:
            # numeric part present
            newargs.insert(0, num)

        # Note: sum() would start with 0

        if len(newargs) == 0:
            # empty Plus = 0
            return 0

        if len(newargs) == 1:
            # single argument
            return newargs[0]

        return type(self)(*newargs)


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

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        args = Operation.simplify(self, **kwargs)[1:]

        num = 1
        newargs = []
        for arg in args:
            if isinstance(arg, Prod):
                # flatten recursive Prod
                otherargs = arg[1:]
                if isinstance(otherargs[0], Number):
                    num *= otherargs[0]
                    otherargs = otherargs[1:]
                newargs += otherargs
            elif isinstance(arg, Number):
                # multiply numbers
                num *= arg
            else:
                newargs.append(arg)

        if num != 1:
            # numeric part present
            newargs.insert(0, num)

        if len(newargs) == 0:
            # empty Prod = 1
            return 1

        if len(newargs) == 1:
            # single argument
            return newargs[0]

        return type(self)(*newargs)


class Div(Operation):

    """Division with at least one of nom, denom an Expression."""

    def __init__(self, nominator, denominator):
        """Init: exactly two arguments."""
        Operation.__init__(self, nominator, denominator)

    def __str__(self):
        """Format as human readable."""
        strs = map(str, self[1:])
        for i, arg in enumerate(self[1:]):
            if isinstance(arg, Operation):
                # paranteses around any Operation
                strs[i] = "(" + strs[i] + ")"
        return strs[0] + " / " + strs[1]

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        nominator, denominator = Operation.simplify(self, **kwargs)[1:]

        if isinstance(nominator, Div):
            # top is a fraction
            return simplify(nominator[1] / (nominator[2] * denominator))

        if isinstance(denominator, Div):
            # bottom is a fraction
            return simplify(nominator * denominator[2] / denominator[1])

        if isinstance(denominator, Number):
            # bottom is a number
            return 1 / denominator * nominator

        return nominator / denominator


class Power(Operation):

    """Power with an experssion as the base."""

    def __init__(self, base, exponent):
        """Init: exactly two arguments."""
        Operation.__init__(self, base, exponent)

    def __str__(self):
        """Format as human readable."""
        strs = map(str, self[1:])
        for i, arg in enumerate(self[1:]):
            if isinstance(arg, Operation):
                # paranteses around any Operation
                strs[i] = "(" + strs[i] + ")"
        return strs[0] + " ^ " + strs[1]

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        base, exponent = Operation.simplify(self, **kwargs)[1:]

        if isinstance(base, Power):
            # base is a power
            return simplify(base[1] ** (base[2] * exponent))

        if isinstance(exponent, int):
            # expand for integer exponent
            return Prod(*(exponent * [base]))()

        return base ** exponent


class Min(Operation):

    """Minimum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format as human readable."""
        return "min(" + ", ".join(map(str, self[1:])) + ")"

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        args = Operation.simplify(self, **kwargs)[1:]

        num = float("inf")
        newargs = []
        for arg in args:
            if isinstance(arg, Min):
                # flatten recursive Min
                otherargs = arg[1:]
                if isinstance(otherargs[0], Number):
                    num = min(num, otherargs[0])
                    otherargs = otherargs[1:]
                newargs += otherargs
            elif isinstance(arg, Number):
                # minimum of numbers
                num = min(num, arg)
            else:
                newargs.append(arg)

        if num != float("inf"):
            # numeric part present
            newargs.insert(0, num)

        if len(newargs) == 0:
            # empty Min == -inf
            return float("-inf")

        if len(newargs) == 1:
            # single argument
            return newargs[0]

        return type(self)(*newargs)


class Max(Operation):

    """Maximum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format as human readable."""
        return "max(" + ", ".join(map(str, self[1:])) + ")"

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        args = Operation.simplify(self, **kwargs)[1:]

        num = float("-inf")
        newargs = []
        for arg in args:
            if isinstance(arg, Max):
                # flatten recursive Max
                otherargs = arg[1:]
                if isinstance(otherargs[0], Number):
                    num = max(num, otherargs[0])
                    otherargs = otherargs[1:]
                newargs += otherargs
            elif isinstance(arg, Number):
                # maximum of numbers
                num = max(num, arg)
            else:
                newargs.append(arg)

        if num != float("-inf"):
            # numeric part present
            newargs.insert(0, num)

        if len(newargs) == 0:
            # empty Max = inf
            return float("inf")

        if len(newargs) == 1:
            # single argument
            return newargs[0]

        return type(self)(*newargs)


class Range(object):

    """Complex range object (possibly containing Expressions)."""

    def __init__(self, *args, **kwargs):
        """Initialize from tuples or string."""
        if len(args) == 1 and isinstance(args[0], str):
            # initialize from string

            # for each subrange
            rangeparts = args[0].split(",")

            args = []
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
                else:
                    subrange = tuple(parts)
                args.append(subrange)
        elif len(args) == 1 and isinstance(args[0], Range):
            # initialize from other range
            args = deepcopy(args[0].subranges)

        self.subranges = []
        for arg in args:
            # check form of subrange
            if not isinstance(arg, tuple) or len(arg) != 3:
                raise Exception("Invalid subrange: %r" % (arg,))
            # check contents of subrange
            for val in arg:
                if not isinstance(val, (Number, Expression)):
                    raise TypeError("Invalid value in range:%r" % (arg,))
            self.subranges.append(arg)

    def substitute(self, **kwargs):
        """Substitute Symbols."""
        return type(self)(*[
            tuple(substitute(val, **kwargs) for val in subrange)
            for subrange in self.subranges
        ])

    def simplify(self, **kwargs):
        """Simplify the range."""
        subranges = self.substitute(**kwargs).subranges

        newsubranges = []
        for subrange in subranges:
            newsubrange = tuple(map(simplify, subrange))

            if any(not isinstance(val, Number) for val in newsubrange):
                newsubranges.append(newsubrange)
                continue

            # discard empty subranges
            start, step, stop = newsubrange
            if (step > 0 and start <= stop or
                    step == 0 and start == stop or
                    step < 0 and start >= stop):
                newsubranges.append(newsubrange)
        return type(self)(*newsubranges)

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
        return self.simplify(**kwargs)

    def __iter__(self):
        """Iterate over values in the complex range."""
        if self.findsymbols():
            raise TypeError("Not numeric: %s" % self)
        for subrange in self.subranges:
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
            elif step == 0:
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
        if self.findsymbols():
            raise TypeError("Not numeric: %s" % self)
        for subrange in self.subranges:
            start, step, stop = subrange
            if step == 0:
                # no direction: empty or length 1
                if start == stop:
                    result += 1
            else:
                # positive ore negative direction
                subrange_len = 1 + (stop - start) // step
                if subrange_len > 0:
                    result += 1 + (stop - start) // step

        return result

    def min(self):
        """compute the minimum."""
        if self.findsymbols():
            raise TypeError("Not numeric: %s" % self)
        # default minimum: inf
        result = float("inf")
        # consider all subranges
        for subrange in self.subranges:
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
        if self.findsymbols():
            raise TypeError("Not numeric: %s" % self)
        # default maximum: -inf
        result = -float("inf")
        # consider all subranges
        for subrange in self.subranges:
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

    def __eq__(self, other):
        """Compare with other Range."""
        return (type(self) == type(other) and
                self.subranges == other.subranges)

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
        return "%s(%s)" % (type(self).__name__,
                           ", ".join(map(repr, self.subranges)))


class Sum(Operation):

    """Sum of an Expression over a Range."""

    def __init__(self, *args, **kwargs):
        """Initialize from argument and range."""
        if len(args) == 0:
            # no arguments: 0
            arg = 0
        elif len(args) == 1:
            # single argument
            arg = args[0]
        else:
            # multiple arguments: Plus
            arg = Plus(*args)
        Operation.__init__(self, arg)

        if len(kwargs) != 1:
            # more than one keyword argument
            raise TypeError("Need exactly one range.")

        # set range attributes
        self.rangevar, self.range_ = next(kwargs.iteritems())

        if not isinstance(self.range_, Iterable):
            # range must be iterable
            raise TypeError("range must support iteration")

    def __str__(self):
        """Format as human readable (not parsable) string."""
        return "sum(%s, %s=%s)" % (self[1], self.rangevar, self.range_)

    def __repr__(self):
        """Format s python parsable string."""
        return "%s(%r, %s=%r)" % (type(self).__name__, self[1],
                                  self.rangevar, self.range_)

    def __eq__(self, other):
        """Compare range too."""
        return Operation.__eq__(self, other) and self.range_ == other.range_

    def substitute(self, **kwargs):
        """Substitute in arg but not rangevar."""
        # substitute in range
        newrange = substitute(self.range_, **kwargs)

        # don't substitute own rangevar in arg
        if self.rangevar in kwargs:
            del kwargs[self.rangevar]

        # substitute in arg
        newarg = substitute(self[1], **kwargs)

        return type(self)(newarg, **{self.rangevar: newrange})

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify argument
        arg = simplify(self[1], **kwargs)

        # simplify range
        range_ = simplify(self.range_)

        if isinstance(range_, Range) and range_.findsymbols():
            # range is symbolic
            return type(self)(arg, **{self.rangevar: range_})

        # range is not symbolic
        if (not isinstance(arg, Expression)
                or self.rangevar not in arg.findsymbols()):
            # argument doesn't depend on range
            return len(range_) * arg

        # Note: sum() would start with 0

        # argument depends on range
        return Plus(*(arg(**{self.rangevar: val}) for val in range_))()


def substitute(expr, **kwargs):
    """Substitute if Expression."""
    if isinstance(expr, (Expression, Range)):
        return expr.substitute(**kwargs)
    return expr


def simplify(expr, **kwargs):
    """(Substitute and) simplify if Expression."""
    if isinstance(expr, (Expression, Range)):
        return expr.simplify(**kwargs)
    return expr


def findsymbols(expr):
    """find symbols if Expression."""
    if isinstance(expr, (Expression, Range)):
        return expr.findsymbols()
    if isinstance(expr, (list, tuple)):
        return set().union(*map(findsymbols, expr))
    return set()


def min(*args, **kwargs):
    """Symbolic minimum."""
    if len(args) > 1:
        return min(args)
    # 1 argument: iterable
    if isinstance(args[0], Range):
        return args[0].min()
    if any(isinstance(arg, Expression) for arg in args[0]):
        return Min(*args[0])
    return __builtin__.min(*args, **kwargs)


def max(*args, **kwargs):
    """Symbolic maximum."""
    if len(args) > 1:
        return max(args)
    if isinstance(args[0], Range):
        return args[0].max()
    if any(isinstance(arg, Expression) for arg in args[0]):
        return Max(*args[0])
    return __builtin__.max(*args, **kwargs)
