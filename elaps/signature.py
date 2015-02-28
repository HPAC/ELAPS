#!/usr/bin/env python
"""Python representations of kernel signatures."""
from __future__ import division, print_function

import numbers

# environment for evaluations
eval_replace = {
    "lower": repr("lower"),
    "upper": repr("upper"),
    "symm": repr("symm"),
    "herm": repr("herm"),
    "work": repr("work"),
}


class Signature(list):

    """Representaiton of a kernel signature."""

    def __init__(self, *args, **kwargs):
        """Initialize from file ore arguments."""
        # TODO: remove file loader?
        if "file" in kwargs:
            self.filename = kwargs["file"]
            # read signature from file
            try:
                with open(self.filename) as fin:
                    sig = eval(fin.read())
            except:
                raise IOError(self.filename + " could not be loaded")
            if not isinstance(sig, Signature):
                raise TypeError(self.filename + " did not conatin a Signature")
            # initialize from loaded signature
            list.__init__(self, sig)
            self.complexitystr = sig.complexitystr
            self.complexity = sig.complexity
            return

        # set attributes
        list.__init__(self, args)
        self.filename = None
        self.complexitystr = None
        self.complexity = None

        if not isinstance(self[0], Name):
            self[0] = Name(self[0])

        # infer and compile complexity, min, attr
        self.init_lambdas(kwargs)

    def init_lambdas(self, kwargs):
        """Initialize lambda expressions."""
        lambdaargs = ", ".join(arg.name for arg in self)
        if "complexity" in kwargs:
            lambdarhs = kwargs["complexity"]
            for key, value in eval_replace.iteritems():
                lambdarhs = lambdarhs.replace(key, value)
            self.complexitystr = kwargs["complexity"]
            self.complexity = eval("lambda %s: %s" % (lambdaargs, lambdarhs))
        for arg in self:
            if hasattr(arg, "minstr") and arg.minstr:
                lambdarhs = arg.minstr
                for key, value in eval_replace.iteritems():
                    lambdarhs = lambdarhs.replace(key, value)
                arg.min = eval("lambda %s: %s" % (lambdaargs, lambdarhs))
            else:
                arg.min = None
            if arg.propertiesstr:
                lambdarhs = arg.propertiesstr
                for key, value in eval_replace.iteritems():
                    lambdarhs = lambdarhs.replace(key, value)
                arg.properties = eval("lambda %s: filter(None, (%s,))" %
                                      (lambdaargs, lambdarhs))
            else:
                arg.properties = lambda *args: ()

    def __str__(self):
        """Format as human readable."""
        return (self[0].name + "(" +
                ", ".join(arg.name for arg in self[1:]) + ")")

    def __repr__(self):
        """Format as python parsable string."""
        args = [repr(self[0].name)] + map(repr, self[1:])
        if self.complexity:
            args.append("complexity=" + repr(self.complexitystr))
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    def __call__(self, *args):
        """Create a call from the signature with given arguments."""
        if len(args) == 0:
            args = tuple(arg.default() for arg in self[1:])
        return Call(self, *args)

    def dataargs(self):
        """Return a list of data argument positions."""
        return [argid for argid, arg in enumerate(self)
                if isinstance(arg, Data)]

    def datatype(self):
        """Deduce type of perands (single, double, complex, ...)."""
        # datatype is type of first dataarg
        return self[self.dataargs()[0]].typename


class Call(list):

    """A call for to a signature."""

    def __init__(self, sig, *args):
        """Initialize from signature and arguments."""
        if not isinstance(sig, Signature):
            raise TypeError("a Signature is requred as first argument")
        if len(args) != len(sig) - 1:
            raise TypeError(sig[0].name + "() takes exactly " +
                            str(len(sig) - 1) + " arguments (" +
                            str(len(args)) + " given)")
        list.__init__(self, (sig[0].name,) + args)
        self.__dict__["sig"] = sig

    def __str__(self):
        """Foramt as human readable."""
        return str(self[0]) + "(" + ", ".join(map(str, self[1:])) + ")"

    def __repr__(self):
        """Format as python parsable string."""
        return (type(self).__name__ + "(" + repr(self.sig) + ", " +
                ", ".join(map(repr, self[1:])) + ")")

    def __getattr__(self, name):
        """Variable names as attributes."""
        for i, arg in enumerate(self.sig):
            if arg.name == name:
                return self[i]
        raise AttributeError("%r object has no attribute %r" %
                             (type(self), name))

    def __setattr__(self, name, value):
        """Variable names as attributes."""
        for i, arg in enumerate(self.sig):
            if arg.name == name:
                self[i] = value
                return
        raise AttributeError("%r object has no attribute %r" %
                             (type(self), name))

    def __copy__(self):
        """Create a deep copy."""
        return Call(self.sig, *self[1:])

    def copy(self):
        """Create a deep copy."""
        return self.__copy__()

    def argdict(self):
        """Create a dictionary of the calls arguments."""
        return {arg.name: val for arg, val in zip(self.sig, self)}

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

    def complexity(self):
        """Compute the call complexity."""
        if self.sig.complexity is not None:
            return self.sig.complexity(*self)
        return None

    def format_str(self):
        """Format as a tuple of strings."""
        return tuple(arg.format_str(val)
                     for arg, val in zip(self.sig, self))

    def format_sampler(self):
        """Format for a sampler."""
        return [arg.format_sampler(val) for arg, val in zip(self.sig, self)]


class Arg(object):

    """Base class for signature arguments."""

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
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    def __str__(self):
        """Format as human readable."""
        return str(self.name)

    def __eq__(self, other):
        """Compare with other argument."""
        return (type(self) == type(other) and
                self.name == other.name and
                self.propertiesstr == other.propertiesstr)

    @staticmethod
    def format_str(val):
        """Format value as a string."""
        return str(val)

    def format_sampler(self, val):
        """Format value for a sampler."""
        return self.format_str(val)


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
        """Init with name nad list of possible flags."""
        Arg.__init__(self, name, attr)
        self.flags = flags

    def __repr__(self):
        """Format as python parsable string."""
        args = [self.name, self.flags]
        if self.propertiesstr:
            args.append(self.propertiesstr)
        args = map(repr, args)
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    def __eq__(self, other):
        """Compare with other."""
        return Arg.__eq__(self, other) and self.flags == other.flags

    def default(self):
        """Default: first possible falg."""
        return self.flags[0]


def _create_Flag(classname, defaultname, flags):
    """Class factory for Flag arguments."""
    def __init__(self, name=defaultname, attr=None):
        """Initialize custon Flag."""
        Flag.__init__(self, name, flags, attr)

    def __repr__(self):
        """Format as python parsable string."""
        args = []
        if self.name != defaultname:
            args.append(repr(self.name))
            if self.propertiesstr:
                args.append(repr(self.propertiesstr))
        elif self.propertiesstr:
            args.append("attr=%r" % self.propertiesstr)
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    class_ = type(classname, (Flag,), {
        "__init__": __init__,
        "__repr__": __repr__
    })
    globals()[classname] = class_
    return class_

_create_Flag("Side", "side", ("L", "R"))
_create_Flag("Uplo", "uplo", ("L", "U"))
_create_Flag("Trans", "trans", ("N", "T"))
_create_Flag("cTrans", "trans", ("N", "C"))
_create_Flag("Diag", "diag", ("N", "U"))


class Dim(Arg):

    """Dimension argument."""

    def __init__(self, name, min_=None, attr=None):
        """Optional minimum expression."""
        Arg.__init__(self, name, attr)
        self.minstr = min_

    def __repr__(self):
        """Format as python parsable string."""
        args = [self.name]
        if self.minstr:
            args.append(self.minstr)
        if self.propertiesstr:
            if not self.minstr:
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    def __eq__(self, other):
        """Compare for equality."""
        return Arg.__eq__(self, other) and self.minstr == other.minstr

    def default(self):
        """Default: 0."""
        if self.minstr is None:
            return 0
        return None


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
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    @staticmethod
    def default():
        """Default: 1."""
        return 1


class iScalar(Scalar):

    """Integer scalar argument."""

    typename = "integer"


class sScalar(Scalar):

    """Integer scalar argument."""

    typename = "single precision"


class dScalar(Scalar):

    """Double precision scalar argument."""

    typename = "double precision"


class cScalar(Scalar):

    """Single precision complex scalar argument."""

    typename = "single precision complex"

    def format_sampler(self, val):
        """Format python complex value as list for the smapler."""
        if isinstance(val, numbers.Number):
            val = complex(val)
            return str(val.real) + "," + str(val.imag)
        return val


class zScalar(Scalar):

    """Double precision complex scalar argument."""

    typename = "double precision complex"

    def format_sampler(self, val):
        """Format python complex value as list for the smapler."""
        if isinstance(val, numbers.Number):
            val = complex(val)
            return "%s,%s" %(val.real, val.imag)
        return val


class Data(Arg):

    """Data (operand) argument."""

    typename = None

    def __init__(self, name, min_=None, attr=None):
        """Init: minimum expression possible."""
        Arg.__init__(self, name, attr)
        self.minstr = min_

    def __repr__(self):
        """Format as python parsable string."""
        args = [self.name]
        if self.minstr:
            args.append(self.minstr)
            if self.propertiesstr:
                args.append(repr(self.propertiesstr))
        elif self.propertiesstr:
            args.append("attr=%r" % self.propertiesstr)
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    def __eq__(self, other):
        """Compare for equality."""
        return Arg.__eq__(self, other) and self.minstr == other.minstr

    def default(self):
        """Default: 1."""
        if self.minstr is None:
            return 1
        return None

    def format_str(self, val):
        """Format surrounded by [] for the sampler."""
        if isinstance(val, int):
            return "[" + str(val) + "]"
        return str(val)


class iData(Data):

    """Integer data argument."""

    typename = "integer"


class sData(Data):

    """Single precision data argument."""

    typename = "single precision"


class dData(Data):

    """Double precision data argument."""

    typename = "double precision"


class cData(Data):

    """Single precision complex data argument."""

    typename = "single precision complex"

    def format_sampler(self, val):
        """Requrest 2x space (for real, compex parts)."""
        if isinstance(val, int):
            val *= 2
        return val


class zData(Data):

    """Double precision complex data argument."""

    typename = "double precision complex"

    def format_sampler(self, val):
        """Requrest 2x space (for real, compex parts)."""
        if isinstance(val, int):
            val *= 2
        return val


class Ld(Arg):

    """Leading dimension argument."""

    def __init__(self, name, min_=None, attr=None):
        """Init: minimum expression possible."""
        Arg.__init__(self, name, attr)
        self.minstr = min_

    def __repr__(self):
        """Format as python parsable string."""
        args = [self.name]
        if self.minstr:
            args.append(self.minstr)
            if self.propertiesstr:
                args.append(repr(self.propertiesstr))
        elif self.propertiesstr:
            args.append("attr=%r" % self.propertiesstr)
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    def __eq__(self, other):
        """Compare for equality."""
        return Arg.__eq__(self, other) and self.minstr == other.minstr

    @staticmethod
    def format_sampler(val):
        """For Sampler: minimum = 1."""
        return str(max(1, val))

    def default(self):
        """Default: 1."""
        if self.minstr is None:
            return 1
        return None


class Inc(Arg):

    """Increment argument."""

    @staticmethod
    def default():
        """Default: 1."""
        return 1


class Work(Data):

    """Work space argument."""

    def __init__(self, name, min_=None, attr=None):
        """Set the "work" attribute."""
        if not attr:
            Data.__init__(self, name, min_, "work")
        else:
            Data.__init__(self, name, min_, "work, " + attr)


class iWork(Work, iData):

    """Double precision work argument."""

    pass


class sWork(Work, sData):

    """Double precision work argument."""

    pass


class dWork(Work, dData):

    """Double precision work argument."""

    pass


class cWork(Work, cData):

    """Double precision work argument."""

    pass


class zWork(Work, zData):

    """Double precision work argument."""

    pass


class Lwork(Arg):

    """Work size argument."""

    def __init__(self, name, min_=None, attr=None):
        """Init: minimum expression possible."""
        Arg.__init__(self, name, attr)
        self.minstr = min_

    def __repr__(self):
        """Format as python parsable string."""
        args = [self.name]
        if self.minstr:
            args.append(self.minstr)
            if self.propertiesstr:
                args.append(repr(self.propertiesstr))
        elif self.propertiesstr:
            args.append("attr=%r" % self.propertiesstr)
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    def __eq__(self, other):
        """Compare for equality."""
        return Arg.__eq__(self, other) and self.minstr == other.minstr

    def default(self):
        """Default: 1."""
        if self.minstr is None:
            return 1
        return None


class Info(Arg):

    """Info argument."""

    def __init__(self, name="info", attr=None):
        """Init (no special case)."""
        Arg.__init__(self, name, attr)

    @staticmethod
    def default():
        """Default: 0."""
        return 0
