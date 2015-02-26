#!/usr/bin/env python
"""API independent base for ELAPS:Mat."""
from __future__ import division, print_function

import signature
import symbolic

import sys
import os
import imp
import time
import pprint
from collections import defaultdict


class Mat(object):

    """Base class for ELAPS:Mat."""

    requiredbuildversion = 1423087329
    requiredstateversion = 1424262159
    datascale = 100
    defaultdim = 1000
    state = {}

    def __init__(self, loadstate=True):
        """Initialize the Mat."""
        # set some absolute paths
        thispath = os.path.dirname(__file__)
        if thispath not in sys.path:
            sys.path.append(thispath)
        self.rootpath = os.path.abspath(os.path.join(thispath, "..", ".."))
        self.reportpath = os.path.join(self.rootpath, "reports")
        self.setuppath = os.path.join(self.rootpath, "setups")

        # initialize components
        self.backends_init()
        self.samplers_init()
        self.signatures_init()
        self.ranges_init()
        self.docs_init()
        self.UI_init()
        self.jobprogress_init()

        self.state_init(loadstate)
        if len(sys.argv) > 1:
            if sys.argv[1][-4:] in (".ems", ".emr"):
                self.state_load(sys.argv[1])

    # state access attributes
    def __getattr__(self, name):
        """Catch attribute accesses to state variables and sampler."""
        # get state items
        if name in self.__dict__["state"]:
            return self.__dict__["state"][name]
        # get sampler
        if name == "sampler":
            return self.samplers[self.samplername]
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))

    def __setattr__(self, name, value):
        """Catch attribute accesses to state variables."""
        # set state items
        if name in self.state:
            self.state[name] = value
        else:
            super(Mat, self).__setattr__(name, value)

    def start(self):
        """Start the Mat (enter the main loop)."""
        self.UI_start()

    # utility
    @staticmethod
    def log(*args):
        """Log a message to stdout."""
        print(*args)

    @staticmethod
    def alert(*args):
        """Log a message to stderr."""
        print("\033[31m" + " ".join(map(str, args)) + "\033[0m",
              file=sys.stderr)

    # initializers
    def backends_init(self):
        """Initialize the backends."""
        self.backends = {}
        backendpath = os.path.join(self.rootpath, "GUI", "src", "backends")
        for filename in os.listdir(backendpath):
            if not filename[-3:] == ".py":
                continue
            name = filename[:-3]
            module = imp.load_source(name, os.path.join(backendpath, filename))
            if hasattr(module, name):
                self.backends[name] = getattr(module, name)()
        self.log("Loaded", len(self.backends), "backends:",
                 *sorted(self.backends))
        if len(self.backends) == 0:
            raise Exception("No backends found")

    def samplers_init(self):
        """Load the available sampler infos."""
        self.samplers = {}
        samplerpath = os.path.join(self.rootpath, "Sampler", "build")
        for path, _, files in os.walk(samplerpath, followlinks=True):
            if "info.py" in files and "sampler.x" in files:
                with open(os.path.join(path, "info.py")) as fin:
                    sampler = eval(fin.read())
                if sampler["buildtime"] < self.requiredbuildversion:
                    self.alert("ERROR: Backend %r is outdated. Please rebuild!"
                               % sampler["name"])
                    continue
                if sampler["backend"] not in self.backends:
                    self.alert("ERROR: Missing backend %r for sampler %r."
                               % (sampler["backend"], sampler["name"]))
                    continue
                sampler["sampler"] = os.path.join(path, "sampler.x")
                sampler["kernels"] = {kernel[0]: tuple(map(intern, kernel))
                                      for kernel in sampler["kernels"]}
                self.samplers[sampler["name"]] = sampler
        self.log("Loaded", len(self.samplers), "Samplers:",
                 *sorted("%s (%d kernels)" % (name, len(sampler["kernels"]))
                         for name, sampler in self.samplers.iteritems()))
        if len(self.samplers) == 0:
            raise Exception("No samplers found")

    def signatures_init(self):
        """Load all available signatures."""
        self.signaturepath = os.path.join(self.rootpath, "GUI", "signatures")
        self.signatures = {}
        self.nosigwarning_shown = False

    def state_init(self):
        """Initialize the Mat state."""
        self.state_reset()

    def ranges_init(self):
        """Initialize some static range info."""
        self.rangetypes = {
            "outer": ("threads", "range"),
            "inner": ("sum", "omp")
        }

    def docs_init(self):
        """Set up the documentation loader."""
        self.docspath = os.path.join(self.rootpath, "GUI", "kerneldocs")
        self.docs = {}

    def jobprogress_init(self):
        """Initialize the jobprogress overview."""
        self.jobprogress = {}

    # state routines
    def state_toflat(self):
        """Removing signatures and turning list to tuples."""
        state = self.state.copy()
        state["calls"] = map(tuple, self.calls)
        state["stateversion"] = self.requiredstateversion
        return state

    def state_fromflat(self, state):
        """Set the state from a possibly flattened representation."""
        state = state.copy()
        calls = state["calls"]
        # apply signatures
        for callid, call in enumerate(calls):
            sig = self.signature_get(call[0])
            if sig:
                try:
                    calls[callid] = sig(*call[1:])
                except:
                    calls[callid] = list(call)
                    self.UI_alert(
                        ("Can't apply signature '%s' to '%s(%s)'.\n"
                         "Signature ignored.") % (sig, call[0], call[1:])
                    )
        state["calls"] = calls
        # check if sampler is available
        samplername = state["samplername"]
        if samplername not in self.samplers:
            samplername = min(self.samplers)
            if state["samplername"] is not None:
                self.alert(
                    "ERROR: Sampler %r is not available, using %r instead."
                    % (state["samplername"], samplername)
                )
        self.state = state
        self.sampler_set(samplername, True)

    def state_fromstring(self, string):
        """Load the state from a string."""
        # parse string in symbolic and signature aware environment
        env = symbolic.__dict__.copy()
        env.update(signature.__dict__)
        state = eval(string, env)
        if state["stateversion"] < self.requiredstateversion:
            # state is too old
            raise Exception("state outdated")
        # delete job attributes
        for attr in ("sampler", "submittime", "filename", "ncalls"):
            if attr in state:
                del state[attr]
        self.state_fromflat(state)

    def state_load(self, filename):
        """Try to laod the state from a file."""
        try:
            with open(filename) as fin:
                if filename[-4:] == ".ems":
                    self.state_fromstring(fin.read())
                    self.log("Loaded setup %r." % os.path.relpath(filename))
                else:
                    self.state_fromstring(fin.readline())
                    self.log("Loaded setup from %r." %
                             os.path.relpath(filename))
            return True
        except:
            self.alert("ERROR: Can't load setup from %r." %
                       os.path.relpath(filename))
            return False

    def state_write(self, filename):
        """Write the state to a file."""
        with open(filename, "w") as fout:
            pprint.pprint(self.state_toflat(), fout)
        self.log("Written setup to %r." % os.path.relpath(filename))

    def state_reset(self):
        """Reset the state to an initial configuration."""
        self.state_load(os.path.join(self.setuppath, "default.ems"))

    # info string
    def sampler_about_str(self):
        """Generate an info string about the current sampler."""
        sampler = self.sampler
        info = "System:\t%s\n" % sampler["system_name"]
        info += "BLAS:\t%s\n" % sampler["blas_name"]
        if sampler["backend"] != "local":
            info += "  (via %s)\n" % sampler["backend"]
        info += "\n"
        info += "CPU:\t%s\n" % sampler["cpu_model"]
        info += "Mhz:\t%.2f\n" % (sampler["frequency"] / 1e6)
        info += "Cores:\t%d\n" % sampler["nt_max"]
        if "dflops/cycle" in sampler:
            info += "Gflops/s:\t%.2f (peak)" % (
                sampler["dflops/cycle"] * sampler["frequency"] *
                sampler["nt_max"] / 1e9
            )
        return info

    # signatures
    def signature_get(self, routine):
        """Try to fetch the documentation for a routine."""
        if routine not in self.signatures:
            try:
                filename = os.path.join(self.signaturepath, routine + ".pysig")
                self.signatures[routine] = signature.Signature(file=filename)
                self.log("Loaded signature for %r." % routine)
            except:
                self.log("Couldn't load signature for %r." % routine)
                self.signatures[routine] = None
        return self.signatures[routine]

    # range routines
    def range_symdict(self, outer=True, inner=True):
        """create a symbolic dictionay fro the range variables."""
        symbols = {}
        if outer and self.userange["outer"]:
            rangevar = self.rangevars[self.userange["outer"]]
            symbols[rangevar] = symbolic.Symbol(rangevar)
        if inner and self.userange["inner"]:
            rangevar = self.rangevars[self.userange["inner"]]
            symbols[rangevar] = symbolic.Symbol(rangevar)
        return symbols

    def range_parse(self, expr, outer=True, inner=True):
        """Parse an expression respecing the range variables."""
        try:
            return eval(expr, {}, self.range_symdict(outer, inner))
        except:
            return None

    def range_eval(self, expr, outerval=None, innerval=None):
        """evaluate an symbolic expression for the ranges."""
        # outer range values
        outervals = outerval,
        if outerval is None and self.userange["outer"]:
            outervals = iter(self.ranges[self.userange["outer"]])
        # inner range
        if innerval is None and self.userange["inner"]:
            innerrange = self.ranges[self.userange["inner"]]

        symdict = {}
        # go over outer range
        for outerval2 in outervals:
            if outerval2 is not None:
                symdict[self.rangevars[self.userange["outer"]]] = outerval2

            # inner range values
            innervals = innerval,
            if innerval is None and self.userange["inner"]:
                innervals = iter(innerrange(**symdict))

            # go over inner range
            for innerval2 in innervals:
                if innerval2 is not None:
                    symdict[self.rangevars[self.userange["inner"]]] = innerval2

                # evaluate expression
                if isinstance(expr, symbolic.Expression):
                    yield expr(**symdict)
                else:
                    yield expr

    def range_eval_minmax(self, expr, outerval=None, innerval=None):
        """Evaluate an expression at the ranges' min and max."""
        # min
        outervalmin = outerval
        innervalmin = innerval
        symdict = {}
        if outervalmin is None and self.userange["outer"]:
            outervalmin = self.ranges[self.userange["outer"]].min()
        if outervalmin is not None:
            symdict[self.rangevars[self.userange["outer"]]] = outervalmin
        if innervalmin is None and self.userange["inner"]:
            innervalmin = self.ranges[self.userange["inner"]](**symdict).min()
        minimum = next(self.range_eval(expr, outervalmin, innervalmin))

        # max
        outervalmax = outerval
        innervalmax = innerval
        symdict = {}
        if outervalmax is None and self.userange["outer"]:
            outervalmax = self.ranges[self.userange["outer"]].max()
        if outervalmax is not None:
            symdict[self.rangevars[self.userange["outer"]]] = outervalmax
        if innervalmax is None and self.userange["inner"]:
            innervalmax = self.ranges[self.userange["inner"]](**symdict).max()
        maximum = next(self.range_eval(expr, outervalmax, innervalmax))

        return minimum, maximum

    def ranges_checkuseage(self):
        """Determine which active ranges are used in the calls."""
        # collect all symbols used in calls
        symbols = set()
        for call in self.calls:
            for arg in call:
                if isinstance(arg, symbolic.Expression):
                    symbols |= arg.findsymbols()

        # check if inner range is used
        result = {}
        inner = self.userange["inner"]
        if inner:
            result[inner] = self.rangevars[inner] in symbols

        # check if outer range is used
        outer = self.userange["outer"]
        if outer:
            result[outer] = self.rangevars[outer] in symbols

        return result

    # simple data operations
    def data_maxdim(self):
        """Compute the maximum dimension across all data."""
        return max(self.range_eval_minmax(dim)[1]
                   for data in self.data.itervalues()
                   if data["dims"] and not issubclass(data["type"],
                                                      signature.Work)
                   for dim in data["dims"])

    # inference system
    def infer_lds(self, callid=None, force=False):
        """Update all leading dimensions."""
        if callid is None:
            # infer lds for all calls
            for callid in range(len(self.calls)):
                self.infer_lds(callid, force)
            return

        call = self.calls[callid]
        if not isinstance(call, signature.Call):
            # only work on calls with signatures
            return
        sig = call.sig

        # 1: infer from call

        # complete leading dimension arguments
        call2 = call.copy()
        for argid, arg in enumerate(sig):
            if isinstance(arg, (signature.Ld, signature.Inc, signature.Lwork)):
                call2[argid] = None
        call2.complete()

        # set ld arguments
        for argid, arg in enumerate(sig):
            if isinstance(arg, (signature.Ld, signature.Inc)):
                if not self.showargs["lds"] or force:
                    call[argid] = call2[argid]
            elif isinstance(arg, signature.Lwork):
                if not self.showargs["work"] or force:
                    call[argid] = call2[argid]

        # 2: infer from data

        # get a symbolic representaiton of the data arguments
        symcall = call.copy()
        for argid, arg in enumerate(sig):
            if isinstance(arg, signature.Data):
                symcall[argid] = None
            elif isinstance(arg, (signature.Dim, signature.Ld, signature.Inc,
                                  signature.Lwork)):
                symcall[argid] = symbolic.Symbol("." + arg.name)
        symcall.complete()

        # find leading dimensions in data arguments
        for dataargid in sig.dataargs():
            if not call[dataargid] in self.data:
                # not a valid data argument
                continue
            data = self.data[call[dataargid]]

            # get dimensions in terms of call arguments
            sym = symcall[dataargid]
            if isinstance(sym, symbolic.Prod):
                symdims = [
                    dim() if isinstance(dim, symbolic.Expression) else dim
                    for dim in sym[1:]
                ]
            else:
                symdims = [
                    sym() if isinstance(sym, symbolic.Expression) else sym
                ]

            # check if lds are in dimension
            for argid, arg in enumerate(sig):
                if not isinstance(arg, signature.Ld):
                    continue
                if "." + arg.name in symdims:
                    call[argid] = data["lds"][symdims.index("." + arg.name)]

    def data_update(self, callid=None):
        """update the data objects from the calls."""
        if callid is None:
            # process all calls
            self.data = {}
            for callid in range(len(self.calls)):
                self.data_update(callid)
            self.vary = {name: vary for name, vary in self.vary.iteritems()
                         if name in self.data}
            return

        call = self.calls[callid]
        if not isinstance(call, signature.Call):
            # only for calls with signatures
            return

        # set up and complete calls
        sizecall = call.copy()  # only Data substituted
        symcall = call.copy()  # symbolic, no lds
        symldcall = call.copy()  # symbolic, lds
        for argid, arg in enumerate(call.sig):
            if isinstance(arg, signature.Data):
                sizecall[argid] = None
                symcall[argid] = None
            elif isinstance(arg, (signature.Ld, signature.Inc)):
                symcall[argid] = None
            elif isinstance(arg, (signature.Dim, signature.Lwork)):
                symcall[argid] = symbolic.Symbol("." + arg.name)
        sizecall.complete()
        symcall.complete()

        argdict = {"." + arg.name: val for arg, val in zip(call.sig, call)}
        for argid in call.sig.dataargs():
            name = call[argid]
            if name is None:
                continue
            data = {
                "size": sizecall[argid],
                "type": call.sig[argid].__class__,
            }

            # dimensions
            sym = symcall[argid]
            if isinstance(sym, symbolic.Prod):
                dims = [
                    dim(**argdict)
                    if isinstance(dim, symbolic.Expression) else dim
                    for dim in sym[1:]
                ]
            else:
                dims = [
                    sym(**argdict)
                    if isinstance(sym, symbolic.Expression) else dim
                ]
            if issubclass(data["type"], signature.Lwork):
                dims = [Prod(*dims)()]
            data["dims"] = dims

            # leading dimension
            lds = dims[:]
            if name in self.vary:
                # extract some variables
                vary = self.vary[name]
                along = vary["along"]
                across = vary["across"]
                userange_inner = self.userange["inner"]

                if along < len(lds) and lds[along] is not None:
                    if userange_inner in across:
                        # varying across range: sum over range
                        lds[along] = symbolic.Sum(
                            lds[along], **{
                                self.rangevars[userange_inner]:
                                self.ranges[userange_inner]
                            }
                        ).simplify()
                    if "reps" in across:
                        # varying across repetitions: multiply by count
                        lds[along] = self.nrep * lds[along]
            data["lds"] = lds

            self.data[name] = data

        # also update lds
        self.infer_lds(callid)

    def connections_update(self):
        """Update the argument connections based on data reuse."""
        # compute symbolic sizes for all calls
        sizes = defaultdict(list)
        for callid, call in enumerate(self.calls):
            if not isinstance(call, signature.Call):
                continue
            symcall = call.copy()
            for argid, arg in enumerate(call.sig):
                if isinstance(arg, signature.Dim):
                    symcall[argid] = symbolic.Symbol((callid, argid))
                elif isinstance(arg, (signature.Ld, signature.Inc,
                                      signature.Data)):
                    symcall[argid] = None
            symcall.complete()
            for argid in call.sig.dataargs():
                datasize = symcall[argid]
                if isinstance(datasize, symbolic.Prod):
                    datasize = datasize[1:]
                elif isinstance(datasize, symbolic.Symbol):
                    datasize = [datasize]
                elif isinstance(datasize, symbolic.Operation):
                    # try simplifying
                    datasize = datasize()
                    if isinstance(datasize, symbolic.Prod):
                        datasize = datasize[1:]
                    elif isinstance(datasize, symbolic.Symbol):
                        datasize = [datasize]
                    else:
                        continue
                else:
                    continue
                datasize = [
                    size.name if isinstance(size, symbolic.Symbol) else None
                    for size in datasize
                ]
                sizes[call[argid]].append(datasize)
        # deduce connections from symbolic sizes for each dataname
        connections = {
            (callid, argid): set([(callid, argid)])
            for callid, call in enumerate(self.calls)
            for argid in range(len(call))
        }
        # combine connections for each data item
        for datasizes in sizes.values():
            for idlist in zip(*datasizes):
                baseid = idlist[0]
                for callargid in idlist[1:]:
                    connections[baseid] |= connections[callargid]
                    for callargid2 in connections[callargid]:
                        connections[callargid2] = connections[baseid]
        self.connections = connections

    def connections_apply(self, callid, argid=None):
        """Apply the data connections, using the specified value loation."""
        if argid is None:
            argids = range(len(self.calls[callid]))
        else:
            argids = [argid]
        for argid in argids:
            value = self.calls[callid][argid]
            for callid2, argid2 in self.connections[callid, argid]:
                self.calls[callid2][argid2] = value

    # treat changes for the calls
    def sampler_set(self, samplername, setall=False):
        """Set the sampler and apply corresponding restrictions."""
        self.samplername = samplername
        self.nt = min(self.nt, self.sampler["nt_max"])

        # update counters (kill unavailable, adjust length)
        papi_counters_max = self.sampler["papi_counters_max"]
        self.options["papi"] &= papi_counters_max > 0
        counters = []
        for counter in self.counters:
            if counter in self.sampler["papi_counters_avail"]:
                counters.append(counter)
        counters = counters[:papi_counters_max]
        counters += (papi_counters_max - len(counters)) * [None]
        self.counters = counters

        # disable omp if not available
        if not self.sampler["omp_enabled"]:
            self.options["omp"] = False
            if self.userange["inner"] == "omp":
                self.UI_userange_change("outer", None)

        # remove unavailable calls
        self.calls = [call for call in self.calls
                      if call[0] in self.sampler["kernels"]]

        self.connections_update()
        self.data_update()
        if setall:
            self.UI_setall()

    def routine_set(self, callid, routine):
        """Set the routine and initialize its arguments."""
        oldroutine = self.calls[callid][0]
        if routine in self.sampler["kernels"]:
            minsig = self.sampler["kernels"][routine]
            call = [routine] + (len(minsig) - 1) * [None]
            self.calls[callid] = call
            sig = self.signature_get(routine)
            if sig:
                if len(sig) == len(minsig):
                    # TODO: better sanity check ?
                    try:
                        call = sig()
                        owndata = []
                        for i, arg in enumerate(call.sig):
                            if isinstance(arg, signature.Dim):
                                call[i] = self.defaultdim
                            elif isinstance(arg, signature.Data):
                                for name in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                                    if (name not in self.data and
                                            name not in owndata):
                                        call[i] = name
                                        owndata.append(name)
                                        break
                        self.calls[callid] = call
                    except:
                        self.UI_alert(
                            ("Can't use the signature %r\n"
                             "Signature Ignored") % sig
                        )
                else:
                    self.UI_alert(
                        ("Kernel %r of sampler %r has %d arguments,\n"
                         "however the signature '%s' requires %d.\n"
                         "Signature ignored.")
                        % (routine, self.samplername, len(minsig) - 1, sig,
                           len(sig) - 1)
                    )
        else:
            call = [routine]
            self.calls[callid] = [routine]
        self.calls[callid] = call
        self.connections_update()
        self.data_update()
        self.infer_lds(callid, True)
        if (routine in self.sampler["kernels"] or
                oldroutine in self.sampler["kernels"]):
            self.UI_submit_setenabled()
            self.UI_call_set(callid, 0)
            self.UI_vary_init()

    def arg_set(self, callid, argid, value):
        """Set an argument and apply corresponding updates."""
        call = self.calls[callid]
        if isinstance(call, signature.Call):
            arg = call.sig[argid]
        else:
            arg = self.sampler["kernels"][call[0]][argid]
        if isinstance(arg, signature.Flag):
            call[argid] = value
            self.connections_update()
            self.connections_apply(callid)
            self.data_update()
            self.UI_calls_set(callid, argid)
            self.UI_vary_set()
            self.UI_data_viz()
        elif isinstance(arg, signature.Scalar):
            call[argid] = self.range_parse(value)
            self.UI_call_set(callid, argid)
            self.UI_range_unusedalerts_set()
        elif isinstance(arg, signature.Dim):
            # evaluate value
            call[argid] = self.range_parse(value)
            self.connections_apply(callid, argid)
            self.data_update()
            self.UI_calls_set(callid, argid)
            self.UI_data_viz()
            self.UI_range_unusedalerts_set()
        elif isinstance(arg, signature.Data):
            if not value:
                value = None
            if value in self.data:
                # resolve potential conflicts
                self.data_override(callid, argid, value)
            else:
                call[argid] = value
                self.connections_update()
                self.data_update()
                self.UI_vary_init()
                self.UI_call_set(callid, argid)
                self.UI_data_viz()
        elif isinstance(arg, (signature.Ld, signature.Inc, signature.Lwork)):
            call[argid] = self.range_parse(value)
            self.data_update()
            self.UI_calls_set(callid, argid)
            self.UI_range_unusedalerts_set()
        # calls without proper signatures
        else:
            if value is None:
                call[argid] = None
            elif arg == "char*":
                call[argid] = value
            elif value[0] == "[" and value[-1] == "]":
                # datasize specification syntax [size]
                parsed = self.range_parse(value[1:-1])
                call[argid] = None
                if parsed is not None:
                    call[argid] = "[" + str(parsed) + "]"
                # TODO: the check won't work for strings containing rangevars
                self.UI_range_unusedalerts_set()
            else:
                call[argid] = self.range_parse(value)
                self.UI_range_unusedalerts_set()
            self.UI_call_set(callid, argid)
        self.UI_submit_setenabled()

    # catch and handle data conflicts
    def data_override(self, callid, argid, value):
        """(propose to) resolve conflicting data dimensions."""
        thistype = self.calls[callid].sig[argid].__class__
        othertype = self.data[value]["type"]
        if thistype != othertype:
            self.UI_alert("Incompatible data types for %r: %r and %r." %
                          (value, thistype.typename, othertype.typename))
            self.UI_call_set(callid)
            return
        call = self.calls[callid]
        oldvalue = call[argid]  # backup
        # apply change and check consistency
        call[argid] = value
        self.connections_update()
        for argid2, value2 in enumerate(call):
            if not all(value2 == self.calls[callid3][argid3] for callid3,
                       argid3 in self.connections[callid, argid2]):
                # inconsistency: restore backup and query override
                call[argid] = oldvalue
                self.connections_update()
                callbacks = {
                    "Ok": (self.data_override_ok, (callid, argid, value)),
                    "Cancel": (self.data_override_cancel,
                               (callid, argid, value))
                }
                self.UI_dialog(
                    "warning", "Incompatible sizes for " + value,
                    "Dimension arguments will be adjusted automatically.",
                    callbacks
                )
                return

    def data_override_ok(self, callid, argid, value):
        """Automatically resolve data conflicts."""
        self.calls[callid][argid] = value
        self.connections_update()
        for callid2 in range(len(self.calls)):
            if callid2 != callid:
                self.connections_apply(callid2)
        self.connections_apply(callid)
        self.data_update()
        self.UI_vary_init()
        self.UI_calls_set()
        self.UI_data_viz()

    def data_override_cancel(self, callid, argid, value):
        """Undo the variable change leading to conflicts."""
        self.UI_call_set(callid)

    def calls_checksanity(self):
        """Check if all calls are valid."""
        for call in self.calls:
            if call[0] not in self.sampler["kernels"]:
                return False
            if any(arg is None for arg in call):
                return False
        return True

    # submit
    def generate_cmds(self, ntrangeval=None):
        """Generate commands for the sampler."""
        cmds = []

        # common expressions
        userange_outer = self.userange["outer"]
        userange_inner = self.userange["inner"]
        if userange_outer:
            rangevar_outer = self.rangevars[userange_outer]

        def varname(name, outerval, rep, innerval):
            """Construct a variable name.

            Format: <name>[_<outerval>][_<rep>][_<innerval>]
            """
            if not self.options["vary"] or name not in self.vary:
                return name
            vary = self.vary[name]
            parts = [name]
            if userange_outer:
                parts.append(outerval)
            if "reps" in vary["across"]:
                parts.append(rep)
            if userange_inner in vary["across"]:
                parts.append(innerval)
            return "_".join(map(str, parts))

        outervals = None,
        if ntrangeval is not None:
            outervals = ntrangeval,
        elif userange_outer:
            outervals = self.ranges[userange_outer]

        if self.options["papi"] and len(self.counters):
            cmds += [
                ["########################################"],
                ["# counters                             #"],
                ["########################################"],
                [],
                ["set_counters"] + list(filter(None, self.counters)),
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
            signature.cData: "s",
            signature.zData: "z",
        }

        # go over all operands
        for name, data in self.data.iteritems():
            cmdprefix = cmdprefixes[data["type"]]

            # comment
            cmds += [[], ["# %s" % name]]

            if not self.options["vary"] or name not in self.vary:
                # argumnet doesn't vary
                size = max(self.range_eval(data["size"], ntrangeval))
                cmds.append([cmdprefix + "malloc", name, size])
                continue
            # operand varies

            # set up some reused variables
            vary = self.vary[name]
            across = vary["across"]
            along = vary["along"]
            repvals = None,
            if "reps" in across:
                repvals = range(self.nrep + 1)

            # init result variables
            offsetcmds = []
            size_max = 0
            offset_max = 0
            # go over outer range
            for outerval in outervals:
                if outerval is not None:
                    # comment
                    offsetcmds.append(["#", rangevar_outer, "=", outerval])

                # prepare inner range
                innervals = None,
                if userange_inner:
                    innerrange = self.ranges[userange_inner]
                    if userange_outer:
                        innerrange = innerrange(**{rangevar_outer: outerval})
                    innervals = list(innerrange)

                # go over repetitions
                for rep in repvals:
                    # offset for repetitions
                    offset_rep = 0
                    if "reps" in across:
                        # operand varies across repetitions
                        offset_rep = offset_max

                    if userange_inner not in across:
                        # operand doesn't vary in inner range (1 offset)
                        offsetcmds.append([
                            cmdprefix + "offset", name, offset_rep,
                            varname(name, outerval, rep, None)
                        ])
                    else:
                        # comment (multiple offsets)
                        offsetcmds.append(["# repetition", rep])

                    # offset for inner rnage
                    offset = offset_rep
                    # go over inner range
                    for innerval in innervals:
                        if userange_inner in across:
                            # operand varies in inner range (offset)
                            offsetcmds.append([
                                cmdprefix + "offset", name, offset,
                                varname(name, outerval, rep, innerval)
                            ])
                        else:
                            # offset is the same every iteration
                            offset = offset_rep
                        # compute next offset
                        dim = 1
                        for idx in range(along):
                            # multiply leading dimensions for skipped dims
                            dim *= next(self.range_eval(data["lds"][idx],
                                                        outerval, innerval))
                        # dimension for traversed dim
                        if along < len(data["dims"]):
                            dim *= next(self.range_eval(data["dims"][along],
                                                        outerval, innerval))
                        # add custom offset
                        offset += dim + next(self.range_eval(vary["offset"],
                                                             outerval,
                                                             innerval))
                        # update max size and offset
                        offset_max = max(offset_max, offset)
                        size = next(self.range_eval(data["size"], outerval,
                                                    innerval))
                        size_max = max(size_max, offset + size)

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

        # go over outer range
        for outerval in outervals:
            if userange_outer == "range":
                # comment
                cmds += [[], ["# %s = %d" % (rangevar_outer, outerval)]]

            # set up inner range values
            innervals = None,
            if userange_inner:
                innerrange = self.ranges[userange_inner]
                if userange_outer:
                    innerrange = innerrange(**{rangevar_outer: outerval})
                innervals = list(innerrange)

            # go over repetitions
            for rep in range(self.nrep + 1):
                if userange_inner:
                    # commentsj
                    cmds += [[], ["# repetition %d" % rep]]
                if userange_inner == "omp":
                    # begin omp range
                    cmds.append(["{omp"])

                # go over inner range
                for innerval in innervals:
                    if userange_inner != "omp" and self.options["omp"]:
                        # begin parallel calls
                        cmds.append(["{omp"])

                    # go over calls
                    for call in self.calls:
                        if isinstance(call, signature.Call):
                            # call with signature

                            # evaluate symbolic arguments
                            call = call.sig(*[
                                next(self.range_eval(val, outerval, innerval))
                                for val in call[1:]
                            ])
                            # format for the sampler
                            cmd = call.format_sampler()
                            # place operand variables
                            for argid in call.sig.dataargs():
                                cmd[argid] = varname(
                                    cmd[argid], outerval, rep, innerval
                                )
                        else:
                            # call without signature
                            cmd = call[:]
                            minsig = self.sampler["kernels"][call[0]]

                            # go over arguments
                            for argid, value in enumerate(call):
                                if argid == 0 or minsig[argid] == "char":
                                    # chars don't need further processing
                                    continue
                                if isinstance(value, str):
                                    if value[0] == "[" and value[-1] == "]":
                                        # parse string as array argument [ ]
                                        expr = self.range_parse(value[1:-1])
                                        if expr is not None:
                                            value = next(self.range_eval(
                                                expr, outerval, innerval
                                            ))
                                            call[argid] = "[%s]" % str(value)
                                        # TODO: parse list argument
                                else:
                                    # parse scalar arguments
                                    expr = self.range_parse(value)
                                    if expr is not None:
                                        value = next(self.range_eval(
                                            expr, outerval, innerval
                                        ))
                                        call[argid] = str(value)

                        # add created call
                        cmds.append(cmd)

                    if userange_inner != "omp" and self.options["omp"]:
                        # end parallel calls
                        cmds.append(["}"])

                if userange_inner == "omp":
                    # end omp range
                    cmds.append(["}"])

            # execute outer range iteration
            cmds.append(["go"])

        return cmds

    def submit(self, filename):
        """Submit the current job."""
        # prepare the filenames
        filebase = filename
        if filename[-4:] == ".emr":
            filebase = filebase[:-4]
        scriptfile = filebase + ".script"
        reportfile = filebase + ".emr"
        errfile = filebase + ".err"

        # get the jobname
        jobname = os.path.basename(filebase)

        # make sure the lds are reflected in sizes
        self.data_update()

        # some shorthands
        header = self.sampler["backend_header"]
        prefix = self.sampler["backend_prefix"]
        suffix = self.sampler["backend_suffix"]
        footer = self.sampler["backend_footer"]
        userange_outer = self.userange["outer"]

        # emptly output files
        open(reportfile, "w").close()
        open(errfile, "w").close()

        script = ""

        # backend header
        if header:
            script += header.format(nt=self.nt) + "\n"

        # script header (from GUI)
        if self.options["header"]:
            script += self.header + "\n"

        # report header
        reportinfo = self.state.copy()
        sampler = self.sampler.copy()
        del sampler["kernels"]
        reportinfo.update({
            "sampler": sampler,
            "submittime": time.time(),
            "filename": reportfile,
            "ncalls": (len(list(self.range_eval(0))) *
                       (self.nrep + 1) * len(self.calls))
        })
        reportinfo["nlines"] = reportinfo["ncalls"]
        if self.userange["inner"] == "omp":
            reportinfo["nlines"] = (len(list(self.range_eval(0, innerval=0)))
                                    * (self.nrep + 1))
        elif self.options["omp"]:
            reportinfo["nlines"] /= len(self.calls)
        script += "cat > %s <<REPORTINFO\n%s\nREPORTINFO\n" % (
            reportfile, repr(reportinfo)
        )

        # timing
        script += "date +%%s >> %s\n" % reportfile

        # set up #threads range
        ntvals = self.nt,
        if userange_outer == "threads":
            ntvals = self.ranges["threads"]

        # go over #threads range
        for ntval in ntvals:
            # filename for commands
            if userange_outer == "threads":
                callfile = filebase + ".%d.calls" % ntval
            else:
                callfile = filebase + ".calls"

            # generate commands file
            if userange_outer == "threads":
                cmds = self.generate_cmds(ntval)
            else:
                cmds = self.generate_cmds()
            with open(callfile, "w") as fout:
                for cmd in cmds:
                    print(*cmd, file=fout)

            # compute omp thread count
            ompthreads = 1
            if self.userange["inner"] == "omp":
                # omp range
                omprange = self.ranges["omp"]
                if userange_outer == "threads":
                    omprange = omprange(**{self.rangevars["threads"]: ntval})
                elif userange_outer:
                    omprange = omprange(**{self.rangevars[userange_outer]:
                                           self.ranges[userange_outer].max()})
                ompthreads = len(self.calls) * len(omprange)
            elif self.options["omp"]:
                # parallel calls
                ompthreads = len(self.calls)
            # limit threads to #cores * #hyperthreads/core
            ompthreads = min(ompthreads, sampler["nt_max"])

            # sampler invocation
            if prefix:
                script += prefix.format(nt=ntval) + " "
            if ompthreads != 1:
                script += "OMP_NUM_THREADS=%d " % ompthreads
            script += "%(x)s < %(i)s >> %(o)s 2>> %(e)s || exit" % {
                "x": self.sampler["sampler"],  # executable
                "i": callfile,  # input
                "o": reportfile,  # output
                "e": errfile  # error
            }
            if suffix:
                script += " " + suffix.format(nt=ntval)
            script += "\n"

            # exit upon error
            script += "[ -s %s ] && exit\n" % errfile

            # delete call file
            script += "rm %s\n" % callfile

        # timing
        script += "date +%%s >> %s\n" % reportfile

        # delete script file
        script += "rm " + scriptfile + "\n"

        # delete errfile (it's empty if we got so far)
        script += "rm %s" % errfile

        if footer:
            script += "\n" + footer.format(nt=self.nt)

        # write script file (dubug)
        with open(scriptfile, "w") as fout:
            fout.write(script)

        # submit
        backend = self.backends[self.sampler["backend"]]
        jobid = backend.submit(script, nt=self.nt, jobname=jobname)

        # track progress
        self.jobprogress_add(jobid, reportinfo)
        self.UI_jobprogress_show()
        self.log("Submitted %r to %r." % (jobname, self.sampler["backend"]))

    # jobprogress
    def jobprogress_add(self, jobid, reportinfo):
        """Add an entry to the jobprogress tracker."""
        backend = self.sampler["backend"]
        self.jobprogress[backend, jobid] = {
            "backend": backend,
            "id": jobid,
            "filebase": reportinfo["filename"][:-4],
            "progress": -1,
            "progressend": reportinfo["nlines"],
            "error": False,
        }

    def jobprogress_update(self):
        """Update all jobprogress states."""
        for job in self.jobprogress.itervalues():
            if job["error"] or job["progress"] >= job["progressend"]:
                continue
            with open(job["filebase"] + ".emr") as fin:
                job["progress"] = len(fin.readlines()) - 2
            if os.path.isfile(job["filebase"] + ".err"):
                if os.path.getsize(job["filebase"] + ".err"):
                    job["error"] = True

    # kernel documentation
    def docs_get(self, routine):
        """Try to fetch the documentation for a routine."""
        if routine not in self.docs:
            try:
                filename = os.path.join(self.docspath, routine + ".pydoc")
                with open(filename) as fin:
                    self.docs[routine] = eval(fin.read(), {}, {})
                self.log("Loaded documentation for %r." % routine)
            except:
                self.docs[routine] = None
        return self.docs[routine]

    def UI_setall(self):
        """Set all GUI elements."""
        self.UI_sampler_set()
        self.UI_sampler_about_set()
        self.UI_nt_setmax()
        self.UI_nt_set()
        self.UI_nrep_set()
        self.UI_showargs_set()
        self.UI_counters_setoptions()
        self.UI_counters_set()
        self.UI_header_set()
        self.UI_useranges_set()
        self.UI_options_set()
        self.UI_ranges_set()
        self.UI_range_unusedalerts_set()
        self.UI_vary_init()
        self.UI_calls_init()
        self.UI_submit_setenabled()

    # event handlers
    def UI_submit(self, filename):
        """Event: Submit a job."""
        self.submit(filename)

    def UI_state_reset(self):
        """Event: Reset the state."""
        self.state_reset()
        self.UI_setall()

    def UI_state_import(self, filename):
        """Event: Import the state."""
        self.state_load(filename)
        self.UI_setall()

    def UI_state_export(self, filename):
        """Event: Export the state."""
        self.state_write(filename)

    def UI_sampler_change(self, samplername):
        """Event: Change the sampler."""
        newsampler = self.samplers[samplername]
        missing = set(call[0] for call in self.calls
                      if call[0] in self.sampler["kernels"]
                      and call[0] not in newsampler["kernels"])
        if missing:
            self.UI_dialog(
                "warning", "Unsupported kernels",
                "%r doesn't support %s\nCorresponding calls will be removed"
                % (samplername, ", ".join(map(repr, missing))), {
                    "Ok": (self.sampler_set, (samplername, True)),
                    "Cancel": None
                }
            )
        else:
            self.sampler_set(samplername, True)

    def UI_nt_change(self, nt):
        """Event: Changed the #threads."""
        self.nt = nt

    def UI_infer_lds(self):
        """Event: Infer leading dimensions."""
        self.infer_lds(force=True)
        self.data_update()
        self.UI_calls_set()

    def UI_option_change(self, optionname, state):
        """Event: Change in the option."""
        self.options[optionname] = state
        self.UI_options_set()

    def UI_showargs_change(self, name, state):
        """Event: Change in the argument showing options."""
        self.showargs[name] = state
        self.UI_showargs_apply()

    def UI_counters_change(self, counters):
        """Event: Change in counters."""
        self.counters = counters

    def UI_header_change(self, header):
        """Event: Change in the script header."""
        self.header = header

    def UI_userange_change(self, rangetype, rangename):
        """Event: Change in used ranges."""
        if self.userange[rangetype]:
            oldname = self.userange[rangetype]
            oldrange = self.ranges[oldname]
            userange_outer = self.userange["outer"]
            if rangetype == "inner" and userange_outer:
                oldrange = oldrange(**{
                    self.rangevars[userange_outer]:
                    self.ranges[userange_outer].max()
                })
            subst = {self.rangevars[oldname]: oldrange.max()}
            # get rid of old range in variables
            for call in self.calls:
                for argid, arg in enumerate(call):
                    if isinstance(arg, symbolic.Expression):
                        call[argid] = arg(**subst)
            # get rid of old range in inner range
            if rangetype == "outer":
                for innername in self.rangetypes["inner"]:
                    self.ranges[innername] = self.ranges[innername](**subst)
            # get rid of range in varys
            for name in self.data:
                if name not in self.vary:
                    continue
                vary = self.vary[name]
                if rangetype == "inner":
                    vary["across"].discard(self.userange["inner"])
                    if not vary["across"]:
                        del self.vary[name]
                # TODO remove rangevar from vary offset
            self.data_update()
            self.UI_calls_set()
        self.userange[rangetype] = rangename
        if rangename == "threads":
            self.ranges["threads"] = symbolic.Range((1, 1, self.nt))
        self.userange[rangetype] = rangename
        self.UI_useranges_set()
        self.UI_range_unusedalerts_set()
        self.UI_options_set()
        self.UI_vary_set()

    def UI_rangevar_change(self, rangename, value):
        """Event: Range variable changed."""
        if not value:
            # TODO: notify user
            return
        subst = {self.rangevars[rangename]: symbolic.Symbol(value)}
        # change variable name in calls
        for call in self.calls:
            for argid, arg in enumerate(call):
                if isinstance(arg, symbolic.Expression):
                    call[argid] = arg.substitute(**subst)
        # change variable name in inner range
        if rangename in self.rangetypes["outer"]:
            for innername in self.rangetypes["inner"]:
                self.ranges[innername] = self.ranges[innername](**subst)
        # TODO: change variable name vary offsets
        self.rangevars[rangename] = value
        self.data_update()
        self.UI_vary_set()
        self.UI_calls_set()

    def UI_range_change(self, rangename, value):
        """Event: Range changed."""
        symdict = {}
        if rangename in self.rangetypes["inner"]:
            symdict = self.range_symdict(inner=False)
        try:
            self.ranges[rangename] = symbolic.Range(value, **symdict)
        except:
            # TODO: notifiy user
            return
        if rangename == "threads":
            self.nt = self.ranges[rangename].max()
        self.data_update()
        self.UI_data_viz()

    def UI_nrep_change(self, nrep):
        """Event: number of repetitions changed."""
        if nrep:
            self.nrep = int(nrep)
        # TODO: else notify user

    def UI_call_add_click(self):
        """Event: Add a call."""
        self.calls.append([""])
        self.UI_call_add()
        self.UI_submit_setenabled()
        self.UI_arg_setfocus(len(self.calls) - 1, 0)

    def UI_call_remove(self, callid):
        """Event: remove a call."""
        del self.calls[callid]
        self.connections_update()
        self.data_update()
        self.UI_calls_init()
        self.UI_vary_init()
        self.UI_submit_setenabled()

    def UI_calls_reorder(self, order):
        """Event: Calls reordered."""
        self.calls = [self.calls[i] for i in order]
        self.connections_update()

    def UI_arg_change(self, callid, argid, value):
        """Event: Changed an arguments."""
        if argid == 0:
            self.routine_set(callid, value)
        else:
            self.arg_set(callid, argid, value)

    def UI_vary_change(self, name, vary):
        """Event: Changed how operands vary."""
        if vary is False:
            del self.vary[name]
        elif vary is True:
            self.vary[name] = {
                "across": set(["reps"]),
                "along": 1,
                "offset": 0
            }
        else:
            self.vary[name] = vary
            if not vary["across"]:
                del self.vary[name]
        # vary may affect lds
        self.data_update()
        self.UI_vary_set(name)
        self.UI_calls_set()

    def UI_jobkill(self, jobid):
        """Event: Kill a job."""
        backend, bjobid = jobid
        self.backends[backend].kill(bjobid)
        del self.jobprogress[jobid]
        self.UI_jobprogress_show()

    def UI_jobview(self, jobid):
        """Event: View a job's report."""
        job = self.jobprogress[jobid]
        self.UI_viewer_load(job["filebase"] + ".emr")

    def UI_jobprogress_hide(self, jobid):
        """Event: Hide a job."""
        del self.jobprogress[jobid]
        self.UI_jobprogress_show()
