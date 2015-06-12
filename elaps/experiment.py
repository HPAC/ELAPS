#!/usr/bin/env python
"""Central ELAPS:Experiment."""
from __future__ import division, print_function

import defines
import symbolic
import signature

from collections import Iterable, defaultdict
from itertools import chain
import warnings
import os
from copy import deepcopy
from numbers import Number


class Experiment(object):

    """ELAPS:Experiment."""

    def __init__(self, other=None, **kwargs):
        """Initialize experiment from (optional) other expeirment."""
        # empty experiment
        self.note = ""
        self.sampler = None
        self.papi_counters = []
        self.nthreads = 1
        self.script_header = ""
        self.range = None
        self.range_randomize_data = False
        self.nreps = 1
        self.sumrange = None
        self.sumrange_parallel = False
        self.calls_parallel = False
        self.calls = []
        self.vary = {}

        # initialize from argument
        otherdict = other.__dict__ if isinstance(other, Experiment) else {}
        for key, value in chain(otherdict, kwargs.items()):
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                warnings.warn("%s doesn't support the key %r" %
                              (type(self).__name__, key), Warning)

        self.update_vary()

    def __repr__(self):
        """Python parsable representation."""
        self.update_vary()

        empty = Experiment()

        # Only print non-default attribute values
        changed = dict((key, value) for key, value in self.__dict__.items()
                       if value != getattr(empty, key))

        # remove kernels and backend
        if "sampler" in changed:
            changed["sampler"] = self.sampler.copy()
            for key in ("kernels", "backend", "papi_counters_avail"):
                if key in changed["sampler"]:
                    del changed["sampler"][key]

        # simplify vary
        if "vary" in changed:
            changedvary = {}
            for name, vary in changed["vary"].items():
                vary = vary.copy()
                if not vary["with"]:
                    del vary["with"]
                if vary["along"] == len(self.get_operand(name)["dims"]) - 1:
                    del vary["along"]
                if vary["offset"] == 0:
                    del vary["offset"]
                if vary:
                    changedvary[name] = vary
            del changed["vary"]
            if changedvary:
                changed["vary"] = changedvary

        args = ["%s=%r" % keyval for keyval in changed.items()]
        return "%s(%s)" % (type(self).__name__, ", ".join(args))

    def __str__(self):
        """Readable string representation."""
        self.update_vary()
        result = ""
        if self.note:
            result += "Note:\t%s\n" % self.note
        if self.sampler:
            result += "Sampler:\t%s (%s, %s)\n" % (self.sampler["name"],
                                                   self.sampler["system_name"],
                                                   self.sampler["blas_name"])
        if isinstance(self.nthreads, int):
            result += "#threads:\t%s\n" % self.nthreads
        if self.script_header:
            result += "Header:\t%s\n" % self.script_header
        indent = ""
        if self.range:
            result += "for %s = %s :\n" % tuple(self.range)
            indent += "    "
        if not isinstance(self.nthreads, int):
            result += indent + "#threads = %s\n" % self.nthreads
        result += indent + "repeat %s times:\n" % self.nreps
        indent += "    "
        if self.sumrange:
            result += indent
            if self.sumrange_parallel:
                result += "in parallel"
            else:
                result += "sum over"
            result += " %s = %s" % tuple(self.sumrange)
            result += ":\n"
            indent += "    "
        if self.calls_parallel:
            result += indent + "in parallel:\n"
            indent += "    "
        for call in self.calls:
            if not isinstance(call, signature.Call):
                result += str(call) + "\n"
                continue
            call = call.copy()
            for argid in call.sig.dataargs():
                name = call[argid]
                self.update_vary(name)
                with_ = list(self.vary[name]["with"])
                if len(with_) == 1:
                    name += "_" + str(with_[0])
                elif len(with_) > 1:
                    name += "_(%s)" % ",".join(with_)
                call[argid] = name
            result += indent + str(call) + "\n"
        return result[:-1]

    def __eq__(self, other):
        """Compare with other Experiment for equality."""
        if not isinstance(other, type(self)):
            return False
        return self.__dict__ == other.__dict__

    def copy(self):
        """Create a deep copy of the experiment."""
        return Experiment(deepcopy(self.__dict__))

    # properties

    @property
    def call(self):
        """Return call if there is only one."""
        if len(self.calls) > 1:
            raise AttributeError("Cannot access 'call' attribute when there "
                                 "is more than one call")
        return self.calls[0]

    @call.setter
    def call(self, call):
        """Set a single call."""
        self.calls = [call]

    @property
    def operands(self):
        """List of all operands."""
        return tuple(set([
            call[argid]
            for call in self.calls
            if isinstance(call, signature.Call)
            for argid in call.sig.dataargs()
            if isinstance(call[argid], str)
        ]))

    @property
    def range_var(self):
        """Return the range variable if set."""
        return self.range[0]

    @range_var.setter
    def range_var(self, value):
        """Set the range variable."""
        self.range[0] = value

    @property
    def range_vals(self):
        """Return the range values if set."""
        if self.range:
            return self.range[1]
        return None,

    @range_vals.setter
    def range_vals(self, value):
        """Set the range values."""
        self.range[1] = value

    @property
    def sumrange_var(self):
        """Return the sumrange variable if set."""
        return self.sumrange[0]

    @sumrange_var.setter
    def sumrange_var(self, value):
        """Set the sumrange variable."""
        self.sumrange[0] = value

    @property
    def sumrange_vals(self):
        """Return the sumrange values if set."""
        if self.sumrange:
            return self.sumrange[1]
        return None,

    @sumrange_vals.setter
    def sumrange_vals(self, value):
        """Set the sumrange values."""
        self.sumrange[1] = value

    # setters
    def set_sampler(self, sampler, force=False, check_only=False):
        """Set the Sampler."""
        # check completness
        for key in ("backend_name", "backend_header", "backend_prefix",
                    "backend_suffix", "backend_footer", "threads_per_core",
                    "ncores", "nt_max", "exe", "kernels", "omp_enabled",
                    "papi_enabled"):
            if key not in sampler:
                raise KeyError("Sampler is missing %r" % key)

        # PAPI
        if sampler["papi_enabled"]:
            papi_counters = []
            for counter in self.papi_counters:
                if counter not in sampler["papi_counters_avail"]:
                    if not force:
                        raise ValueError(
                            "Sampler doesn't support PAPI counter %r" % counter
                        )
                    continue
                papi_counters.append(counter)
            if len(papi_counters) > sampler["papi_counters_max"]:
                if not force:
                    raise ValueError("Sampler only supports %d counters" %
                                     sampler["papi_counters_max"])
                papi_counters = papi_counters[:sampler["papi_counters_max"]]
        else:
            if len(self.papi_counters):
                if not force:
                    raise ValueError("Sampler doesn't support PAPI")
            papi_counters = []
        self.papi_counters = papi_counters

        # thread count
        nthreads = self.nthreads
        if isinstance(nthreads, int):
            nt_max = sampler["nt_max"]
            if nthreads > nt_max:
                if not force:
                    raise ValueError("Sampler only supports %s threads" %
                                     nt_max)
                nthreads = nt_max

        # check OpenMP
        calls_parallel = self.calls_parallel
        sumrange_parallel = self.sumrange_parallel
        if not sampler["omp_enabled"]:
            if calls_parallel or sumrange_parallel:
                if not force:
                    raise ValueError("Sampler doesn't support OpenMP")
                calls_parallel = False
                sumrange_parallel = False

        # check kernel availability
        calls = []
        for call in self.calls:
            if call[0] not in sampler["kernels"]:
                if not force:
                    raise KeyError("Sampler doesn't support kernel %r" %
                                   call[0])
                continue
            sig = sampler["kernels"][call[0]]
            if len(sig) != len(call):
                if not force:
                    raise ValueError("Incompatible kernel: %r" % call[0])
                continue
            calls.append(call)

        if check_only:
            return

        # set new values
        self.sampler = sampler
        self.papi_counters = papi_counters
        self.nthreads = nthreads
        self.calls_parallel = calls_parallel
        self.sumrange_parallel = sumrange_parallel
        self.calls = calls

        self.update_vary()

    def set_papi_counters(self, papi_counters, force=False, check_only=False):
        """Set PAPI counters."""
        sampler = self.sampler

        if papi_counters is None:
            papi_counters = []

        # type check
        if not isinstance(papi_counters, (list, tuple)):
            raise TypeError("Expecting a list of counters.")

        # counters enabled?
        if not sampler["papi_enabled"]:
            if len(papi_counters):
                if not force:
                    raise ValueError("Sampler doesn't support PAPI")
                papi_counters = []
        else:
            # availablility
            papi_counters2 = []
            for counter in papi_counters:
                if counter not in sampler["papi_counters_avail"]:
                    if not force:
                        raise ValueError(
                            "Sampler doesn't support PAPI counter %r" % counter
                        )
                    continue
                papi_counters2.append(counter)
            papi_counters = papi_counters2

            # length
            if len(papi_counters) > sampler["papi_counters_max"]:
                if not force:
                    raise ValueError("Sampler only supports %s PAPI counters" %
                                     sampler["papi_counters_max"])
                papi_counters = papi_counters[:sampler["papi_counters_max"]]

        if check_only:
            return

        # set new values
        self.papi_counters = papi_counters

    def set_nthreads(self, nthreads, force=False, check_only=False):
        """Set number of threds."""
        if isinstance(nthreads, str):
            nthreads = self.ranges_parse(nthreads, dosumrange=False)
        if isinstance(nthreads, int):
            # check bounds
            nt_max = self.sampler["nt_max"]
            if nthreads > nt_max:
                if not force:
                    raise ValueError("Sampler only supports %s threads." %
                                     nt_max)
                nthreads = nt_max
        elif isinstance(nthreads, symbolic.Symbol):
            # check if == range_var
            if not self.range or nthreads != self.range_var:
                raise NameError("Invalid thread count: %s" % nthreads)
        else:
            raise TypeError("Invalid thread count: %s" % nthreads)

        if check_only:
            return

        # set new values
        self.nthreads = nthreads

    def set_range_var(self, range_var, force=False, check_only=False):
        """Set the range variabel."""
        # turn str to symbol
        if isinstance(range_var, str):
            if not range_var:
                if not force:
                    raise ValueError("Invalid range variable: %r" % range_var)
                range_var = "i"
            range_var = symbolic.Symbol(range_var)
        # check type
        if not isinstance(range_var, symbolic.Symbol):
            if not force:
                raise TypeError("Invalid range variable: %r" % range_var)
            range_var = symbolic.Symbol("i")
        # check conflict with sumrange
        if self.sumrange and range_var == self.sumrange_var:
            if not force:
                raise ValueError(
                    "Cannot use same variable for range and sumrange"
                )
            range_var = symbolic.Symbol("j" if range_var == "i" else "i")

        if check_only:
            return

        # range must exist to actually set it
        if not self.range:
            if not force:
                raise ValueError("Range is not enabled.")
            self.range = [range_var, symbolic.Range("1")]
        else:
            # set new value
            self.substitute(**self.ranges_valdict(range_var))
            self.range_var = range_var

    def set_range_vals(self, range_vals, force=False, check_only=False):
        """Set range values."""
        # parse string
        if isinstance(range_vals, str):
            if not range_vals:
                if not force:
                    raise ValueError("Empty range")
                range_vals = "1"
            range_vals = symbolic.Range(range_vals)

        # check for type
        if not isinstance(range_vals, (list, tuple, symbolic.Range)):
            if not force:
                raise TypeError("Invalid range: %r" % range_vals)
            range_vals = symbolic.Range("1")

        # check for unknown symbols
        if symbolic.findsymbols(range_vals):
            if not force:
                raise ValueError("Unknown symbols in range: %s" % range_vals)
            range_vals = symbolic.Range("1")

        # check for length
        if len(range_vals) == 0:
            if not force:
                raise ValueError("Empty range: %s" % range_vals)
            range_vals = symbolic.Range("1")

        if check_only:
            return

        # range must exist to actually set it
        if not self.range:
            if not force:
                raise ValueError("Range is not enabled.")
            self.set_range_var("i", force=True)

        # set new value
        self.range_vals = range_vals

    def set_range(self, range_, force=False, check_only=False):
        """Set the range."""
        if range_ is None:
            # disabling range
            if check_only:
                return
            if self.range:
                # use last range value
                range_val = tuple(self.range_vals)[-1]
                self.substitute(**self.ranges_valdict(range_val))
                self.range = None
            return

        range_var, range_vals = range_

        # checks
        self.set_range_var(range_var, force=force, check_only=True)
        self.set_range_vals(range_vals, force=force, check_only=True)

        if check_only:
            return

        # set new values
        self.range = [range_var, range_vals]
        self.set_range_var(range_var, force=force)
        self.set_range_vals(range_vals, force=force)

    def set_nreps(self, nreps, force=False, check_only=False):
        """Set repetition count."""
        # parse string
        if isinstance(nreps, str):
            if not nreps:
                if not force:
                    raise ValueError("Invalid repetition count: %r" % int)
                nreps = "1"
            nreps = int(nreps)

        # check type
        if not isinstance(nreps, int):
            if not force:
                raise TypeError("Invalid repetition count: %r" % int)
            nreps = 1

        # ensure > 0
        if nreps <= 0:
            if not force:
                raise ValueError("Invalid repetition count: %r" % int)
            nreps = 1

        if check_only:
            return

        self.nreps = nreps

    def set_sumrange_var(self, sumrange_var, force=False, check_only=False):
        """Set the sumrange variabel."""
        # turn str to symbol
        if isinstance(sumrange_var, str):
            if not sumrange_var:
                if not force:
                    raise ValueError("Invalid range variable: %r" %
                                     sumrange_var)
                sumrange_var = "j"
            sumrange_var = symbolic.Symbol(sumrange_var)

        # check type
        if not isinstance(sumrange_var, symbolic.Symbol):
            if not force:
                raise TypeError("Invalid range variable: %r" % sumrange_var)
            sumrange_var = symbolic.Symbol("j")

        # check conflict with range
        if self.range and sumrange_var == self.range_var:
            if not force:
                raise ValueError(
                    "Cannot use same variable for range and sumrange"
                )
            sumrange_var = symbolic.Symbol("i" if sumrange_var == "j" else "j")

        if check_only:
            return

        # range must exist to actually set it
        if not self.sumrange:
            if not force:
                raise ValueError("Sumrange is not enabled.")
            self.sumrange = [sumrange_var, symbolic.Range("1")]
        else:
            # set new value
            self.substitute(**self.ranges_valdict(None, sumrange_var))
            self.sumrange_var = sumrange_var

    def set_sumrange_vals(self, sumrange_vals, force=False, check_only=False):
        """Set sumrange values."""
        # parse string
        if isinstance(sumrange_vals, str):
            if not sumrange_vals:
                if not force:
                    raise ValueError("Empty range")
                sumrange_vals = "1"
            sumrange_vals = symbolic.Range(
                sumrange_vals, **self.ranges_vardict(dosumrange=False)
            )

        # check for type
        if not isinstance(sumrange_vals, (list, tuple, symbolic.Range)):
            if not force:
                raise TypeError("Invalid range: %r" % sumrange_vals)
            sumrange_vals = symbolic.Range("1")

        # check for unknown symbols
        symbols = symbolic.findsymbols(sumrange_vals)
        if symbols:
            if (not self.range or len(symbols) > 1 or
                    (len(symbols) == 1 and self.range_var not in symbols)):
                if not force:
                    raise ValueError("Unknown symbols in range: %s" %
                                     sumrange_vals)
                sumrange_vals = symbolic.Range("1")
        else:
            # check for length
            if len(sumrange_vals) == 0:
                if not force:
                    raise ValueError("Empty range: %s" % sumrange_vals)
                sumrange_vals = symbolic.Range("1")

        if check_only:
            return

        # sumrange must exist to actually set it
        if not self.sumrange:
            if not force:
                raise ValueError("Sumrange is not enabled.")
            self.set_sumrange_var("j", force=True)

        # set new value
        self.sumrange_vals = sumrange_vals

    def set_sumrange(self, sumrange, force=False, check_only=False):
        """Set the sumrange."""
        if sumrange is None:
            if check_only:
                return
            if self.sumrange:
                self.update_vary()
                for vary in self.vary.values():
                    vary["with"].discard(self.sumrange_var)
                range_val = tuple(self.range_vals)[-1]
                sumrange_val = tuple(self.sumrange_vals_at(range_val))[-1]
                self.substitute(**self.ranges_valdict(None, sumrange_val))
                self.sumrange = None
                self.sumrange_parallel = False
            return

        sumrange_var, sumrange_vals = sumrange

        # checks
        self.set_sumrange_var(sumrange_var, force=force, check_only=True)
        self.set_sumrange_vals(sumrange_vals, force=force, check_only=True)

        if check_only:
            return

        # set new values
        self.sumrange = [sumrange_var, sumrange_vals]
        self.set_sumrange_var(sumrange_var, force=force)
        self.set_sumrange_vals(sumrange_vals, force=force)

    def set_sumrange_parallel(self, sumrange_parallel=True, force=False,
                              check_only=False):
        """Set the parllalel sumrange option."""
        # convert to bool
        sumrange_parallel = bool(sumrange_parallel)

        # check availability
        if sumrange_parallel and not self.sampler["omp_enabled"]:
            if not force:
                raise ValueError("Sampler doesn't support OpenMP")
            sumrange_parallel = False

        if check_only:
            return

        # set new value
        self.sumrange_parallel = sumrange_parallel

    def set_calls_parallel(self, calls_parallel=True, force=False,
                           check_only=False):
        """Set the parllalel sumrange option."""
        # convert to bool
        calls_parallel = bool(calls_parallel)

        # check availability
        if calls_parallel and not self.sampler["omp_enabled"]:
            if not force:
                raise ValueError("Sampler doesn't support OpenMP")
            calls_parallel = False

        if check_only:
            return

        # set new value
        self.calls_parallel = calls_parallel

    def set_arg(self, callid, argid, value, force=False, check_only=False):
        """Set a call argument."""
        # check callid
        if not (0 <= callid < len(self.calls)):
            raise IndexError("Invalid callid: %s" % callid)

        call = self.calls[callid]

        # parse argname to argid
        if isinstance(argid, str) and isinstance(call, signature.Call):
            argname = argid
            argid = call.sig.argpos(argname)
            if argid is None:
                raise IndexError("Unknown argument name: %s" % argname)

        # check argid
        if argid == 0:
            raise IndexError("Cannot set routine name (argument 0)")

        arg = call.sig[argid]

        if isinstance(arg, signature.Arg):
            if isinstance(arg, signature.Flag):
                # check if flag is known
                if value not in arg.flags:
                    if not force:
                        raise ValueError("Unkonwn flag: %s" % value)
                    value = arg.flags[0]

                # TODO: check for changes?

                if check_only:
                    return

                # set new value
                call[argid] = value

                # apply connections
                connections = self.get_connections()
                self.apply_connections_to(callid, connections=connections)
                self.apply_connections_from(callid, connections=connections)

                return

            if isinstance(arg, signature.Data):
                # ensure value is str
                if not isinstance(value, str):
                    if not force:
                        raise TypeError("Operand arguments must be strings.")
                    value = str(value)
                if not value:
                    raise ValueError("Empty operand argument.")

                if value not in self.operands:
                    # no conflics
                    if check_only:
                        return

                    call[argid] = value
                    return

                operand = self.get_operand(value)
                oldoperand = self.get_operand(call[argid])

                # check type
                if operand["type"] != type(arg):
                    raise TypeError("Incompatible operand types: %r and %r" %
                                    (operand["type"].typename,
                                     type(arg).typename))

                # check compatibility
                if oldoperand != operand:
                    if not force:
                        raise ValueError("Incompatible operand sizes.")

                if check_only:
                    return

                # set new value
                call[argid] = value

                # apply connections
                connections = self.get_connections()
                self.apply_connections_to(callid, connections=connections)
                self.apply_connections_from(callid, connections=connections)

                self.update_vary()
                return

            # parse string
            if isinstance(value, str):
                value = self.ranges_parse(value)

            # check type
            if not isinstance(value, (int, symbolic.Expression)):
                if not force:
                    raise TypeError("Invalid argument type: %s" % value)
                value = 0

            # check min
            if arg.min:
                argmin = arg.min(*call)
                for range_val in self.range_vals:
                    if value == argmin:
                        break
                    for sumrange_val in self.sumrange_vals_at(range_val):
                        if value == argmin:
                            break
                        valdict = self.ranges_valdict(range_val, sumrange_val)
                        value_val = symbolic.simplify(value, **valdict)
                        argmin_val = symbolic.simplify(argmin, **valdict)
                        if value_val < argmin_val:
                            if not force:
                                raise ValueError("Value doesn't satisfy min")
                            value = argmin

            if check_only:
                return

            # set new value
            call[argid] = value

            # apply connections
            self.apply_connections_from(callid, argid)

            return

        # don't have a Signature
        if arg == "char*":
            if not isinstance(value, str):
                if not force:
                    raise TypeError("char* value must be str")
                value = str(value)
        else:
            try:
                value = self.ranges_parse(value)
            except:
                pass

        if check_only:
            return

        # set new value
        call[argid] = value

    def set_call(self, callid, call, force=False, check_only=False):
        """Set a call."""
        # check callid
        if callid == -1:
            # wrap -1 to append a call
            callid = len(self.calls)
        if not (0 <= callid <= len(self.calls)):
            if not force:
                raise IndexError("Invalid callid: %s" % callid)
            callid = max(0, min(callid, len(self.calls)))

        # None => remove call
        if call is None:
            self.remove_call(callid, check_only)
            return

        # check if kernel is available
        routine = call[0]
        if routine not in self.sampler["kernels"]:
            if not force:
                raise ValueError("Sampler doesn't support the kernel.")
            if check_only:
                return
            if callid < len(self.calls):
                self.calls.pop(callid)
            return

        # check type
        if not isinstance(call, signature.BasicCall):
            if isinstance(call, (tuple, list)):
                # generate BasicCall
                minsig = self.sampler["kernels"][routine]
                call = signature.BasicCall(minsig, *call[1:])
            else:
                raise TypeError("Invalid call: %s" % call)

        # check arguments
        if callid == len(self.calls):
            self.calls.append(None)
        oldcall = self.calls[callid]
        self.calls[callid] = call
        try:
            for argid in range(1, len(call)):
                self.set_arg(callid, argid, call[argid], force=force)
        finally:
            self.calls[callid] = oldcall
            if oldcall is None:
                self.calls = self.calls[:-1]

        if check_only:
            return

        # set new call
        if callid == len(self.calls):
            self.calls.append(None)
        self.calls[callid] = call
        for argid in range(1, len(call)):
            self.set_arg(callid, argid, call[argid], force=force)

    def add_call(self, call, force=False, check_only=False):
        """Add a call."""
        self.set_call(-1, call, force, check_only)

    def remove_call(self, callid, force=False, check_only=False):
        """Remove a call."""
        # check callid
        if not (0 <= callid < len(self.calls)):
            if not force:
                raise IndexError("Invalid callid: %s" % callid)
            callid = max(0, min(callid, len(self.calls) - 1))

        if check_only:
            return

        self.calls.pop(callid)

    def set_calls(self, calls, force=False, check_only=False):
        """Set all calls."""
        # check type
        if not isinstance(calls, list):
            raise TypeError("calls must be list (not %s)" % type(calls))

        # check consistency
        oldcalls = self.calls
        oldvary = self.vary
        self.calls = []
        self.vary = {}
        try:
            for call in calls:
                self.set_call(-1, call, force=force)
        finally:
            self.calls = oldcalls
            self.vary = oldvary

        if check_only:
            return

        # set new calls
        self.calls = []
        for call in calls:
            self.set_call(-1, call, force=force)

    def set_vary_with(self, name, with_, force=False, check_only=False):
        """Set the vary with option of an operand."""
        # operand existence
        if name not in self.operands:
            raise IndexError("Unknown operand: %s" % name)

        self.update_vary(name)

        # type conversion
        if isinstance(with_, (list, tuple)):
            with_ = set(with_)

        # type check
        if not isinstance(with_, set):
            raise TypeError("Invalid vary with type: %s" % with_)

        with2 = set()
        for with_var in with_:
            if with_var == "rep":
                with2.add(with_var)
                continue
            if self.sumrange and with_var == self.sumrange_var:
                with2.add(with_var)
                continue
            if not force:
                raise ValueError("Invlaid vary with entry: %s" % with_var)
        with_ = with2

        if check_only:
            return

        # set new value
        self.vary[name]["with"] = with_

    def add_vary_with(self, name, with_var, force=False, check_only=False):
        """Add a variable to the vary with option."""
        # operand existence
        if name not in self.operands:
            raise IndexError("Unknown operand: %s" % name)

        self.update_vary(name)

        # value/type check
        if with_var != "rep":
            if isinstance(with_var, str):
                with_var = self.ranges_parse(with_var, dorange=False)
            if not self.sumrange or with_var != self.sumrange_var:
                raise ValueError("Invalid vary with entry: %s" % with_var)

        if check_only:
            return

        self.vary[name]["with"].add(with_var)

    def remove_vary_with(self, name, with_var, force=False, check_only=False):
        """Add a variable to the vary with option."""
        # operand existence
        if name not in self.operands:
            raise IndexError("Unknown operand: %s" % name)

        self.update_vary(name)

        # value/type check
        if with_var != "rep":
            if isinstance(with_var, str):
                with_var = self.ranges_parse(with_var, dorange=False)
            if not self.sumrange or with_var != self.sumrange_var:
                raise ValueError("Invalid vary with entry: %s" % with_var)

        if check_only:
            return

        self.vary[name]["with"].discard(with_var)

    def set_vary_along(self, name, along, force=False, check_only=False):
        """Set the vary along option of a variable."""
        # operand existence
        if name not in self.operands:
            raise IndexError("Unknown operand: %s" % name)
        operand = self.get_operand(name)

        self.update_vary(name)

        # parse string
        if isinstance(along, str):
            along = eval(along)

        # type check
        if not isinstance(along, int):
            raise TypeError("Invalid vary along type: %s" % along)

        # value
        if not (0 <= along < len(operand["dims"])):
            if not force:
                raise IndexError("Invalid vary along value: %s" % along)
            along = max(0, min(along, len(operand["dims"]) - 1))

        if check_only:
            return

        self.vary[name]["along"] = along

    def set_vary_offset(self, name, offset, force=False, check_only=False):
        """Set the vary offset option of a variable."""
        # operand existence
        if name not in self.operands:
            raise IndexError("Unknown operand: %s" % name)
        operand = self.get_operand(name)

        self.update_vary(name)

        # parse string
        if isinstance(offset, str):
            offset = self.ranges_parse(offset)

        # type
        if not isinstance(offset, (int, symbolic.Expression)):
            raise TypeError("Invalid offset: %s" % offset)

        # check for symbols
        known_symbols = list(self.ranges_vardict())
        if not all(symbol in known_symbols
                   for symbol in symbolic.findsymbols(offset)):
            raise ValueError("offset contains unknown symbols: %s" % offset)

        if check_only:
            return

        # set new values
        self.vary[name]["offset"] = offset

    def set_vary(self, name, with_=None, along=None, offset=None, force=False,
                 check_only=False):
        """Set the vary specs of a variable."""
        # operand existence
        if name not in self.operands:
            raise IndexError("Unknown operand: %s" % name)

        self.update_vary()

        if with_ is not None:
            self.set_vary_with(name, with_, force=force, check_only=True)
        if along is not None:
            self.set_vary_along(name, along, force=force, check_only=True)
        if offset is not None:
            self.set_vary_offset(name, offset, force=force, check_only=True)

        if check_only:
            return

        # set new values
        if with_ is not None:
            self.set_vary_with(name, with_, force=force)
        if along is not None:
            self.set_vary_along(name, along, force=force)
        if offset is not None:
            self.set_vary_offset(name, offset, force=force)

    # inference
    def get_operand(self, name):
        """Get an operand information dict."""
        # get any call that contains name
        try:
            call, name_argid = next(
                (call, argid)
                for call in self.calls
                if isinstance(call, signature.Call)
                for argid in call.sig.dataargs()
                if call[argid] == name
            )
        except:
            raise KeyError("no operand argument named %r" % name)
        sig = call.sig

        dimcall = call.copy()
        ldcall = call.copy()
        sizecall = call.copy()
        for argid, arg in enumerate(sig):
            if isinstance(arg, signature.Data):
                dimcall[argid] = None
                ldcall[argid] = None
                sizecall[argid] = None
            elif isinstance(arg, (signature.Ld, signature.Inc)):
                dimcall[argid] = None
                ldcall[argid] = symbolic.Symbol("." + arg.name)
            elif isinstance(arg, (signature.Dim, signature.Lwork)):
                dimcall[argid] = symbolic.Symbol("." + arg.name)
                ldcall[argid] = symbolic.Symbol("." + arg.name)
        dimcall.complete()
        ldcall.complete()
        sizecall.complete()

        argdict = dict(("." + arg.name, val) for arg, val in zip(sig, call))

        operand = {
            "size": sizecall[name_argid],
            "type": type(sig[name_argid])
        }

        # dimensions
        dims = dimcall[name_argid]
        if isinstance(dims, symbolic.Prod):
            dims = dims[1:]
        else:
            dims = [dims]
        dims = [symbolic.simplify(dim, **argdict) for dim in dims]
        if isinstance(sig[name_argid], signature.Work):
            # Workspace is 1D
            dims = [symbolic.simplify(symbolic.Prod(*dims))]
        operand["dims"] = tuple(dims)

        # leading dimension
        lds = ldcall[name_argid]
        if isinstance(lds, symbolic.Prod):
            lds = lds[1:]
        else:
            lds = [lds]
        lds = [symbolic.simplify(ld, **argdict) for ld in lds]
        operand["lds"] = tuple(lds)

        return operand

    def update_vary(self, name=None):
        """Update the vary attributes."""
        if name is None:
            operands = self.operands
            for name in list(self.vary):
                if name not in operands:
                    del self.vary[name]
            for name in operands:
                self.update_vary(name)
            return

        vary = {
            "with": set(),
            "along": len(self.get_operand(name)["dims"]) - 1,
            "offset": 0
        }
        if name in self.vary:
            for key, value in self.vary[name].items():
                if key in vary:
                    vary[key] = value

        self.vary[name] = vary

    def infer_ld(self, callid, ldargid):
        """Infer one leading dimension."""
        self.update_vary()
        call = self.calls[callid]

        # check call type
        if not isinstance(call, signature.Call):
            raise TypeError(
                "can only infer leading dimension for Call (not %r)" %
                type(call)
            )
        sig = call.sig

        # parse string argument name
        if isinstance(ldargid, str):
            ldargid = call.argpos(name)

        # check argument type
        if not isinstance(sig[ldargid], signature.Ld):
            raise TypeError(
                "can only infer leading dimension for Ld (not %r)" %
                type(sig[ldargid])
            )

        ldname = sig[ldargid].name

        # operand dimensions in terms of lds
        ldcall = call.copy()
        for argid, arg in enumerate(sig):
            if isinstance(arg, signature.Data):
                ldcall[argid] = None
            elif isinstance(arg, (signature.Dim, signature.Ld, signature.Inc,
                                  signature.Lwork)):
                ldcall[argid] = symbolic.Symbol("." + arg.name)
        ldcall.complete()

        # search for ld in all operand args
        for dataargid in sig.dataargs():
            dims = ldcall[dataargid]
            if isinstance(dims, symbolic.Prod):
                dims = dims[1:]
            else:
                dims = [dims]
            dims = map(symbolic.simplify, dims)

            if "." + ldname in dims:
                break
        else:
            # ld not found
            return

        # extract stuff
        opname = call[dataargid]
        dimidx = dims.index("." + ldname)
        operand = self.get_operand(opname)
        vary = self.vary[opname]

        # initial: required by operand
        ld = operand["dims"][dimidx]

        # varying along this dimension
        if vary["along"] == dimidx:
            if self.sumrange and self.sumrange_var in vary["with"]:
                ld = symbolic.Sum(ld, **{str(self.sumrange_var):
                                         self.sumrange_vals})()
            if "rep" in vary["with"]:
                ld *= self.nreps

        call[ldargid] = symbolic.simplify(ld)

    def infer_lds(self, callid=None):
        """Infer all leading dimensions."""
        if callid is None:
            for callid, call in enumerate(self.calls):
                self.infer_lds(callid)
            return

        call = self.calls[callid]

        if not isinstance(call, signature.Call):
            return

        for argid, arg in enumerate(call.sig):
            if isinstance(arg, signature.Ld):
                self.infer_ld(callid, argid)

    def infer_lwork(self, callid, argid):
        """Infer one leading dimension."""
        self.update_vary()
        call = self.calls[callid]

        # check call type
        if not isinstance(call, signature.Call):
            raise TypeError(
                "can only infer work space size for Call (not %r)" %
                type(call)
            )
        sig = call.sig

        # parse string argument name
        if isinstance(argid, str):
            argid = call.argpos(name)

        # check argument type
        if not isinstance(call.sig[argid], signature.Lwork):
            raise TypeError(
                "can only infer work space size for Lwork (not %r)" %
                type(call.sig[argid])
            )

        # infer argument
        call[argid] = None
        call.complete()

    def infer_lworks(self, callid=None):
        """Infer all leading dimensions."""
        if callid is None:
            for callid, call in enumerate(self.calls):
                self.infer_lworks(callid)
            return

        call = self.calls[callid]

        if not isinstance(call, signature.Call):
            return

        for argid, arg in enumerate(call.sig):
            if isinstance(arg, signature.Lwork):
                self.infer_lwork(callid, argid)

    def apply_connections_from(self, callid, argid=None, connections=None):
        """Apply operand-connections from this call."""
        connections = connections or self.get_connections()
        call = self.calls[callid]
        argids = argid,
        if argid is None:
            # no argid specified: infer all args
            argids = range(len(call))
        for argid in argids:
            for con_callid, con_argid in connections[callid, argid]:
                self.calls[con_callid][con_argid] = call[argid]

    def apply_connections_to(self, callid, argid=None, connections=None):
        """Apply operand-connections from this call."""
        connections = connections or self.get_connections()
        call = self.calls[callid]
        argids = argid,
        if argid is None:
            # no argid specified: infer all args
            argids = range(len(call))
        for argid in argids:
            for con_callid, con_argid in connections[callid, argid]:
                call[argid] = self.calls[con_callid][con_argid]

    def check_sanity(self, raise_=False):
        """Check if the experiment is self-consistent."""
        if not raise_:
            # catch errors here and instead return False
            try:
                self.check_sanity(True)
                return True
            except:
                return False

        self.update_vary()

        self.set_sampler(self.sampler, check_only=True)
        self.set_papi_counters(self.papi_counters, check_only=True)
        self.set_nthreads(self.nthreads, check_only=True)
        self.set_range(self.range, check_only=True)
        self.set_nreps(self.nreps, check_only=True)
        self.set_sumrange(self.sumrange, check_only=True)
        self.set_sumrange_parallel(self.sumrange_parallel, check_only=True)
        self.set_calls_parallel(self.calls_parallel, check_only=True)
        self.set_calls(self.calls, check_only=True)

        # vary
        for name, vary in self.vary.items():
            self.set_vary_with(name, vary["with"], check_only=True)
            self.set_vary_along(name, vary["along"], check_only=True)
            self.set_vary_offset(name, vary["offset"], check_only=True)

    # job generation
    def generate_cmds(self, range_val=None):
        """Generate commands for the Sampler."""
        def varname(name, range_val, rep, sumrange_val):
            """Construct a variable name.

            Format: <name>[_<range_val>][_<rep>][_<sumrange_val>]
            """
            vary = self.vary[name]
            if not vary["with"]:
                return name
            parts = [name]
            if self.range and self.nthreads != self.range_var:
                parts.append(range_val)
            if "rep" in vary["with"]:
                parts.append(rep)
            if self.sumrange and self.sumrange_var in vary["with"]:
                parts.append(sumrange_val)
            return "_".join(map(str, parts))

        self.update_vary()

        cmds = []

        range_vals = range_val,
        if range_val is None:
            range_vals = tuple(self.range_vals)

        if len(self.papi_counters):
            cmds += [
                ["########################################"],
                ["# counters                             #"],
                ["########################################"],
                [],
                ["set_counters"] + self.papi_counters,
                [], []
            ]

        if len(self.operands):
            cmds += [
                ["########################################"],
                ["# operands                             #"],
                ["########################################"]
            ]

        # datatype prefixes for malloc and offset commands
        cmdprefixes = {
            signature.Data: "",
            signature.iData: "i",
            signature.sData: "s",
            signature.dData: "d",
            signature.cData: "c",
            signature.zData: "z",
            signature.Work: "",
            signature.iWork: "i",
            signature.sWork: "s",
            signature.dWork: "d",
            signature.cWork: "c",
            signature.zWork: "z",
        }

        # collect data sizes for randomization
        operand_range_sizes = {}

        # go over all operands
        for name in sorted(self.operands):
            # TODO: merge this whole thing into call generation
            operand = self.get_operand(name)
            vary = self.vary[name]
            cmdprefix = cmdprefixes[operand["type"]]

            # comment
            cmds += [[], ["#", name]]

            # init operand size collection
            operand_range_sizes[name] = {}

            if not vary["with"]:
                # argumnet doesn't vary
                size = max(self.ranges_eval(operand["size"], range_val))
                cmds.append([cmdprefix + "malloc", name, size])
                operand_range_sizes[name][range_val] = size
                continue
            # operand varies

            # set up some reused variables
            rep_vals = None,
            if "rep" in vary["with"]:
                rep_vals = range(self.nreps)

            # init result variables
            offsetcmds = []
            size_max = 0
            # go over range
            for range_val in range_vals:
                if range_val is not None:
                    # comment
                    offsetcmds.append(["#", self.range_var, "=", range_val])

                # prepare sumrange
                sumrange_vals = self.sumrange_vals_at(range_val)

                offset = 0

                # go over repetitions
                for rep in rep_vals:
                    # offset for repetitions
                    if "rep" not in vary["with"]:
                        offset = 0

                    if (not self.sumrange or
                            self.sumrange_var not in vary["with"]):
                        # operand doesn't vary in sumrange (1 offset)
                        offsetcmds.append([
                            cmdprefix + "offset", name, offset,
                            varname(name, range_val, rep, None)
                        ])
                    else:
                        # comment (multiple offsets)
                        offsetcmds.append(["#", "repetition", rep])

                    # offset for rep
                    offset_rep = offset
                    # go over sumrange
                    for sumrange_val in sumrange_vals:
                        if self.sumrange and self.sumrange_var in vary["with"]:
                            # operand varies in sumrange (offset)
                            offsetcmds.append([
                                cmdprefix + "offset", name, offset,
                                varname(name, range_val, rep, sumrange_val)
                            ])
                        else:
                            # offset is the same every iteration
                            offset = offset_rep
                        # compute current needed size
                        size = next(self.ranges_eval(
                            operand["size"], range_val, sumrange_val
                        ))
                        size_max = max(size_max, offset + size)
                        # compute next offset
                        dim = 1
                        for idx in range(vary["along"]):
                            # multiply leading dimensions for skipped dims
                            dim *= next(self.ranges_eval(
                                operand["lds"][idx], range_val, sumrange_val
                            ))
                        # dimension for traversed dim
                        if vary["along"] < len(operand["dims"]):
                            dim *= next(self.ranges_eval(
                                operand["dims"][vary["along"]], range_val,
                                sumrange_val
                            ))
                        # add custom offset
                        offset += dim + next(self.ranges_eval(
                            vary["offset"], range_val, sumrange_val
                        ))

                # operand size collection
                operand_range_sizes[name][range_val] = size_max

            # malloc with needed size before offsetting
            cmds.append([cmdprefix + "malloc", name,  size_max])
            cmds += offsetcmds

        if len(self.operands):
            cmds += [[], []]

        cmds += [
            ["########################################"],
            ["# calls                                #"],
            ["########################################"]
        ]

        # go over range
        for range_val in range_vals:
            if self.range and len(range_vals) > 1:
                # comment
                cmds += [[], ["#", str(self.range_var), "=", range_val]]

            # randomize operand
            if self.range_randomize_data:
                for name in sorted(self.operands):
                    cmdprefix = cmdprefixes[self.get_operand(name)["type"]]
                    size = operand_range_sizes[name][range_val]
                    cmds.append([cmdprefix + "gerand", size, 1, name, size])

            # set up sumrange values
            sumrange_vals = self.sumrange_vals_at(range_val)

            # go over repetitions
            for rep in range(self.nreps):
                if self.sumrange:
                    # comment
                    cmds += [[], ["#", "repetition",  rep]]

                if self.sumrange and self.sumrange_parallel:
                    # begin omp range
                    cmds.append(["{omp"])

                # go over sumrange
                for sumrange_val in sumrange_vals:
                    if self.calls_parallel and not self.sumrange_parallel:
                        # begin parallel calls
                        cmds.append(["{omp"])

                    # go over calls
                    for call in self.calls:
                        if isinstance(call, signature.Call):
                            # call with signature

                            # evaluate symbolic arguments
                            call = call.sig(*[
                                next(self.ranges_eval(val, range_val,
                                                      sumrange_val))
                                for val in call[1:]
                            ])
                            # format for the sampler
                            cmd = call.format_sampler()
                            # place operand variables
                            for argid in call.sig.dataargs():
                                cmd[argid] = varname(
                                    cmd[argid], range_val, rep, sumrange_val
                                )
                        else:  # BasicCall
                            # call without signature
                            cmd = call[:]
                            sig = call.sig

                            # go over arguments
                            for argid, value in enumerate(call):
                                if argid == 0 or sig[argid] == "char*":
                                    # chars don't need further processing
                                    continue
                                if isinstance(value, list):
                                    value = [next(self.ranges_eval(
                                        value[0], range_val, sumrange_val
                                    ))]
                                    # TODO: parse list argument
                                else:
                                    # parse scalar arguments
                                    value = next(self.ranges_eval(
                                        value, range_val, sumrange_val
                                    ))
                                cmd[argid] = value

                        # add created call
                        cmds.append(cmd)

                    if self.calls_parallel and not self.sumrange_parallel:
                        # begin parallel calls
                        cmds.append(["}"])

                if self.sumrange and self.sumrange_parallel:
                    # end omp range
                    cmds.append(["}"])

            # execute range iteration
            cmds.append(["go"])

        return cmds

    def submit_prepare(self, filebase):
        """Create all files needed to run the experiment."""
        self.check_sanity()
        scriptfile = "%s.%s" % (filebase, defines.script_extension)
        reportfile = "%s.%s" % (filebase, defines.report_extension)
        errfile = "%s.%s" % (filebase, defines.error_extension)

        # emptly output files
        if os.path.isfile(reportfile):
            os.remove(reportfile)
        if os.path.isfile(errfile):
            os.remove(errfile)

        nthreads_vals = self.nthreads,
        if self.range and self.range_var == self.nthreads:
            nthreads_vals = tuple(self.range_vals)

        script = ""

        # shorthands
        b_header = self.sampler["backend_header"]
        b_prefix = self.sampler["backend_prefix"]
        b_suffix = self.sampler["backend_suffix"]
        b_footer = self.sampler["backend_footer"]

        # backend header
        if b_header:
            script += "%s\n" % b_header.format(nt=max(nthreads_vals))

        # script header (from GUI)
        if self.script_header:
            script += "%s\n" % self.script_header.format(nt=max(nthreads_vals))

        # experiment as part of the
        selfrepr = repr(self)
        delim = "EXPERIMENT"
        if delim in selfrepr:
            i = 0
            while "%s%d" % (delim, i) in selfrepr:
                i += 1
            delim = "%s%d" % (delim, i)
        script += "cat > \"%s\" <<%s\n%s\n%s\n" % (
            reportfile, delim, selfrepr, delim
        )

        # timing
        script += "date +%%s >> \"%s\"\n" % reportfile

        # go over #threads range
        for nthreads in nthreads_vals:
            # filename for commands
            callfile = "%s.%s" % (filebase, defines.calls_extension)
            if len(nthreads_vals) > 1:
                callfile = "%s.%d.%s" % (filebase, nthreads,
                                         defines.calls_extension)

            # generate commands file
            if len(nthreads_vals) > 1:
                cmds = self.generate_cmds(nthreads)
            else:
                cmds = self.generate_cmds()
            with open(callfile, "w") as fout:
                for cmd in cmds:
                    print(*cmd, file=fout)

            # compute omp thread count
            ompthreads = 1
            if self.sumrange and self.sumrange_parallel:
                if self.range:
                    if len(nthreads_vals) > 1:
                        sumrangelen = len(self.sumrange_vals_at(nthreads))
                    else:
                        sumrangelen = max(
                            len(self.sumrange_vals_at(range_val))
                            for range_val in self.range_vals
                        )
                else:
                    sumrangelen = len(self.sumrange_vals)
                ompthreads = sumrangelen * len(self.calls)
            elif self.calls_parallel:
                ompthreads = len(self.calls)
            # limit threads to #cores * #hyperthreads/core
            while ompthreads * nthreads > self.sampler["nt_max"]:
                ompthreads = ompthreads - 1

            # sampler invocation
            if ompthreads != 1:
                script += "export OMP_NUM_THREADS=%d\n" % ompthreads
            if b_prefix:
                script += "%s " % b_prefix.format(nt=nthreads)
            script += "%(x)s < \"%(i)s\" >> \"%(o)s\" 2>> \"%(e)s\"" % {
                "x": self.sampler["exe"],  # executable
                "i": callfile,  # input
                "o": reportfile,  # output
                "e": errfile  # error
            }
            script += " || echo \"ERROR $?\" >> \"%s\"" % errfile
            if b_suffix:
                script += " %s" % b_suffix.format(nt=nthreads)
            script += "\n"

            # exit upon error
            script += "[ -s \"%s\" ] && exit\n" % errfile

            # delete call file
            script += "rm \"%s\"\n" % callfile

        # timing
        script += "date +%%s >> \"%s\"\n" % reportfile

        # delete script file
        script += "rm \"%s\"\n" % scriptfile

        # delete errfile (it's empty if we got so far)
        script += "rm \"%s\"" % errfile

        if b_footer:
            script += "\n" + b_footer.format(nt=self.nthreads)

        # write script file
        with open(scriptfile, "w") as fout:
            fout.write(script)

        return script

    def submit(self, filebase):
        """Submit the experiment to a backend."""
        script = self.submit_prepare(filebase)
        nthreads = self.nthreads
        if self.range and self.range_var == nthreads:
            nthreads = symbolic.max(self.range_vals)
        backend = self.sampler["backend"]
        jobname = os.path.basename(filebase)
        return(backend.submit(script, nt=nthreads, jobname=jobname))

    # primarily internal routines
    def ranges_vardict(self, dorange=True, dosumrange=True):
        """Create a dictionary for the symbolic range variables."""
        vardict = {}
        if self.range and dorange:
            vardict[str(self.range_var)] = self.range_var
        if self.sumrange and dosumrange:
            vardict[str(self.sumrange_var)] = self.sumrange_var
        return vardict

    def ranges_valdict(self, range_val=None, sumrange_val=None):
        """Create a dictionary for the range substitution."""
        valdict = {}
        if self.range and range_val is not None:
            valdict[str(self.range_var)] = range_val
        if self.sumrange and sumrange_val is not None:
            valdict[str(self.sumrange_var)] = sumrange_val
        return valdict

    def sumrange_vals_at(self, range_val):
        """Evaluate the sumrange at a range value."""
        if self.range:
            return symbolic.simplify(self.sumrange_vals,
                                     **self.ranges_valdict(range_val))
        return self.sumrange_vals

    def ranges_parse(self, expr, dorange=True, dosumrange=True):
        """Parse (eval) a string or Call with symbolic range variables."""
        if isinstance(expr, signature.Call):
            args = []
            for arg, val in zip(expr.sig[1:], expr[1:]):
                if isinstance(arg, (signature.Dim, signature.Ld,
                                    signature.Scalar)):
                    val = self.ranges_parse(val, dorange, dosumrange)
                args.append(val)
            return expr.sig(*args)
        if isinstance(expr, str):
            return eval(expr, self.ranges_vardict(dorange, dosumrange),
                        symbolic.__dict__)
        return expr

    def ranges_eval(self, expr, range_val=None, sumrange_val=None):
        """Evaluate an symbolic expression for the ranges."""
        range_val_fixed = range_val
        sumrange_val_fixed = sumrange_val

        # range values
        range_vals = range_val_fixed,
        if range_val_fixed is None:
            range_vals = tuple(self.range_vals)

        # go over the range
        for range_val in range_vals:

            # sumrange values
            sumrange_vals = sumrange_val_fixed,
            if sumrange_val_fixed is None:
                sumrange_vals = self.sumrange_vals_at(range_val)

            # go over sumrange
            for sumrange_val in sumrange_vals:
                yield symbolic.simplify(
                    expr, **self.ranges_valdict(range_val, sumrange_val)
                )

    def ranges_eval_minmax(self, expr, range_val=None, sumrange_val=None):
        """Get the minimum for an symbolic expression for the ranges."""
        range_val_fixed = range_val
        sumrange_val_fixed = sumrange_val

        # range values
        range_vals = range_val_fixed,
        if range_val_fixed is None and self.range:
            range_vals = self.range_vals
            if not range_vals:
                range_vals = None,
            else:
                range_vals = (symbolic.min(range_vals),
                              symbolic.max(range_vals))

        values = []

        # go over the range
        for range_val in range_vals:

            # sumrange values
            sumrange_vals = sumrange_val_fixed,
            if sumrange_val_fixed is None and self.sumrange:
                sumrange_vals = self.sumrange_vals_at(range_val)
                if not sumrange_vals:
                    sumrange_vals = None,
                else:
                    sumrange_vals = (symbolic.min(sumrange_vals),
                                     symbolic.max(sumrange_vals))

            # go over sumrange
            for sumrange_val in sumrange_vals:
                values.append(symbolic.simplify(
                    expr, **self.ranges_valdict(range_val, sumrange_val)
                ))
        return min(values), max(values)

    def substitute(self, **kwargs):
        """Substitute symbols everywhere."""
        if self.range:
            self.range_vals = symbolic.simplify(self.range_vals, **kwargs)
        if self.nthreads in kwargs:
            self.nthreads = kwargs[self.nthreads]
            if self.sampler:
                self.nthreads = min(self.sampler["nt_max"], self.nthreads)
        if self.sumrange:
            self.sumrange_vals = symbolic.simplify(self.sumrange_vals,
                                                   **kwargs)
        for call in self.calls:
            for argid, value in enumerate(call):
                call[argid] = symbolic.simplify(value, **kwargs)
        self.update_vary()
        for vary in self.vary.values():
            vary["offset"] = symbolic.simplify(vary["offset"], **kwargs)
            for key, val in kwargs.items():
                if key in vary["with"]:
                    vary["with"].add(str(val))
                    vary["with"].discard(key)

    def operands_maxdim(self):
        """Get maximum size along any operand dimension."""
        maxdim = 0
        for name in self.operands:
            operand = self.get_operand(name)
            if not operand["dims"]:
                return None
            if issubclass(operand["type"], signature.Work):
                continue
            for dim in operand["dims"]:
                max_ = self.ranges_eval_minmax(dim)[1]
                if not isinstance(max_, Number):
                    return None
                maxdim = max(maxdim, max_)
        return maxdim

    def get_connections(self):
        """Update connections between arguments based on coinciding operand."""
        sizes = defaultdict(list)
        for callid, call in enumerate(self.calls):
            if not isinstance(call, signature.Call):
                continue
            symcall = call.copy()
            for argid, arg in enumerate(call.sig):
                if isinstance(arg, (signature.Dim, signature.Lwork)):
                    symcall[argid] = symbolic.Symbol((callid, argid))
                elif isinstance(arg, (signature.Data, signature.Ld)):
                    symcall[argid] = None
            symcall.complete()
            for argid in call.sig.dataargs():
                name = call[argid]
                opsize = symcall[argid]
                if isinstance(opsize, symbolic.Symbol):
                    opsize = [opsize]
                elif isinstance(opsize, symbolic.Prod):
                    opsize = opsize[1:]
                elif isinstance(opsize, symbolic.Operation):
                    # try simplifying
                    opsize = opsize()
                    if isinstance(opsize, symbolic.Symbol):
                        opsize = [opsize]
                    elif isinstance(opsize, symbolic.Prod):
                        opsize = opsize[1:]
                    else:
                        continue
                else:
                    continue
                opsize = [
                    size.name if isinstance(size, symbolic.Symbol) else None
                    for size in opsize
                ]
                sizes[name].append(opsize)
        # initial connections
        connections = dict(
            ((callid, argid), set([(callid, argid)]))
            for callid, call in enumerate(self.calls)
            for argid in range(len(call))
        )
        connections[None] = set()
        # combine connections for each operand item
        for opsize in sizes.values():
            for idlist in zip(*opsize):
                connected = set().union(*(connections[id_] for id_ in idlist))
                for id_ in connected:
                    connections[id_] = connected
        del connections[None]
        return {key: sorted(val) for key, val in connections.items()}

    def nresults(self):
        """How many results the current experiment woudl produce."""
        assert(self.check_sanity())
        nresults = 0
        for range_val in self.range_vals:
            if self.range_randomize_data:
                nresults += len(self.operands)
            for rep in range(self.nreps):
                if self.sumrange and self.sumrange_parallel:
                    nresults += 1
                else:
                    for sumrange_val in self.sumrange_vals_at(range_val):
                        if self.calls_parallel:
                            nresults += 1
                        else:
                            nresults += len(self.calls)
        return nresults
