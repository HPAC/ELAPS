#!/usr/bin/env python
"""Python representations of kernel signatures."""
from __future__ import division, print_function

import numbers
import symbolic


named_attributes = ("lower", "upper", "symm", "herm", "spd", "hpd", "work")

datatype_prefixes = {
    "i": "integer",
    "s": "single precision",
    "d": "double precision",
    "c": "single precision complex",
    "z": "double precision complex"
}


class Signature(list):

    """Representation of a kernel signature."""

    def __init__(self, *args, **kwargs):
        """Initialize from file ore arguments."""
        list.__init__(self, args)
        self.flopsstr = None
        self.flops = None

        if not isinstance(self[0], Name):
            self[0] = Name(self[0])

        # infer and compile flops, min, max, attr
        self.init_lambdas(kwargs)

        # lookup for fast argument selection
        self.argtypelookup = {}

    def init_lambdas(self, kwargs):
        """Initialize lambda expressions."""
        lambdaargs = ", ".join(arg.name for arg in self)
        if "complexity" in kwargs and "flops" not in kwargs:
            # legacy support
            kwargs["flops"] = kwargs["complexity"]
        if "flops" in kwargs:
            self.flopsstr = kwargs["flops"]
            self.flops = eval("lambda %s: %s" % (lambdaargs, kwargs["flops"]),
                              symbolic.__dict__)
        for arg in self:
            arg.min = None
            arg.max = None
            if isinstance(arg, ArgWithMin) and arg.minstr:
                arg.min = eval("lambda %s: %s" % (lambdaargs, arg.minstr),
                               symbolic.__dict__)
            if isinstance(arg, ArgWithMin) and arg.maxstr:
                arg.max = eval("lambda %s: %s" % (lambdaargs, arg.maxstr),
                               symbolic.__dict__)
            arg.properties = lambda *args: ()
            if arg.propertiesstr:
                lambdarhs = arg.propertiesstr
                for attrname in named_attributes:
                    lambdarhs = lambdarhs.replace(attrname, repr(attrname))
                arg.properties = eval("lambda %s: filter(None, (%s,))" %
                                      (lambdaargs, lambdarhs),
                                      symbolic.__dict__)

        self.check_lambdas()

    def check_lambdas(self):
        """Check lambdas for unknown arguments."""
        args = range(len(self))
        if self.flops:
            try:
                self.flops(*args)
            except NameError as e:
                raise NameError("Unknown argument %r used in flops" %
                                str(e).split("'")[1])
        for arg in self:
            if arg.min:
                try:
                    arg.min(*args)
                except NameError as e:
                    raise NameError("Unknown argument %r used in min for %s" %
                                    (str(e).split("'")[1], arg))
            if arg.max:
                try:
                    arg.max(*args)
                except NameError as e:
                    raise NameError("Unknown argument %r used in max for %s" %
                                    (str(e).split("'")[1], arg))
            if arg.properties:
                try:
                    arg.properties(*args)
                except NameError as e:
                    raise NameError("Unknown argument or property %r "
                                    "used in properties for %s" %
                                    (str(e).split("'")[1], arg))

    def __str__(self):
        """Format as human readable."""
        return (self[0].name + "(" +
                ", ".join(arg.name for arg in self[1:]) + ")")

    def __repr__(self):
        """Format as python parsable string."""
        args = map(repr, [self[0].name] + self[1:])
        if self.flops:
            args.append("flops=%r" % self.flopsstr)
        return "%s(%s)" % (type(self).__name__, ", ".join(args))

    def __call__(self, *args):
        """Create a call from the signature with given arguments."""
        if len(args) == 0:
            args = tuple(arg.default() for arg in self[1:])
        return Call(self, *args)

    def __getattr__(self, name):
        """Variable names as attributes."""
        try:
            return self[self.argpos(name)]
        except:
            raise AttributeError("%r object has no attribute %r" %
                                 (type(self).__name__, name))

    def argpos(self, name):
        """Search for an argument id by name."""
        for argid, arg in enumerate(self):
            if arg.name == name:
                return argid
        raise IndexError("Unknown argument: %s" % name)

    def argsbytype(self, type_, *types):
        """Return a list of argument posisions."""
        if types:
            return sorted(set(self.argsbytype(type_) +
                              self.argsbytype(*types)))
        if type_ not in self.argtypelookup:
            self.argtypelookup[type_] = [i for i, arg in enumerate(self)
                                         if isinstance(arg, type_)]
        return self.argtypelookup[type_]

    def dataargs(self):
        """Return a list of data argument positions."""
        return self.argsbytype(Data)

    def datatype(self):
        """Deduce type of operands (single, double, complex, ...)."""
        # datatype is type of first dataarg
        return self[self.dataargs()[0]].typename


class BasicCall(list):

    """Base class for Calls with and without a Signature."""

    def __init__(self, sig, *args):
        """Initialize from arguments."""
        if not args:
            args = tuple("" if arg == "char*" else 0 for arg in sig[1:])
        if len(sig) != 1 + len(args):
            raise TypeError("%s takes %d arguments (%d given)" %
                            (sig[0], len(sig) - 1, len(args)))
        list.__init__(self, (str(sig[0]),) + args)
        self.__dict__["sig"] = sig

    def __str__(self):
        """Format as human readable."""
        args = []
        for arg in self[1:]:
            if type(arg) is list:
                args.append("[%s]" % arg[0])
            else:
                args.append(str(arg))
        return str(self[0]) + "(" + ", ".join(args) + ")"

    def __repr__(self):
        """Format as python parsable string."""
        args = map(repr, [self.sig] + self[1:])
        return "%s(%s)" % (type(self).__name__, ", ".join(args))

    def __copy__(self):
        """Create a deep copy."""
        return type(self)(self.sig, *self[1:])

    def copy(self):
        """Create a copy."""
        return self.__copy__()


class Call(BasicCall):

    """A call to a signature."""

    def __init__(self, sig, *args):
        """Initialize from signature and arguments."""
        if not isinstance(sig, Signature):
            raise TypeError("a Signature is required as first argument")
        BasicCall.__init__(self, sig, *args)

    def __getattr__(self, name):
        """Variable names as attributes."""
        try:
            return self[self.sig.argpos(name)]
        except:
            raise AttributeError("%r object has no attribute %r" %
                                 (type(self).__name__, name))

    def __setattr__(self, name, value):
        """Variable names as attributes."""
        for i, arg in enumerate(self.sig):
            if arg.name == name:
                self[i] = value
                return
        list.__setattr__(self, name, value)

    def copy(self):
        """Create a copy."""
        return type(self)(self.sig, *self[1:])

    def argdict(self):
        """Create a dictionary of the calls arguments."""
        return dict((arg.name, val) for arg, val in zip(self.sig, self))

    def restrict_once(self):
        """Restrict integer arguments with mimum expressions once."""
        l = list(self)
        for i, arg in enumerate(self.sig):
            if self[i] is not None and arg.min:
                try:
                    self[i] = max(self[i], arg.min(*l))
                except TypeError:
                    pass  # probably a None
            if self[i] is not None and arg.max:
                try:
                    self[i] = min(self[i], arg.max(*l))
                except TypeError:
                    pass  # probably a None

    def restrict(self):
        """Restrict integer arguments with mimum expressions."""
        calls = []
        while self[1:] not in calls:
            calls.append(self[1:])
            self.restrict_once()

    def complete_once(self):
        """Attempt to complete arguments with minimum expressions once."""
        l = list(self)
        for i, arg in enumerate(self.sig):
            if self[i] is None:
                if arg.min:
                    try:
                        self[i] = arg.min(*l)
                    except TypeError:
                        pass  # probably a None
                else:
                    self[i] = arg.default()

    def complete(self):
        """Attempt to complete all arguments with minimum expressions."""
        calls = []
        while self[1:] not in calls:
            calls.append(self[1:])
            self.complete_once()

    def properties(self, argid=None):
        """Return a list of properties for the arguments."""
        if argid:
            return self.sig[argid].properties(*self)
        return tuple(arg.properties(*self) for arg in self.sig)

    def flops(self):
        """Compute the call flops."""
        if self.sig.flops is not None:
            return self.sig.flops(*self)
        return None

    def format_sampler(self):
        """Format for a sampler."""
        return [arg.format_sampler(val) for arg, val in zip(self.sig, self)]


class Arg(object):

    """Base class for signature arguments."""

    class __metaclass__(type):

        """Meta class for Arg."""

        def __repr__(cls):
            """Class name as representation."""
            return cls.__name__

    def __init__(self, name, attr=None):
        """Keep name and attributes."""
        self.name = name
        self.propertiesstr = attr

    def __repr__(self):
        """Format as python parsable string."""
        args = [self.name]
        if self.propertiesstr:
            args.append(self.propertiesstr)
        args = map(repr, args)
        return "%s(%s)" % (type(self).__name__, ", ".join(args))

    def __str__(self):
        """Format as human readable."""
        return str(self.name)

    def __eq__(self, other):
        """Compare with other argument."""
        return (type(self) == type(other) and
                self.name == other.name and
                self.propertiesstr == other.propertiesstr)

    @staticmethod
    def format_sampler(val):
        """Format value for a sampler."""
        return val


class Name(Arg):

    """Name argument."""

    def __eq__(self, other):
        """Check for equality."""
        return Arg.__eq__(self, other) or self.name == other

    def default(self):
        """Default: Kernel name."""
        return self.name


class Flag(Arg):

    """Flag argument."""

    def __init__(self, name, flags, attr=None):
        """Initalize with name and list of possible flags."""
        Arg.__init__(self, name, attr)
        self.flags = flags

    def __repr__(self):
        """Format as python parsable string."""
        args = [self.name, self.flags]
        if self.propertiesstr:
            args.append(self.propertiesstr)
        args = map(repr, args)
        return "%s(%s)" % (type(self).__name__, ", ".join(args))

    def __eq__(self, other):
        """Compare with other."""
        return Arg.__eq__(self, other) and self.flags == other.flags

    def default(self):
        """Default: first possible flag."""
        return self.flags[0]


def _create_Flag(classname, defaultname, flags):
    """Class factory for Flag arguments."""
    def __init__(self, name=defaultname, attr=None):
        """Initialize custom Flag."""
        Flag.__init__(self, name, flags, attr)

    def __repr__(self):
        """Format as python parsable string."""
        args = []
        if self.name != defaultname:
            args.append(self.name)
            if self.propertiesstr:
                args.append(self.propertiesstr)
            args = map(repr, args)
        elif self.propertiesstr:
            args.append("attr=%r" % self.propertiesstr)
        return "%s(%s)" % (type(self).__name__, ", ".join(args))

    globals()[classname] = type(classname, (Flag,), {
        "__init__": __init__,
        "__repr__": __repr__
    })

_create_Flag("Side", "side", ("L", "R"))
_create_Flag("Uplo", "uplo", ("L", "U"))
_create_Flag("Trans", "trans", ("N", "T"))
_create_Flag("cTrans", "trans", ("N", "T", "C"))
_create_Flag("Diag", "diag", ("N", "U"))


class ArgWithMin(Arg):

    """Base class for Arguments with a minstr."""

    def __init__(self, name, min=None, attr=None, max=None):
        """Optional minimum expression."""
        Arg.__init__(self, name, attr)
        self.minstr = min
        self.maxstr = max

    def __repr__(self):
        """Format as python parsable string."""
        args = [self.name]
        if self.minstr:
            args.append(self.minstr)
        if self.propertiesstr:
            if not self.minstr:
                args.append(None)
            args.append(self.propertiesstr)
        if self.maxstr:
            if not self.minstr:
                args.append(None)
            if not self.propertiesstr:
                args.append(None)
            args.append(self.maxstr)
        args = map(repr, args)
        return "%s(%s)" % (type(self).__name__, ", ".join(args))

    def __eq__(self, other):
        """Compare for equality."""
        return Arg.__eq__(self, other) and (self.minstr == other.minstr and
                                            self.maxstr == other.maxstr)

    def default(self):
        """Default: 1."""
        if self.minstr is None:
            return 1
        return None


class Dim(ArgWithMin):

    """Dimension argument."""

    pass


class Scalar(Arg):

    """Scalar argument."""

    typename = None

    def __init__(self, name="alpha", attr=None):
        """Initialize (no special case)."""
        Arg.__init__(self, name, attr)

    def __repr__(self):
        """Format as python parsable string."""
        args = []
        if self.name != "alpha":
            args.append(repr(self.name))
            if self.propertiesstr:
                args.append(repr(self.propertiesstr))
        elif self.propertiesstr:
            args.append("attr=%r" % self.propertiesstr)
        return "%s(%s)" % (type(self).__name__, ", ".join(args))

    @staticmethod
    def default():
        """Default: 1.0."""
        return 1.0


def _create_Scalar(classname, typename):
    """Class factory Scalar arguments."""
    attributes = {"typename": typename}
    if "complex" in typename:

        def format_sampler(self, val):
            """Format complex number as tuple of two reals."""
            if isinstance(val, numbers.Number):
                val = complex(val)
                return "%s,%s" % (val.real, val.imag)
            return val
        attributes["format_sampler"] = format_sampler
    if typename == "integer":

        @staticmethod
        def default():
            """Default: 1."""
            return 1
        attributes["default"] = default
    globals()[classname] = type(classname, (Scalar,), attributes)

_create_Scalar("iScalar", "integer")
_create_Scalar("sScalar", "single precision")
_create_Scalar("dScalar", "double precision")
_create_Scalar("cScalar", "single precision complex")
_create_Scalar("zScalar", "double precision complex")


class Data(ArgWithMin):

    """Data (operand) argument."""

    typename = None

    def format_sampler(self, val):
        """Format surrounded by [] for the sampler."""
        if isinstance(val, int):
            return "[" + str(val) + "]"
        return val


def _create_Data(classname, typename):
    """Class factory Data arguments."""
    attributes = {"typename": typename}
    if "complex" in typename:
        def format_sampler(self, val):
            """Format surrounded by [] for the sampler.

            2x space (for real and complex parts).
            """
            if isinstance(val, int):
                return "[" + str(2 * val) + "]"
            return val
        attributes["format_sampler"] = format_sampler
    globals()[classname] = type(classname, (Data,), attributes)

_create_Data("iData", "integer")
_create_Data("sData", "single precision")
_create_Data("dData", "double precision")
_create_Data("cData", "single precision complex")
_create_Data("zData", "double precision complex")


class Ld(ArgWithMin):

    """Leading dimension argument."""

    @staticmethod
    def format_sampler(val):
        """For Sampler: minimum = 1."""
        return max(1, val)


class Inc(Arg):

    """Increment argument."""

    @staticmethod
    def default():
        """Default: 1."""
        return 1


class Work(Data):

    """Work space argument."""

    pass


def _create_Work(classname, dataclass):
    """Class factory Work arguments."""
    globals()[classname] = type(classname, (Work, dataclass), {})

_create_Work("iWork", iData)
_create_Work("sWork", sData)
_create_Work("dWork", dData)
_create_Work("cWork", cData)
_create_Work("zWork", zData)


class Lwork(ArgWithMin):

    """Work size argument."""

    pass


class Info(Arg):

    """Info argument."""

    def __init__(self, name="info", attr=None):
        """Initialize (no special case)."""
        Arg.__init__(self, name, attr)

    @staticmethod
    def default():
        """Default: 0."""
        return 0


class String(Arg):

    """String argument."""

    @staticmethod
    def default():
        """Default: '' (empty string)."""
        return ""
