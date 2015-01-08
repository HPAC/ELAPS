#!/usr/bin/env python
from __future__ import division, print_function

import numbers


class Signature(list):
    def __init__(self, *args, **kwargs):
        if "file" in kwargs:
            self.filename = kwargs["file"]
            # read signature from file
            try:
                with open(self.filename) as fin:
                    sig = eval(fin.read())
            except:
                raise TypeError(self.filename + "could not be loaded")
            if not isinstance(sig, Signature):
                raise TypeError(self.filename + "did not conatin a Signature")
            # initialize from loaded signature
            list.__init__(self, sig)
            self.complexity = sig.complexity
            return
        # set attributes
        list.__init__(self, args)
        self.complexity = None
        self.filename = None
        if "complexity" in kwargs:
            self.complexity = kwargs["complexity"]

        # infer and compile min and attr
        if not isinstance(self[0], Name):
            self[0] = Name(self[0])
        lambdaargs = ", ".join(arg.name for arg in self)
        for arg in self:
            if hasattr(arg, "minstr") and arg.minstr:
                arg.min = eval("lambda " + lambdaargs + ": " + arg.minstr)
            else:
                arg.min = None
            if arg.propertiesstr:
                arg.properties = eval("lambda " + lambdaargs +
                                      ": filter(None, (" + arg.propertiesstr +
                                      ",))")
            else:
                arg.properties = lambda *args: ()

    def __str__(self):
        return (self[0].name + "(" +
                ", ".join(arg.name for arg in self[1:]) + ")")

    def __repr__(self):
        return (self.__class__.__name__ + "(" + repr(self[0].name) + ", "
                + ", ".join(map(repr, self[1:])) + ")")

    def __call__(self, *args):
        if len(args) == 0:
            args = tuple(arg.default() for arg in self[1:])
        return Call(self, *args)

    def dataargs(self):
        return [argid for argid, arg in enumerate(self)
                if isinstance(arg, Data)]


class Call(list):
    def __init__(self, sig, *args):
        if not isinstance(sig, Signature):
            raise TypeError("a Signature is requred as first argument")
        if len(args) != len(sig) - 1:
            raise TypeError(sig[0].name + "() takes exactly " +
                            str(len(sig) - 1) + " arguments (" +
                            str(len(args)) + " given)")
        list.__init__(self, (sig[0].name,) + args)
        self.__dict__["sig"] = sig

    def __str__(self):
        return str(self[0]) + "(" + ", ".join(map(str, self[1:])) + ")"

    def __repr__(self):
        return (self.__class__.__name__ + "(" + repr(self.sig) + ", " +
                ", ".join(map(repr, self[1:])) + ")")

    def __getattr__(self, name):
        for i, arg in enumerate(self.sig):
            if arg.name == name:
                return self[i]
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))

    def __setattr__(self, name, value):
        for i, arg in enumerate(self.sig):
            if arg.name == name:
                self[i] = value
                return
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))

    def __copy__(self):
        return Call(self.sig, *self[1:])

    def copy(self):
        return self.__copy__()

    def argdict(self):
        return {arg.name: val for arg, val in zip(self.sig, self)}

    def complete_once(self):
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
        calls = []
        while self[1:] not in calls:
            calls.append(self[1:])
            self.complete_once()

    def clear_completable(self):
        for i, arg in enumerate(self.sig):
            if arg.min:
                self[i] = None

    def properties(self, argid=None):
        if argid:
            return self.sig[argid].properties(*self)
        return [arg.properties(*self) for arg in self.sig]

    def format_str(self):
        return tuple(arg.format_str(val)
                     for arg, val in zip(self.sig, self))

    def format_sampler(self):
        return [arg.format_sampler(val) for arg, val in zip(self.sig, self)]


class Arg(object):
    def __init__(self, name, attr=None):
        self.name = name
        self.propertiesstr = attr

    def __repr__(self):
        args = [self.name]
        if self.propertiesstr:
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"

    def __str__(self):
        return str(self.name)

    def format_str(self, val):
        return str(val)

    def format_sampler(self, val):
        return self.format_str(val)


class Name(Arg):
    def default(self):
        return self.name


class Flag(Arg):
    def __init__(self, name, flags, attr=None):
        Arg.__init__(self, name, attr)
        self.flags = flags

    def __repr__(self):
        args = [self.name, self.flags]
        if self.propertiesstr:
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"

    def default(self):
        return self.flags[0]


class Side(Flag):
    def __init__(self, name="side", attr=None):
        Flag.__init__(self, name, ["L", "R"], attr)

    def __repr__(self):
        args = []
        if self.name != "side":
            args.append(self.name)
        if self.propertiesstr:
            if self.name == "side":
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"


class Uplo(Flag):
    def __init__(self, name="uplo", attr=None):
        Flag.__init__(self, name, ["L", "U"], attr)

    def __repr__(self):
        args = []
        if self.name != "uplo":
            args.append(self.name)
        if self.propertiesstr:
            if self.name == "uplo":
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"


class Trans(Flag):
    def __init__(self, name="trans", attr=None):
        Flag.__init__(self, name, ["N", "T"], attr)

    def __repr__(self):
        args = []
        if self.name != "trans":
            args.append(self.name)
        if self.propertiesstr:
            if self.name == "trans":
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"


class Diag(Flag):
    def __init__(self, name="diag", attr=None):
        Flag.__init__(self, name, ["N", "U"], attr)

    def __repr__(self):
        args = []
        if self.name != "diag":
            args.append(self.name)
        if self.propertiesstr:
            if self.name == "diag":
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"


class Dim(Arg):
    def __init__(self, name, min=None, attr=None):
        Arg.__init__(self, name, attr)
        self.minstr = min

    def __repr__(self):
        args = [self.name]
        if self.minstr:
            args.append(self.minstr)
        if self.propertiesstr:
            if not self.minstr:
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"

    def default(self):
        if self.minstr is None:
            return 0
        return None


class Scalar(Arg):
    def __init__(self, name="alpha", attr=None):
        Arg.__init__(self, name, attr)

    def __repr__(self):
        args = []
        if self.name != "alpha":
            args.append(self.name)
        if self.propertiesstr:
            if self.name == "alpha":
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"

    def default(self):
        return 1


class iScalar(Scalar):
    typename = "integer"


class sScalar(Scalar):
    typename = "single precision"


class dScalar(Scalar):
    typename = "double precision"


class cScalar(Scalar):
    typename = "single precision complex"

    def format_sampler(self, val):
        if isinstance(val, numbers.Number):
            val = complex(val)
            return str(val.real) + "," + str(val.imag)
        return val


class zScalar(Scalar):
    typename = "double precision complex"

    def format_sampler(self, val):
        if isinstance(val, numbers.Number):
            val = complex(val)
            return str(val.real) + "," + str(val.imag)
        return val


class Data(Arg):
    def __init__(self, name, min=None, attr=None):
        Arg.__init__(self, name, attr)
        self.minstr = min

    def __repr__(self):
        args = [self.name]
        if self.minstr:
            args.append(self.minstr)
        if self.propertiesstr:
            if self.minstr:
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"

    def default(self):
        if self.minstr is None:
            return 1
        return None

    def format_str(self, val):
        if isinstance(val, int):
            return "[" + str(val) + "]"
        return str(val)


class iData(Data):
    typename = "integer"


class sData(Data):
    typename = "single precision"


class dData(Data):
    typename = "double precision"


class cData(Data):
    typename = "single precision complex"

    def format_sampler(self, val):
        if isinstance(val, int):
            val *= 2
        return val


class zData(Data):
    typename = "double precision complex"

    def format_sampler(self, val):
        if isinstance(val, int):
            val *= 2
        return val


class Ld(Arg):
    def __init__(self, name, min=None, attr=None):
        Arg.__init__(self, name, attr)
        self.minstr = min

    def __repr__(self):
        args = [self.name]
        if self.minstr:
            args.append(self.minstr)
        if self.propertiesstr:
            if self.minstr:
                args.append(None)
            args.append(self.propertiesstr)
        args = map(repr, args)
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"

    def default(self):
        if self.minstr is None:
            return 1
        return None


class Inc(Arg):
    def default(self):
        return 1

# attr
lower = "lower"
upper = "upper"
symm = "symm"
herm = "herm"
