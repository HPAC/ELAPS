"""Simple symbolic expression engine."""

from __future__ import division

import __builtin__
import math
from numbers import Number
from collections import Iterable, defaultdict
from operator import itemgetter
from copy import deepcopy
from inspect import isgenerator


class Expression(tuple):

    """Base class for all expressions."""

    interned = {}

    class __metaclass__(type):
        def __new__(cls, name, bases, clsdict):
            clsdict["__slots__"] = ()
            return type.__new__(cls, name, bases, clsdict)

    def __new__(cls, *args):
        """Implementing interning."""
        if hasattr(cls, "fixedlen") and len(args) != cls.fixedlen:
            raise TypeError("%r takes exactly %s arguments (%s given)" %
                            (cls.__name__, cls.fixedlen, len(args)))
        id_ = (cls,) + args
        if id_ not in cls.interned:
            cls.interned[id_] = super(Expression, cls).__new__(cls, args)
        return cls.interned[id_]

    def __setattr__(self, name, value):
        """Make immutable."""
        if hasattr(self, name):
            raise AttributeError("can't set attribute")
        raise AttributeError("%r object has no attribute %r" %
                             (type(self).__name__, name))

    def __hash__(self):
        """Differentiate between classes."""
        return hash(type(self)) ^ hash(self[:])

    def __eq__(self, other):
        """Check equality by id."""
        return id(self) == id(other)

    def __cmp__(self, other):
        """Compare with other."""
        return cmp(type(self), type(other)) or cmp(self[:], other[:])

    def __repr__(self):
        """Format as python parsable string."""
        return "%s(%s)" % (type(self).__name__, ", ".join(map(repr, self)))

    def __str__(self):
        """Format: cls(args)."""
        return "%s(%s)" % (type(self).__name__, ", ".join(map(str, self)))

    def substitute(self, **kwargs):
        """Variable substitution."""
        return self

    def simplify(self, **kwargs):
        """(Substitute and) simplify the expression."""
        return self.substitute(**kwargs)

    def __call__(self, **kwargs):
        """Substitution and simplification."""
        return simplify(self, **kwargs)

    # math operator overloading:
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
        return Plus(self, -other)

    def __rsub__(self, other):
        """Other - Expression ."""
        return Plus(other, -self)

    def __mul__(self, other):
        """Expression * Other ."""
        return Times(self, other)

    def __rmul__(self, other):
        """Other * Expression ."""
        return Times(other, self)

    def __div__(self, other):
        """Expression / Other ."""
        return Div(self, other)

    def __truediv__(self, other):
        """Expression / Other ."""
        return Div(self, other)

    def __rdiv__(self, other):
        """Other / Expression ."""
        return Div(other, self)

    def __rtruediv__(self, other):
        """Other / Expression ."""
        return Div(other, self)

    def __pow__(self, other):
        """Expression ** Other ."""
        return Power(self, other)


class Symbol(Expression):

    """Symbolic variable.

    tuple layout: (name,)
    """

    fixedlen = 1
    name = property(itemgetter(0))

    def __str__(self):
        """Format: a."""
        return str(self.name)

    def __eq__(self, other):
        """Allow comparison with strings."""
        return self.name == other or Expression.__eq__(self, other)

    def substitute(self, **kwargs):
        """Substitute: return value if matching."""
        return kwargs.get(self.name, self)

    def findsymbols(self):
        """Find all contained symbols: self is a symbol."""
        return set([self])


class Operation(Expression):

    """Base class for symbolic operations."""

    def __new__(cls, *args):
        """If any argument is None, the operation is None."""
        if any(arg is None for arg in args):
            return None
        return super(Operation, cls).__new__(cls, *args)

    def substitute(self, **kwargs):
        """Substitute in all arguments."""
        return type(self)(*substitute(self[:], **kwargs))

    def simplify(self, **kwargs):
        """(Substitute in and) simplify the operation."""
        return type(self)(*simplify(self[:], **kwargs))

    def findsymbols(self):
        """Find all contained symbols."""
        return findsymbols(self[:])


class Minus(Operation):

    """-Expression (unary)."""

    fixedlen = 1
    expr = property(itemgetter(0))

    def __str__(self):
        """Format: -a or -(x)."""
        if isinstance(self.expr, Operation):
            return "-(%s)" % (self.expr,)
        return "-%s" % (self.expr,)

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        arg = simplify(self.expr, **kwargs)

        if isinstance(arg, Minus):
            # double negation
            return arg.expr

        if isinstance(arg, Plus):
            # distribute minus
            return simplify(sum(-x for x in arg))

        return -arg


class Abs(Operation):

    """abs(Expression) (unary)."""

    fixedlen = 1
    expr = property(itemgetter(0))

    def __str__(self):
        """Format: abs(x)."""
        return "abs(%s)" % (self.expr,)

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        arg = simplify(self.expr, **kwargs)

        if isinstance(arg, Minus):
            # redundant -
            return simplify(abs(arg.expr))

        if isinstance(arg, Abs):
            # redundant recursive abs
            return arg

        return abs(arg)


class Plus(Operation):

    """Sum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format a + b - c + (x) + ...."""
        if not self:
            return ""
        result = str(self[0])
        for arg in self[1:]:
            if isinstance(arg, Minus):
                if isinstance(arg.expr, Plus):
                    result += " - (%s)" % (arg.expr,)
                else:
                    result += " - %s" % (arg.expr,)
            elif isinstance(arg, Number) and arg < 0:
                result += " - %s" % -arg
            else:
                result += " + %s" % (arg,)
        return result

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        args = simplify(self[:], **kwargs)

        num = 0
        newargs = []
        for arg in args:
            if isinstance(arg, Plus):
                # flatten recursive Plus
                if isinstance(arg[0], Number):
                    num += arg[0]
                    arg = arg[1:]
                newargs += arg[:]
            elif isinstance(arg, Number):
                # sum numbers
                num += arg
            else:
                newargs.append(arg)

        # combine terms
        collected = defaultdict(int)
        for arg in newargs:
            if isinstance(arg, Times) and isinstance(arg[0], Number):
                collected[Times(*arg[1:])()] += arg[1]
            else:
                collected[arg] += 1
        newargs = [arg if c == 1 else simplify(c * arg)
                   for arg, c in collected.iteritems()]

        # sort
        newargs.sort()

        if num != 0:
            # numeric part present
            newargs.insert(0, num)

        if len(newargs) == 0:
            # empty Plus = 0
            return 0

        if len(newargs) == 1:
            # single argument
            return newargs[0]

        return Plus(*newargs)


class Times(Operation):

    """Product of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format: a * (b + c) * ...."""
        if self[0] == -1:
            return str(Times(-self[0], *self[1:]))
        return " * ".join("(%s)" % (arg,) if isinstance(arg, Plus)
                          else str(arg) for arg in self)

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        args = simplify(self[:], **kwargs)

        num = 1
        newargs = []
        for arg in args:
            if isinstance(arg, Minus):
                # pull out -1
                num *= -1
                arg = arg.expr
            if isinstance(arg, Times):
                # flatten recursive Times
                if isinstance(arg[0], Number):
                    num *= arg[0]
                    arg = arg[1:]
                newargs += arg[:]
            elif isinstance(arg, Number):
                # multiply numbers
                num *= arg
            else:
                newargs.append(arg)

        # sort
        newargs.sort()

        if num == -1 and len(newargs) == 1:
            return simplify(-newargs[0])

        if num != 1:
            # numeric part present
            newargs.insert(0, num)

        # multiply out a (b + c) d
        if any(isinstance(arg, Plus) for arg in args):
            idx = min(i for i, arg in enumerate(args) if isinstance(arg, Plus))
            return simplify(sum(Times(*(args[:idx] + (arg,) + args[idx+1:]))
                                for arg in args[idx]))

        if len(newargs) == 0:
            # empty Times = 1
            return 1

        if len(newargs) == 1:
            # single argument
            return newargs[0]

        return Times(*newargs)


class Div(Operation):

    """Division with at least one of nom, denom an Expression.

    tuple layout: (nominator, denominator)
    """

    fixedlen = 2
    nominator = property(itemgetter(0))
    denominator = property(itemgetter(1))

    def __str__(self):
        """Format: a / b or (x) / (y)."""
        return " / ".join("(%s)" % (arg,) if isinstance(arg, Operation)
                          else str(arg) for arg in self)

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        nominator, denominator = simplify(self[:], **kwargs)

        if isinstance(nominator, Div):
            # top is a fraction
            return simplify(nominator.nominator /
                            (nominator.denominator * denominator))

        if isinstance(denominator, Div):
            # bottom is a fraction
            return simplify(nominator * denominator.denominator /
                            denominator.nominator)

        if isinstance(denominator, Number):
            # bottom is a number
            return 1 / denominator * nominator

        return nominator / denominator


class Power(Operation):

    """Power with an Expression as the base.

    tuple layout: (base, exponent)
    """

    fixedlen = 2
    base = property(itemgetter(0))
    exponent = property(itemgetter(1))

    def __str__(self):
        """Format: a ^ b or (x) ^ (y)."""
        return " ^ ".join("(%s)" % (arg,) if isinstance(arg, Operation)
                          else str(arg) for arg in self)

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        base, exponent = simplify(self[:], **kwargs)

        if isinstance(base, Power):
            # base is a power
            return simplify(base.base ** (base.exponent * exponent))

        if isinstance(exponent, Div) and isinstance(Div.nominator, Number):
            # exponent is int / expr
            return -(base ** (1 / exponent))

        if isinstance(exponent, Log):
            # exponent is log
            if base == exponent.base:
                return exponent.expr
            if isinstance(base, Number) and isinstance(exponent.base, Number):
                return simplify(exponent.expr ** log(base, exponent.base))

        if isinstance(exponent, int):
            # expand for integer exponent
            if exponent > 0:
                return simplify(Times(*(exponent * [base])))
            return simplify(1 / Times(*(-exponent * [base])))

        return Power(base, exponent)


class Log(Operation):

    """Logarithm in any base (default: e).

    tuple layout: (expr, base)
    """

    expr = property(itemgetter(0))
    base = property(itemgetter(1))

    def __new__(cls, expr, base=math.e):
        """2nd argument default: math.e."""
        return super(Log, cls).__new__(cls, expr, base)

    def __str__(self):
        """Format: log(x) or log_a(x)."""
        if self.base == math.e:
            return "log(%s)" % (self.expr,)
        return "log_%s(%s)" % (self.base, self.expr)

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        arg, base = simplify(self[:], **kwargs)

        if arg == base:
            return 1

        if isinstance(arg, Power):
            # argument is a power
            return simplify(arg.exponent * log(arg.base, base))

        return log(arg, base)


class Floor(Operation):

    """Floor function: round(x-.5)."""

    fixedlen = 1
    expr = property(itemgetter(0))

    def __str__(self):
        """Format: floor(x)."""
        return "floor(%s)" % (self.expr,)

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        arg = simplify(self.expr, **kwargs)

        if isinstance(arg, Floor):
            # redundant recursive floor
            return arg

        if isinstance(arg, Number):
            return int(math.floor(arg))

        return floor(arg)


class Ceil(Operation):

    """Ceiling function: round(x+.5)."""

    fixedlen = 1
    expr = property(itemgetter(0))

    def __str__(self):
        """Format: ceil(x)."""
        return "ceil(%s)" % (self.expr,)

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        arg = simplify(self.expr, **kwargs)

        if isinstance(arg, Ceil):
            # redundant recursive floor
            return arg

        if isinstance(arg, Number):
            return int(math.ceil(arg))

        return ceil(arg)


class Min(Operation):

    """Minimum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format: min(x, x, ...)."""
        return "min(%s)" % ", ".join(map(str, self))

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        args = simplify(self[:], **kwargs)

        num = float("inf")
        newargs = []
        for arg in args:
            if isinstance(arg, Min):
                # flatten recursive Min
                if isinstance(arg[0], Number):
                    num = min(num, arg[0])
                    arg = arg[1:]
                newargs += arg[:]
            elif isinstance(arg, Number):
                # minimum of numbers
                num = min(num, arg)
            else:
                newargs.append(arg)

        if num != float("inf"):
            # numeric part present
            newargs.insert(0, num)

        if len(newargs) == 0:
            # empty Min == None
            return None

        if len(newargs) == 1:
            # single argument
            return newargs[0]

        return min(newargs)


class Max(Operation):

    """Maximum of multiple operands (at least 1 Expression)."""

    def __str__(self):
        """Format: max(x, x, ...)."""
        return "max(%s)" % ", ".join(map(str, self))

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify arguments
        args = simplify(self[:], **kwargs)

        num = float("-inf")
        newargs = []
        for arg in args:
            if isinstance(arg, Max):
                # flatten recursive Max
                if isinstance(arg[0], Number):
                    num = max(num, arg[0])
                    arg = arg[1:]
                newargs += arg[:]
            elif isinstance(arg, Number):
                # maximum of numbers
                num = max(num, arg)
            else:
                newargs.append(arg)

        if num != float("-inf"):
            # numeric part present
            newargs.insert(0, num)

        if len(newargs) == 0:
            # empty Max = None
            return None

        if len(newargs) == 1:
            # single argument
            return newargs[0]

        return max(newargs)


class Sum(Operation):

    """Sum of an Expression over a Range.

    tuple layout: (expr, rangevar, range_)
    """

    expr = property(itemgetter(0))
    rangevar = property(itemgetter(1))
    range_ = property(itemgetter(2))

    def __new__(cls, *args, **kwargs):
        """Create a new Sum or Plus."""
        if len(kwargs) == 0:
            # no range: plus
            return Plus(*args)
        if len(kwargs) > 1:
            # more than one range: nesting
            kwargs = sorted(kwargs.items())
            return Sum(Sum(*args, **dict(kwargs[0])), **dict(kwargs[1:]))
        if len(args) == 0:
            # no arguments: 0
            arg = 0
        elif len(args) == 1:
            # single argument
            arg = args[0]
        else:
            # multiple arguments: Plus
            arg = Plus(*args)
        # retrieve and check range
        rangevar, range_ = next(kwargs.iteritems())
        if not isinstance(range_, Iterable):
            # range must be iterable
            raise TypeError("range must support iteration")
        if isinstance(range_, list):
            # make range immutable
            range_ = tuple(range_)
        return super(Sum, cls).__new__(cls, arg, rangevar, range_)

    def __str__(self):
        """Format: sum(x, a=y)."""
        return "sum(%s, %s=%s)" % self

    def __repr__(self):
        """Format as python parsable string."""
        return "%s(%r, %s=%r)" % ((type(self).__name__,) + self[:])

    def substitute(self, **kwargs):
        """Substitute in arg but not rangevar."""
        # substitute in range
        newrange = substitute(self.range_, **kwargs)

        # don't substitute own rangevar in arg
        if self.rangevar in kwargs:
            del kwargs[self.rangevar]

        # substitute in arg
        newarg = substitute(self.expr, **kwargs)

        return Sum(newarg, **{self.rangevar: newrange})

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify range
        range_ = simplify(self.range_, **kwargs)

        # don't substitute own rangevar in arg
        if self.rangevar in kwargs:
            del kwargs[self.rangevar]

        # simplify argument
        arg = simplify(self.expr, **kwargs)

        if isinstance(range_, Range) and findsymbols(range_):
            # range is symbolic
            return Sum(arg, **{self.rangevar: range_})

        # range is not symbolic
        if isinstance(arg, Expression):
            return simplify(Plus(*(arg(**{self.rangevar: val})
                                   for val in range_)))

        return len(range_) * arg


class Prod(Operation):

    """Product of an Expression over a Range.

    tuple layout: (expr, rangevar, range_)
    """

    expr = property(itemgetter(0))
    rangevar = property(itemgetter(1))
    range_ = property(itemgetter(2))

    def __new__(cls, *args, **kwargs):
        """Create a new Prod or Times."""
        if len(kwargs) == 0:
            # no range: Times
            return Times(*args)
        if len(kwargs) > 1:
            # more than one range: nesting
            kwargs = sorted(kwargs.items())
            return Prod(Prod(*args, **dict(kwargs[0])), **dict(kwargs[1:]))
        if len(args) == 0:
            # no arguments: 1
            arg = 1
        elif len(args) == 1:
            # single argument
            arg = args[0]
        else:
            # multiple arguments: Plus
            arg = Times(*args)
        rangevar, range_ = next(kwargs.iteritems())
        if not isinstance(range_, Iterable):
            # range must be iterable
            raise TypeError("range must support iteration")
        if isinstance(range_, list):
            # make range immutable
            range_ = tuple(range_)
        return super(Prod, cls).__new__(cls, arg, rangevar, range_)

    def __str__(self):
        """Format: prod(x, a=y)."""
        return "prod(%s, %s=%s)" % self

    def __repr__(self):
        """Format as python parsable string."""
        return "%s(%r, %s=%r)" % ((type(self).__name__,) + self[:])

    def substitute(self, **kwargs):
        """Substitute in arg but not rangevar."""
        # substitute in range
        newrange = substitute(self.range_, **kwargs)

        # don't substitute own rangevar in arg
        if self.rangevar in kwargs:
            del kwargs[self.rangevar]

        # substitute in arg
        newarg = substitute(self.expr, **kwargs)

        return Prod(newarg, **{self.rangevar: newrange})

    def simplify(self, **kwargs):
        """(Substitute in and) Simplify the operation."""
        # simplify range
        range_ = simplify(self.range_, **kwargs)

        # don't substitute own rangevar in arg
        if self.rangevar in kwargs:
            del kwargs[self.rangevar]

        # simplify argument
        arg = simplify(self.expr, **kwargs)

        if isinstance(range_, Range) and range_.findsymbols():
            # range is symbolic
            return Prod(arg, **{self.rangevar: range_})

        # range is not symbolic
        return simplify(Times(*(arg(**{self.rangevar: val})
                                for val in range_)))


class Range(tuple):

    """Complex range object (possibly containing Expressions).

    tuple layout: (subranges,)
    """

    subranges = property(itemgetter(0))

    def __new__(cls, *args, **kwargs):
        """Instantiate from tuples or string."""
        if len(args) == 1 and isinstance(args[0], str):
            # initialize from string

            # for each subrange
            rangeparts = args[0].split(",")

            args = []
            for rangepart in rangeparts:
                # format: min[[:step]:max]
                parts = rangepart.strip().split(":")
                parts = [eval(part, {}, kwargs) for part in parts if part]
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

        subranges = []
        for arg in args:
            # check form of subrange
            if not isinstance(arg, tuple) or len(arg) != 3:
                raise Exception("Invalid subrange: %r" % (arg,))
            # check contents of subrange
            for val in arg:
                if not isinstance(val, (Number, Expression)):
                    raise TypeError("Invalid value in range:%r" % (arg,))
            subranges.append(arg)
        return super(Range, cls).__new__(cls, (tuple(subranges),))

    def __setattr__(self, name, value):
        """Make immutable."""
        if hasattr(self, name):
            raise AtributeError("can't set attribute")
        else:
            raise AttributeError("%r object has no attribute %r" %
                                 (type(self).__name__, name))

    def __deepcopy__(self, memo):
        """Range is immutable."""
        return self

    def __copy__(self, memo):
        """Range is immutable."""
        return self

    def substitute(self, **kwargs):
        """Substitute Symbols."""
        return Range(*(tuple(substitute(val, **kwargs) for val in subrange)
                       for subrange in self.subranges
                       ))

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
        return Range(*newsubranges)

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

                # iterate over next values
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

                # iterate over next values
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
        # empty range: None
        if not self.subranges:
            return None
        # initial minimum: inf
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
        # empty range: None
        if not self.subranges:
            return None
        # initial minimum: -inf
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
        """Format: a:b:,x:y:z,...."""
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


def substitute(expr, **kwargs):
    """Substitute if Expression."""
    if isinstance(expr, (Expression, Range)):
        return expr.substitute(**kwargs)
    if isinstance(expr, (list, tuple)):
        return type(expr)(substitute(e, **kwargs) for e in expr)
    return kwargs.get(expr, expr)


def simplify(expr, **kwargs):
    """(Substitute and) simplify if Expression."""
    if isinstance(expr, (Expression, Range)):
        return expr.simplify(**kwargs)
    if isinstance(expr, (list, tuple)):
        return type(expr)(simplify(e, **kwargs) for e in expr)
    return expr


def findsymbols(expr):
    """find symbols if Expression."""
    if isinstance(expr, (Expression, Range)):
        return expr.findsymbols()
    if isinstance(expr, (list, tuple)):
        return set().union(*map(findsymbols, expr))
    return set()


# math overloads

def min(*args, **kwargs):
    """Symbolic minimum."""
    if len(args) > 1 or isinstance(args[0], Expression):
        return min(args, **kwargs)
    # 1 argument: iterable
    if isinstance(args[0], Range):
        return args[0].min()
    if isgenerator(args[0]):
        # don't process generators
        return __builtin__.min(*args, **kwargs)
    if any(isinstance(arg, Expression) for arg in args[0]):
        return Min(*args[0])
    return __builtin__.min(*args, **kwargs)


def max(*args, **kwargs):
    """Symbolic maximum."""
    if len(args) > 1 or isinstance(args[0], Expression):
        return max(args, **kwargs)
    # 1 argument: iterable
    if isinstance(args[0], Range):
        return args[0].max()
    if isgenerator(args[0]):
        # don't process geneartors
        return __builtin__.max(*args, **kwargs)
    if any(isinstance(arg, Expression) for arg in args[0]):
        return Max(*args[0])
    return __builtin__.max(*args, **kwargs)


def log(*args):
    """Symbolic logarithm."""
    if any(isinstance(arg, Expression) for arg in args):
        return Log(*args)
    if args[0] == 0:
        # return none instead of throwing an error
        return None
    return math.log(*args)


def floor(arg):
    """Symbolic floor."""
    if isinstance(arg, Expression):
        return Floor(arg)
    return int(math.ceil(arg))


def ceil(arg):
    """Symbolic ceiling."""
    if isinstance(arg, Expression):
        return Ceil(arg)
    return int(math.ceil(arg))
