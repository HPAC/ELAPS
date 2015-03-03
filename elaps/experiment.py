#!/usr/bin/env python
"""Central Experiment concept."""
from __future__ import division, print_function

import symbolic
import signature

from collections import Iterable, defaultdict
from itertools import chain
import warnings
import os
from copy import deepcopy


class Experiment(dict):

    """Representation of one experiment."""

    def __init__(self, other={}, **kwargs):
        """Initialize experiment from (optional) other expeirment."""
        dict.__init__(self)

        # empty experiment
        self.update({
            "note": "",
            "sampler": None,
            "nthreads": 1,
            "script_header": "",
            "range": None,
            "nreps": 1,
            "sumrange": None,
            "sumrange_parallel": False,
            "calls_parallel": False,
            "calls": [],
            "data": {},
            "papi_counters": []
        })

        # initialize from argument
        for key, value in chain(other.iteritems(), kwargs.items()):
            if key in self:
                self.__setattr__(key, value)
            else:
                warnings.warn("%s doesn't support the key %r" %
                              (type(self).__name__, key), Warning)

    def __getattr__(self, name):
        """Element access through attributes."""
        if name in self:
            return self[name]
        if name == "call" and len(self.calls) == 1:
            return self.calls[0]
        raise AttributeError("%r object has no attribute %r" %
                             (type(self), name))

    def __setattr__(self, name, value):
        """Element access through attributes."""
        if name in self:
            self[name] = value
        if name == "call":
            self.calls = [value]
        dict.__setattr__(self, name, value)

    def __repr__(self):
        """Python parsable representation."""
        empty = Experiment()

        # Only print non-default attribute values
        changed = {key: value for key, value in self.items()
                   if value != empty[key]}

        # remove unused sampler kernels
        if "sampler" in changed:
            changed["sampler"] = self.sampler.copy()
            del changed["sampler"]["kernels"]
        args = ["%s=%r" % keyval for keyval in changed.items()]
        return type(self).__name__ + "(" + ", ".join(args) + ")"

    def __str__(self):
        """Readable string representation."""
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
            result += "For %s = %s :\n" % self.range
            indent += "    "
        if not isinstance(self.nthreads, int):
            result += indent + "#threads = %s\n" % self.nthreads
        result += indent + "repeat %s times :\n" % self.nreps
        indent += "    "
        if self.sumrange:
            result += indent + "sum over %s = %s" % self.sumrange
            if self.sumrange_parallel:
                result += " in parallel"
            result += " :\n"
            indent += "    "
        if self.calls_parallel:
            result += indent + "in parallel :\n"
            indent += "    "
        for call in self.calls:
            result += indent + str(call)
        return result

    def update_data(self, name=None):
        """Update the data from the calls."""
        if name is None:
            names = set([
                call[argid]
                for call in self.calls
                if isinstance(call, signature.Call)
                for argid in call.sig.dataargs()
                if isinstance(call[argid], str)
            ])
            for name in set(self.data) - names:
                del self.data[name]
            for name in names:
                self.update_data(name)
            return

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
            raise KeyError("no Data argument named %r" % name)
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

        argdict = {"." + arg.name: val for arg, val in zip(sig, call)}

        data = {
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
            dims = [symbolic.Prod(*dims)()]
        data["dims"] = dims

        # leading dimension
        lds = ldcall[name_argid]
        if isinstance(lds, symbolic.Prod):
            lds = lds[1:]
        else:
            lds = [lds]
        lds = [symbolic.simplify(ld, **argdict) for ld in lds]
        data["lds"] = lds

        # vary
        if name in self.data:
            vary = self.data[name]["vary"]
        else:
            vary = {
                "with": set(),
                "along": len(dims) - 1,
                "offset": 0
            }
        data["vary"] = vary

        self.data[name] = data

    def infer_ld(self, callid, ldargid):
        """Infer one leading dimension."""
        self.update_data()

        call = self.calls[callid]

        if not isinstance(call, signature.Call):
            raise TypeError(
                "can only infer leading dimension for Call (not %r)" %
                type(call)
            )

        sig = call.sig

        if not isinstance(sig[ldargid], signature.Ld):
            raise TypeError(
                "can only infer leading dimension for Ld (not %r)" %
                type(sig[ldargid])
            )

        ldname = sig[ldargid].name

        # data dimensions in terms of lds
        ldcall = call.copy()
        for argid, arg in enumerate(sig):
            if isinstance(arg, signature.Data):
                ldcall[argid] = None
            elif isinstance(arg, (signature.Dim, signature.Ld, signature.Inc,
                                  signature.Lwork)):
                ldcall[argid] = symbolic.Symbol("." + arg.name)
        ldcall.complete()

        # search for ld in all data args
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
        dataname = call[dataargid]
        dimidx = dims.index("." + ldname)
        data = self.data[dataname]
        vary = data["vary"]

        # initial: required by data
        ld = data["dims"][dimidx]

        # varying along this dimension
        if vary["along"] == dimidx:
            if self.sumrange and self.sumrange[0] in vary["with"]:
                ld = symbolic.Sum(ld, **dict((self.sumrange,)))()
            if "rep" in vary["with"]:
                ld *= self.nreps

        call[ldargid] = symbolic.simplify(ld)

        self.update_data()

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
        call = self.calls[callid]

        if not isinstance(call, signature.Call):
            raise TypeError(
                "can only infer work space size for Call (not %r)" %
                type(call)
            )

        if not isinstance(call.sig[argid], signature.Lwork):
            raise TypeError(
                "can only infer work space size for Lwork (not %r)" %
                type(sig[argid])
            )

        call[argid] = None
        call.complete()

        self.update_data()

    def infer_lworks(self, callid=None):
        """Infer all leading dimensions."""
        if callid is None:
            for callid, call in enumerate(self.calls):
                self.infer_lworks(callid)
            return

        call = self.calls[callid]

        if not isinstance(call, signature.Call):
            return

        for argid, arg in call.sig:
            if isinstance(arg, signature.Lwork):
                self.infer_lwork(callid, argid)

    def apply_connections(self, callid, argid):
        """Apply data-connections from this starging point."""
        value = self.calls[callid][argid]
        for callid2, argid2 in self.get_connections()[callid, argid]:
            self.calls[callid2][argid2] = value

    def vary_set(self, name, with_=None, along=None, offset=0):
        """Set the vary specs of a variable."""
        data = self.data[name]
        if with_ is None:
            with_ = set()
        if along is None:
            along = len(data["dims"]) - 1
        if isinstance(offset, str):
            offset = self.ranges_parse(offset)
            data["vary"] = {"with": with_, "along": along, "offset": offset}

    def check_sanity(self, raise_=False):
        """Check if the experiment is self-consistent."""
        if not raise_:
            try:
                self.check_sanity(True)
                return True
            except:
                return False

        # instance checking
        for key, types in (
            ("note", str),
            ("sampler", dict),
            ("nthreads", (int, str)),
            ("script_header", str),
            ("range", (type(None), tuple)),
            ("nreps", int),
            ("sumrange", (type(None), tuple)),
            ("sumrange_parallel", bool),
            ("calls_parallel", bool),
            ("calls", list),
            ("data", dict),
            ("papi_counters", list)
        ):
            if not isinstance(self[key], types):
                raise TypeError("Attribute %r should be of type %s" %
                                (key, types))

        # sampler
        for key in ("backend_header", "backend_prefix", "backend_suffix",
                    "backend_footer", "kernels", "nt_max", "exe"):
            if key not in self.sampler:
                raise KeyError("Sampler has not key %r" % key)

        # ranges
        if self.range:
            if len(self.range) != 2:
                raise TypeError("range must have length 2: str, iterator")
            if not isinstance(self.range[0], str):
                raise TypeError("range[0] must be int (not %s)" %
                                type(self.range[0]))
            if not isinstance(self.range[1], Iterable):
                raise TypeError("range[1] must be iterable")
        if self.sumrange:
            if len(self.sumrange) != 2:
                raise TypeError("sumrange must have length 2: str, iterator")
            if not isinstance(self.sumrange[0], str):
                raise TypeError("sumrange[0] must be int (not %s)" %
                                type(self.sumrange[0]))
            if not isinstance(self.sumrange[1], Iterable):
                raise TypeError("sumrange[1] must be iterable")
            dependson = symbolic.findsymbols(self.sumrange[1])
            if self.range:
                dependson.discard(symbolic.Symbol(self.range[0]))
            if dependson:
                raise ValueError("unknown symbol %r in sumrange" %
                                 dependson.pop())
        if self.range and self.sumrange:
            if self.sumrange[0] == self.range[0]:
                raise ValueError("range and sumrange use the same symbol")

        # threads
        if isinstance(self.nthreads, int):
            if self.nthreads > self.sampler["nt_max"]:
                raise ValueError("nthreads must be <= sampler[\"nt_max\"]")
        else:
            if not self.range or self.nthreads != self.range[0]:
                raise ValueError("nthreads int or range[0]")

        # calls
        symbols = set()
        if self.range:
            symbols.add(symbolic.Symbol(self.range[0]))
        if self.sumrange:
            symbols.add(symbolic.Symbol(self.sumrange[0]))
        if len(self.calls) == 0:
            raise ValueError("calls are empty")
        for callid, call in enumerate(self.calls):
            if not isinstance(call, signature.BasicCall):
                raise ValueError("call[%d] must be Call or BasicCall" % callid)
            if call[0] != str(call.sig[0]):
                raise ValueError("call[%d] is for %s but has signature for %s"
                                 % (callid, call[0], call.sig[0]))
            if len(call) != len(call.sig):
                raise ValueError("%s takes %d arguments but call[%d] has %d" %
                                 (call.sig[0], len(call.sig) - 1, callid,
                                  len(call) - 1))

            # Nones
            if any(arg is None for arg in call):
                raise ValueError("call[%d] contains None")

            # symbols
            for argid, arg in enumerate(call):
                excess = symbolic.findsymbols(arg) - symbols
                if excess:
                    raise ValueError("unknown symbol %r in call[%d][%d]" %
                                     (excess.pop(), callid, argid))

        # data
        needed = set(call[argid] for call in self.calls
                     if isinstance(call, signature.Call)
                     for argid in call.sig.dataargs())
        excess = needed - set(self.data)
        if excess:
            raise KeyError("%r not in data" % excess.pop())
        withoptions = set(["rep"])
        if self.range:
            withoptions.add(self.range[0])
        if self.sumrange:
            withoptions.add(self.sumrange[0])
        databackup = deepcopy(self.data)
        self.update_data()
        if self.data != databackup:
            raise Exception("Data is not up to date")

        # vary
        for name, data in self.data.items():
            self.data = databackup
            excess = data["vary"]["with"] - withoptions
            if excess:
                raise ValueError("data[%s] varies with unknown %s" %
                                 (name, excess.pop()))
            if data["vary"]["along"] >= len(data["dims"]):
                raise IndexError("data[%s] has %d dims but varies with dim %d"
                                 % (name, len(data["dims"]),
                                    data["vary"]["along"]))
            excess = symbolic.findsymbols(data["vary"]["offset"]) - symbols
            if excess:
                raise ValueError("unknown symbol %r in offset for data[%s]" %
                                 (excess.pop(), name))

        return True

    def generate_cmds(self, range_val=None):
        """Generate commands for the Sampler."""
        def varname(name, range_val, rep, sumrange_val):
            """Construct a variable name.

            Format: <name>[_<range_val>][_<rep>][_<sumrange_val>]
            """
            vary = self.data[name]["vary"]
            if not vary["with"]:
                return name
            parts = [name]
            if self.range and self.nthreads != self.range[0]:
                parts.append(range_val)
            if "rep" in vary["with"]:
                parts.append(rep)
            if self.sumrange and self.sumrange[0] in vary["with"]:
                parts.append(sumrange_val)
            return "_".join(map(str, parts))

        self.update_data()

        cmds = []

        range_vals = range_val,
        if range_val is None:
            range_vals = self.range_vals()

        if len(self.papi_counters):
            cmds += [
                ["########################################"],
                ["# counters                             #"],
                ["########################################"],
                [],
                ["set_counters"] + self.papi_counters,
                [], []
            ]

        if len(self.data):
            cmds += [
                ["########################################"],
                ["# data                                 #"],
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
            }

        # go over all operands
        for name in sorted(self.data):
            # TODO: merge this whole thing into call generation
            data = self.data[name]
            cmdprefix = cmdprefixes[data["type"]]

            # comment
            cmds += [[], ["#", name]]

            vary = data["vary"]
            if not vary["with"]:
                # argumnet doesn't vary
                size = max(self.ranges_eval(data["size"], range_val))
                cmds.append([cmdprefix + "malloc", name, size])
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
                    offsetcmds.append(["#", self.range[1], "=", range_val])

                # prepare sumrange
                sumrange_vals = self.sumrange_vals(range_val)

                offset = 0

                # go over repetitions
                for rep in rep_vals:
                    # offset for repetitions
                    if "rep" not in vary["with"]:
                        offset = 0

                    if (not self.sumrange or
                            self.sumrange[0] not in vary["with"]):
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
                        if self.sumrange and self.sumrange[0] in vary["with"]:
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
                            data["size"], range_val, sumrange_val
                        ))
                        size_max = max(size_max, offset + size)
                        # compute next offset
                        dim = 1
                        for idx in range(vary["along"]):
                            # multiply leading dimensions for skipped dims
                            dim *= next(self.ranges_eval(
                                data["lds"][idx], range_val, sumrange_val
                            ))
                        # dimension for traversed dim
                        if vary["along"] < len(data["dims"]):
                            dim *= next(self.ranges_eval(
                                data["dims"][vary["along"]], range_val,
                                sumrange_val
                            ))
                        # add custom offset
                        offset += dim + next(self.ranges_eval(
                            vary["offset"], range_val, sumrange_val
                        ))

            # malloc with needed size before offsetting
            cmds.append([cmdprefix + "malloc", name,  size_max])
            cmds += offsetcmds

        if len(self.data):
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
                cmds += [[], ["#", self.range[0], "=", range_val]]

            # set up sumrange values
            sumrange_vals = self.sumrange_vals(range_val)

            # go over repetitions
            for rep in range(self.nreps):
                if self.sumrange:
                    # comment
                    cmds += [[], ["#", "repetition",  rep]]

                if self.sumrange_parallel:
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
                                if argid == 0 or sig[argid] == "char *":
                                    # chars don't need further processing
                                    continue
                                if isinstance(value, str):
                                    if value[0] == "[" and value[-1] == "]":
                                        # parse string as array argument [ ]
                                        expr = self.ranges_parse(value[1:-1])
                                        if expr is not None:
                                            value = next(self.ranges_eval(
                                                expr, range_val, sumrange_val
                                            ))
                                            value = "[%s]" % str(value)
                                        # TODO: parse list argument
                                    else:
                                        # parse scalar arguments
                                        expr = self.ranges_parse(value)
                                        if expr is not None:
                                            value = next(self.ranges_eval(
                                                expr, range_val, sumrange_val
                                            ))
                                    cmd[argid] = value

                        # add created call
                        cmds.append(cmd)

                    if self.calls_parallel and not self.sumrange_parallel:
                        # begin parallel calls
                        cmds.append(["}"])

                if self.sumrange_parallel:
                    # end omp range
                    cmds.append(["}"])

            # execute range iteration
            cmds.append(["go"])

        return cmds

    def submit_prepare(self, filebase):
        """Create all files needed to run the experiment."""
        self.update_data()
        assert(self.check_sanity())
        scriptfile = filebase + ".sh"
        reportfile = filebase + ".eer"
        errfile = filebase + ".err"

        # emptly output files
        if os.path.isfile(reportfile):
            os.remove(reportfile)
        if os.path.isfile(errfile):
            os.remove(errfile)

        nthreads_vals = self.nthreads,
        if self.range and self.range[0] == self.nthreads:
            nthreads_vals = tuple(self.range[1])

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
        script += "cat > %s <<%s\n%s\n%s\n" % (
            reportfile, delim, selfrepr, delim
        )

        # timing
        script += "date +%%s >> %s\n" % reportfile

        # go over #threads range
        for nthreads in nthreads_vals:
            # filename for commands
            callfile = "%s.calls" % filebase
            if len(nthreads_vals) > 1:
                callfile = "%s.%d.calls" % (filebase, nthreads)

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
                        sumrangelen = len(simplify(self.sumrange,
                                                   **dict(self.range)))
                    else:
                        sumrangelen = max(
                            len(simplify(self.sumrange,
                                         **{self.range[0]: range_val}))
                            for range_val in self.range[1]
                        )
                else:
                    sumrangelen = len(self.sumrange[1])
                ompthreads = sumrangelen * len(self.calls)
            elif self.calls_parallel:
                ompthreads = len(self.calls)
            # limit threads to #cores * #hyperthreads/core
            ompthreads = min(ompthreads, self.sampler["nt_max"])

            # sampler invocation
            if b_prefix:
                script += "%s " % b_prefix.format(nt=nthreads)
            if ompthreads != 1:
                script += "OMP_NUM_THREADS=%d " % ompthreads
            script += "%(x)s < %(i)s >> %(o)s 2>> %(e)s" % {
                "x": self.sampler["exe"],  # executable
                "i": callfile,  # input
                "o": reportfile,  # output
                "e": errfile  # error
            }
            script += " || echo \"ERROR $?\" >> %s" % errfile
            if b_suffix:
                script += " %s" % b_suffix.format(nt=nthreads)
            script += "\n"

            # exit upon error
            script += "[ -s %s ] && exit\n" % errfile

            # delete call file
            script += "rm %s\n" % callfile

        # timing
        script += "date +%%s >> %s\n" % reportfile

        # delete script file
        script += "rm %s\n" % scriptfile

        # delete errfile (it's empty if we got so far)
        script += "rm %s" % errfile

        if b_footer:
            script += "\n" + footer.format(nt=self.nt)

        # write script file
        with open(scriptfile, "w") as fout:
            fout.write(script)

        return script

    def submit(self, filebase, backend):
        """Submit the experiment to a backend."""
        script = self.submit_prepare(filebase)
        nthreads = self.nthreads
        if self.range and self.range[0] == nthreads:
            nthreads = range.max()
        return(backend.submit(script, nt=nthreads, jobname=filebase))

    # primarily internal routines
    def range_vals(self):
        """Get the range values if set, else None."""
        if self.range:
            return tuple(self.range[1])
        return None,

    def sumrange_vals(self, range_val=None):
        """Get the range values if set, else None."""
        if self.sumrange:
            if self.range:
                return tuple(symbolic.simplify(self.sumrange[1],
                                               **{self.range[0]: range_val}))
            return tuple(self.sumrange[1])
        return None,

    def ranges_valdict(self, range_val=None, sumrange_val=None):
        """Create a dictionary for the range substitution."""
        valdict = {}
        if self.range and range_val is not None:
            valdict[self.range[0]] = range_val
        if self.sumrange and sumrange_val is not None:
            valdict[self.sumrange[0]] = sumrange_val
        return valdict

    def ranges_eval(self, expr, range_val=None, sumrange_val=None):
        """Evaluate an symbolic expression for the ranges."""
        range_val_fixed = range_val
        sumrange_val_fixed = sumrange_val

        # range values
        range_vals = range_val_fixed,
        if range_val_fixed is None:
            range_vals = self.range_vals()

        # go over the range
        for range_val in range_vals:

            # sumrange values
            sumrange_vals = sumrange_val_fixed,
            if sumrange_val_fixed is None:
                sumrange_vals = self.sumrange_vals(range_val)

            # go over sumrange
            for sumrange_val in sumrange_vals:
                yield symbolic.simplify(
                    expr, **self.ranges_valdict(range_val, sumrange_val)
                )

    def ranges_parse(self, expr):
        """Parse (eval) a string or Call with symbolic range variables."""
        if isinstance(expr, signature.Call):
            args = []
            for arg, val in zip(expr.sig[1:], expr[1:]):
                if isinstance(arg, (signature.Dim, signature.Ld,
                                    signature.Scalar)):
                    val = self.ranges_parse(val)
                args.append(val)
            return expr.sig(*args)
        if isinstance(expr, str):
            symdict = {}
            if self.range:
                symdict[self.range[0]] = symbolic.Symbol(self.range[0])
            if self.sumrange:
                symdict[self.sumrange[0]] = symbolic.Symbol(self.sumrange[0])
            return eval(expr, symdict, symbolic.env)
        return expr

    def get_connections(self):
        """Update the connections between arguments based on coincidng data."""
        sizes = defaultdict(list)
        for callid, call in enumerate(self.calls):
            if not isinstance(call, signature.Call):
                continue
            symcall = call.copy()
            for argid, arg in enumerate(call.sig):
                if isinstance(arg, (signature.Dim, signature.Lwork)):
                    symcall[argid] = symbolic.Symbol((callid, argid))
                elif isinstance(arg, signature.Data):
                    symcall[argid] = None
            symcall.complete()
            for argid in call.sig.dataargs():
                name = call[argid]
                datasize = symcall[argid]
                # TODO: pull out?
                if isinstance(datasize, symbolic.Symbol):
                    datasize = [datasize]
                elif isinstance(datasize, symbolic.Prod):
                    datasize = datasize[1:]
                elif isinstance(datasize, symbolic.Operation):
                    # try simplifying
                    datasize = datasize()
                    if isinstance(datasize, symbolic.Symbol):
                        datasize = [datasize]
                    elif isinstance(datasize, symbolic.Prod):
                        datasize = datasize[1:]
                    else:
                        raise Exception
                else:
                    continue
                datasize = [
                    size.name if isinstance(size, symbolic.Symbol) else None
                    for size in datasize
                ]
                sizes[name].append(datasize)
        # initial connections
        connections = {
            (callid, argid): set([(callid, argid)])
            for callid, call in enumerate(self.calls)
            for argid in range(len(call))
        }
        connections[None] = set()
        # combine connections for each data item
        for datasize in sizes.values():
            for idlist in zip(*datasize):
                connected = set().union(*(connections[id_] for id_ in idlist))
                for id_ in connected:
                    connections[id_] = connected
        return connections
