#!/usr/bin/env python
from __future__ import division, print_function

import signature
import symbolic

import sys
import os
import imp
import time
from collections import defaultdict
from __builtin__ import intern  # fix for pyflake error


class GUI(object):
    requiredbuildversion = 1422278229
    requiredstateversion = 1423087329
    state = {}

    def __init__(self, loadstate=True):
        thispath = os.path.dirname(__file__)
        if thispath not in sys.path:
            sys.path.append(thispath)
        self.rootpath = os.path.abspath(os.path.join(thispath, "..", ".."))
        self.reportpath = os.path.join(self.rootpath, "GUI", "reports")

        self.backends_init()
        self.samplers_init()
        self.signatures_init()
        self.ranges_init()
        self.docs_init()
        self.UI_init()
        self.jobprogress_init()
        self.state_init(loadstate)

    # state access attributes
    def __getattr__(self, name):
        if name in self.__dict__["state"]:
            return self.__dict__["state"][name]
        if name == "sampler":
            return self.samplers[self.samplername]
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))

    def __setattr__(self, name, value):
        if name in self.state:
            self.state[name] = value
        else:
            super(GUI, self).__setattr__(name, value)

    def start(self):
        self.UI_start()

    # utility
    def log(self, *args):
        print(*args)

    def alert(self, *args):
        print(*args, file=sys.stderr)

    # initializers
    def backends_init(self):
        self.backends = {}
        backendpath = os.path.join(self.rootpath, "GUI", "src", "backends")
        for filename in os.listdir(backendpath):
            if not filename[-3:] == ".py":
                continue
            name = filename[:-3]
            module = imp.load_source(name, os.path.join(backendpath, filename))
            if hasattr(module, name):
                self.backends[name] = getattr(module, name)()
        self.log("loaded", len(self.backends), "backends:",
                 *sorted(self.backends))
        if len(self.backends) == 0:
            raise Exception("No backends found")

    def samplers_init(self):
        self.samplers = {}
        samplerpath = os.path.join(self.rootpath, "Sampler", "build")
        for path, dirs, files in os.walk(samplerpath, followlinks=True):
            if "info.py" in files and "sampler.x" in files:
                with open(os.path.join(path, "info.py")) as fin:
                    sampler = eval(fin.read())
                if sampler["buildtime"] < self.requiredbuildversion:
                    self.alert("backend", sampler["name"],
                               "is outdated.  Please rebuild!")
                    continue
                if sampler["backend"] not in self.backends:
                    self.alert("missing backend %r for sampler %r"
                               % (sampler["backend"], sampler["name"]))
                    continue
                sampler["sampler"] = os.path.join(path, "sampler.x")
                sampler["kernels"] = {kernel[0]: tuple(map(intern, kernel))
                                      for kernel in sampler["kernels"]}
                self.samplers[sampler["name"]] = sampler
        self.log("loaded", len(self.samplers), "samplers:",
                 *sorted("%s (%d)" % (name, len(sampler["kernels"]))
                         for name, sampler in self.samplers.iteritems()))
        if len(self.samplers) == 0:
            raise Exception("No samplers found")

    def signatures_init(self):
        self.signatures = {}
        signaturepath = os.path.join(self.rootpath, "GUI", "signatures")
        for path, dirs, files in os.walk(signaturepath, followlinks=True):
            for filename in files:
                if filename[0] == "." or filename[-6:] != ".pysig":
                    continue
                try:
                    sig = signature.Signature(file=os.path.join(path,
                                                                filename))
                    self.signatures[str(sig[0])] = sig
                except:
                    self.alert("couldn't load", os.path.relpath(filename))
        self.log("loaded", len(self.signatures), "signatures:",
                 *sorted(self.signatures))
        self.nosigwarning_shown = False

    def state_init(self, load=True):
        self.state_reset()

    def ranges_init(self):
        self.rangetypes = {
            "outer": ("threads", "range"),
            "inner": ("sum",)
        }

    def docs_init(self):
        self.docspath = os.path.join(self.rootpath, "GUI", "kerneldocs")
        self.docs = {}

    def jobprogress_init(self):
        self.jobprogress = []

    # state routines
    def state_toflat(self):
        state = self.state.copy()
        state["calls"] = tuple(map(tuple, self.calls))
        state["counters"] = tuple(self.counters)
        state["ranges"] = {rangename: range.subranges
                           for rangename, range in self.ranges.iteritems()}
        return state

    def state_fromflat(self, state):
        state = state.copy()
        calls = list(map(list, state["calls"]))
        # apply signatures
        for callid, call in enumerate(calls):
            if call[0] in self.signatures:
                sig = self.signatures[call[0]]
                try:
                    calls[callid] = sig(*call[1:])
                except:
                    self.UI_alert(
                        ("Could not applying the signature '%s' to '%s(%s)'.\n"
                         "Signature Ignored.") % (str(sig), call[0], call[1:])
                    )
        state["calls"] = calls
        # set ranges
        state["ranges"] = {key: symbolic.Range(*val)
                           for key, val in state["ranges"].iteritems()}
        # check if sampler is available
        samplername = state["samplername"]
        if samplername not in self.samplers:
            samplername = min(self.sampler)
            self.alert("sampler %r is not available, using %r instead"
                       % (state["samplername"], samplername))
        self.state = state
        self.sampler_set(samplername)
        self.connections_update()
        self.data_update()
        self.UI_setall()

    def state_reset(self):
        sampler = self.samplers[min(self.samplers)]
        state = {
            "statetime": time.time(),
            "stateversion": self.requiredstateversion,
            "samplername": sampler["name"],
            "nt": 1,
            "ranges": {
                "threads": ((1, 0, 1),),
                "range": ((8, 32, 1000),),
                "sum": ((1, 1, 10),)
            },
            "rangevars": {
                "threads": "nt",
                "range": "n",
                "sum": "m"
            },
            "userange": {
                "outer": "range",
                "inner": None,
            },
            "usepapi": False,
            "useheader": False,
            "usevary": False,
            "showargs": {
                "flags": True,
                "scalars": True,
                "lds": False,
                "infos": False
            },
            "counters": sampler["papi_counters_max"] * [None],
            "header": "# script header\n",
            "nrep": 10,
            "calls": [[""]],
            "vary": set(),
            "datascale": 100,
            "defaultdim": 1000
        }
        if "dgemm_" in sampler["kernels"]:
            n = symbolic.Symbol("n")
            state["calls"] = [
                ("dgemm_", "N", "N", n, n, n, 1, "A", n, "B", n, 1, "C", n)
            ]
        self.state_fromflat(state)

    def state_fromstring(self, string):
        env = symbolic.__dict__.copy()
        env.update(signature.__dict__)
        state = eval(string, env)
        if state["stateversion"] < self.requiredstateversion:
            raise Exception
        if "sampler" in state:
            del state["sampler"]
        if "submittime" in state:
            del state["submittime"]
        self.state_fromflat(state)

    def state_load(self, filename):
        try:
            with open(filename) as fin:
                self.state_fromstring(fin.read())
            self.log("loaded state from", os.path.relpath(filename))
            return True
        except:
            self.alert("could not load state from", os.path.relpath(filename))
            return False

    # info string
    def sampler_about_str(self):
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

    # range routines
    def range_symdict(self, outer=True, inner=True):
        symbols = {}
        if outer and self.userange["outer"]:
            rangevar = self.rangevars[self.userange["outer"]]
            symbols[rangevar] = symbolic.Symbol(rangevar)
        if inner and self.userange["inner"]:
            rangevar = self.rangevars[self.userange["inner"]]
            symbols[rangevar] = symbolic.Symbol(rangevar)
        return symbols

    def range_parse(self, text, outer=True, inner=True):
        try:
            return eval(text, {}, self.range_symdict(outer, inner))
        except:
            return None

    def range_eval(self, expr, outerval=None, innerval=None):
        if not isinstance(expr, symbolic.Expression):
            yield expr
            return
        outervals = outerval,
        if outerval is None and self.userange["outer"]:
            outervals = iter(self.ranges[self.userange["outer"]])
        symdict = {}
        for outerval2 in outervals:
            if outerval2 is not None:
                symdict[self.rangevars[self.userange["outer"]]] = outerval2
            innervals = innerval,
            if innerval is None and self.userange["inner"]:
                innervals = iter(self.ranges[self.userange["inner"]])
            for innerval2 in innervals:
                if innerval2 is not None:
                    symdict[self.rangevars[self.userange["inner"]]] = innerval2
                yield expr(**symdict)

    # simple data operations
    def data_maxdim(self):
        result = 0
        for data in self.data.itervalues():
            sym = data["sym"]
            if isinstance(sym, symbolic.Prod):
                datamax = max(max(self.range_eval(val)) for val in sym[1:])
            else:
                datamax = max(self.range_eval(sym))
            result = max(result, datamax)
        return result

    # inference system
    def infer_lds(self, callid=None):
        if callid is None:
            for callid in range(len(self.calls)):
                self.infer_lds(callid)
            return
        call = self.calls[callid]
        if not isinstance(call, signature.Call):
            return
        call2 = call.copy()
        for i, arg in enumerate(call2.sig):
            if isinstance(arg, (signature.Ld, signature.Inc)):
                call2[i] = None
        call2.complete()
        for argid, arg in enumerate(call2.sig):
            if isinstance(arg, (signature.Ld, signature.Inc)):
                if (self.showargs["lds"] and
                        not isinstance(call2[argid], symbolic.Expression)):
                    call[argid] = max(call2[argid], call[argid])
                else:
                    call[argid] = call2[argid]

    def data_update(self, callid=None):
        if callid is None:
            self.data = {}
            for callid in range(len(self.calls)):
                self.data_update(callid)
            self.vary = {name for name in self.vary if name in self.data}
            return
        call = self.calls[callid]
        if not isinstance(call, signature.Call):
            return
        compcall = call.copy()
        mincall = call.copy()
        symcall = call.copy()
        for argid, arg in enumerate(call.sig):
            if isinstance(arg, signature.Data):
                compcall[argid] = None
                mincall[argid] = None
                symcall[argid] = None
            elif isinstance(arg, (signature.Ld, signature.Inc)):
                mincall[argid] = None
                symcall[argid] = None
            elif isinstance(arg, signature.Dim):
                symcall[argid] = symbolic.Symbol("." + arg.name)
        compcall.complete()
        mincall.complete()
        symcall.complete()
        argdict = {"." + arg.name: val for arg, val in zip(call.sig, call)}
        argnamedict = {"." + arg.name: symbolic.Symbol(arg.name)
                       for arg in call.sig}
        for argid in call.sig.dataargs():
            name = call[argid]
            if name is None:
                continue
            self.data[name] = {
                "comp": compcall[argid],
                "min": mincall[argid],
                "sym": None,
                "symnames": None,
                "type": call.sig[argid].__class__,
            }
            if symcall[argid] is not None:
                self.data[name]["sym"] = symcall[argid].substitute(**argdict)
                self.data[name]["symnames"] = symcall[argid].substitute(
                    **argnamedict
                )

    def connections_update(self):
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
                    datasize = datasize.simplify()
                    if isinstance(datasize, symbolic.Prod):
                        datasize = datasize[1:]
                    elif isinstance(datasize, symbolic.Symbol):
                        datasize = [datasize]
                    else:
                        continue
                else:
                    continue
                datasize = [size.name for size in datasize]
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
        if argid is None:
            argids = range(len(self.calls[callid]))
        else:
            argids = [argid]
        for argid in argids:
            value = self.calls[callid][argid]
            for callid2, argid2 in self.connections[(callid, argid)]:
                self.calls[callid2][argid2] = value

    # treat changes for the calls
    def sampler_set(self, samplername):
        self.samplername = samplername
        self.nt = max(self.nt, self.sampler["nt_max"])

        # update countes (kill unavailable, adjust length)
        papi_counters_max = self.sampler["papi_counters_max"]
        self.usepapi &= papi_counters_max > 0
        counters = []
        for counter in self.counters:
            if counter in self.sampler["papi_counters_avail"]:
                counters.append(counter)
        counters = counters[:papi_counters_max]
        counters += (papi_counters_max - len(counters)) * [None]
        self.counters = counters

        # remove unavailable calls
        self.calls = [call for call in self.calls
                      if call[0] in self.sampler["kernels"]]

        self.data_update()
        # update UI
        self.UI_nt_setmax()
        self.UI_nt_set()
        self.UI_usepapi_setenabled()
        self.UI_usepapi_set()
        self.UI_counters_setoptions()
        self.UI_counters_set()
        self.UI_sampler_about_set()
        self.UI_calls_init()

    def routine_set(self, callid, value):
        if value in self.sampler["kernels"]:
            minsig = self.sampler["kernels"][value]
            call = [value] + (len(minsig) - 1) * [None]
            self.calls[callid] = call
            if value in self.signatures:
                sig = self.signatures[value]
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
                        self.infer_lds(callid)
                    except:
                        self.UI_alert(
                            ("Could not use the signature '%s'\n"
                             "Signature Ignored") % str(sig)
                        )
                else:
                    self.UI_alert(
                        ("Kernel %r of sampler %r has %d arguments,\n"
                         "however the signature '%s' requires %d.\n"
                         "Signature ignored.")
                        % (value, self.samplername, len(minsig) - 1, str(sig),
                           len(sig) - 1)
                    )
        else:
            call = [value]
            self.calls[callid] = [value]
        self.calls[callid] = call
        self.connections_update()
        self.data_update()
        self.UI_submit_setenabled()
        self.UI_call_set(callid, 0)

    def arg_set(self, callid, argid, value):
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
            self.UI_data_viz()
        elif isinstance(arg, signature.Scalar):
            call[argid] = self.range_parse(value)
            self.UI_call_set(callid, argid)
        elif isinstance(arg, signature.Dim):
            # evaluate value
            call[argid] = self.range_parse(value)
            self.connections_apply(callid, argid)
            self.infer_lds()
            self.data_update()
            self.UI_calls_set(callid, argid)
            self.UI_data_viz()
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
                self.UI_call_set(callid, argid)
        elif isinstance(arg, (signature.Ld, signature.Inc)):
            call[argid] = self.range_parse(value)
            self.data_update()
            self.UI_calls_set(callid, argid)
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
            else:
                call[argid] = self.range_parse(value)
            self.UI_call_set(callid, argid)
        self.UI_submit_setenabled()

    # catch and handle data conflicts
    def data_override(self, callid, argid, value):
        thistype = self.calls[callid].sig[argid].__class__
        othertype = self.data[value]["type"]
        if thistype != othertype:
            self.UI_alert("Incompatible data types for %r: %r and %r" %
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
                       argid3 in self.connections[(callid, argid2)]):
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
        self.calls[callid][argid] = value
        self.connections_update()
        for callid2 in range(len(self.calls)):
            if callid2 != callid:
                self.connections_apply(callid2)
        self.connections_apply(callid)
        self.infer_lds()
        self.data_update()
        self.UI_calls_set()

    def data_override_cancel(self, callid, argid, value):
        self.UI_call_set(callid)

    def calls_checksanity(self):
        for call in self.calls:
            if call[0] not in self.sampler["kernels"]:
                return False
            if any(arg is None for arg in call):
                return False
        return True

    # submit
    def generate_cmds(self, ntrangeval=None):
        cmds = []

        def varname(name, outerval, rep, innerval):
            if name not in self.vary:
                return name
            parts = [name]
            if outerval is not None:
                parts.append(outerval)
            parts.append(rep)
            if innerval is not None:
                parts.append(innerval)
            return "_".join(map(str, parts))

        outervals = None,
        if self.userange["outer"] == "threads":
            outervals = ntrangeval,
        elif self.userange["outer"]:
            outervals = self.ranges[self.userange["outer"]]

        if len(self.counters):
            cmds.append(["########################################"])
            cmds.append(["# counters                             #"])
            cmds.append(["########################################"])
            cmds.append([])
            cmds.append(["set_counters"] + list(filter(None, self.counters)))
            cmds.append([])
            cmds.append([])

        if len(self.data):
            cmds.append(["########################################"])
            cmds.append(["# data                                 #"])
            cmds.append(["########################################"])
        cmdprefixes = {
            signature.Data: "",
            signature.iData: "i",
            signature.sData: "s",
            signature.dData: "d",
            signature.cData: "s",
            signature.zData: "z",
        }
        for name, data in self.data.iteritems():
            cmds.append([])
            cmds.append(["# %s" % name])
            cmdprefix = cmdprefixes[data["type"]]
            expr = data["comp"]
            if name not in self.vary:
                size = max(self.range_eval(expr, ntrangeval))
                cmds.append([cmdprefix + "malloc", name, size])
                continue
            # argument varies
            size = max(sum(self.range_eval_sum(expr, outerval))
                       for outerval in outervals) * (self.nrep + 1)
            cmds.append([cmdprefix + "malloc", name, size])
            for outerval in outervals:
                if self.userange["outer"] == "range":
                    if self.userange["inner"]:
                        cmds.append([])
                    cmds.append(["# %s = %d" % (self.rangevars["range"],
                                                outerval)])
                innervals = None,
                if self.userange["inner"]:
                    innerrange = self.ranges[self.userange["inner"]]
                    if self.userange["outer"]:
                        innerrange = innerrange(**{
                            self.rangevar[self.userange["outer"]]: outerval
                        })
                    innervals = list(innerrange)
                offset = 0
                for rep in range(self.nrep + 1):
                    if self.userange["inner"]:
                        cmds.append(["# repetition %d" % rep])
                    for innerval in innervals:
                        cmds.append([
                            cmdprefix + "offset", name, offset,
                            varname(name, outerval, rep, innerval)
                        ])
                        offset += next(self.range_eval(
                            expr, outerval, innerval
                        ))
        if len(self.data):
            cmds.append([])
            cmds.append([])

        # calls
        cmds.append(["########################################"])
        cmds.append(["# calls                                #"])
        cmds.append(["########################################"])
        for outerval in outervals:
            if self.userange["outer"] == "range":
                cmds.append([])
                cmds.append(["# %s = %d" % (self.rangevars["range"],
                                            outerval)])
            innervals = None,
            if self.userange["inner"]:
                innerrange = self.ranges[self.userange["inner"]]
                if self.userange["outer"]:
                    innerrange = innerrange(**{
                        self.rangevar[self.userange["outer"]]: outerval
                    })
                innervals = list(innerrange)
            for rep in range(self.nrep + 1):
                if self.userange["inner"]:
                    cmds.append([])
                    cmds.append(["# repetition %d" % rep])
                for innerval in innervals:
                    for call in self.calls:
                        if isinstance(call, signature.Call):
                            call = call.sig(*[
                                next(self.range_eval(val, outerval, innerval))
                                for val in call[1:]
                            ])
                            cmd = call.format_sampler()
                            for argid in call.sig.dataargs():
                                cmd[argid] = varname(
                                    cmd[argid], outerval, rep, innerval
                                )
                        else:
                            # call without proper signature
                            cmd = call[:]
                            minsig = self.sampler["kernels"][call[0]]
                            for argid, value in enumerate(call):
                                if argid == 0 or minsig[argid] == "char":
                                    # chars don't need further processing
                                    continue
                                if isinstance(value, str):
                                    if value[0] == "[" and value[-1] == "]":
                                        expr = self.range_parse(value[1:-1])
                                        if expr is not None:
                                            value = next(self.range_eval(
                                                expr, outerval, innerval
                                            ))
                                        call[argid] = "[" + str(value) + "]"
                                else:
                                    expr = self.range_parse(value)
                                    if expr is not None:
                                        value = next(self.range_eval(
                                            expr, outerval, innerval
                                        ))
                                        call[argid] = str(value)
                        cmds.append(cmd)
            cmds.append(["go"])

        return cmds

    def submit(self, filename):
        filebase = filename
        if filename[-5:] == ".smpl":
            filebase = filebase[:-5]
        scriptfile = filebase + ".script"
        smplfile = filebase + ".smpl"
        errfile = filebase + ".err"
        jobname = os.path.basename(filebase)

        header = self.sampler["backend_header"]
        prefix = self.sampler["backend_prefix"]
        suffix = self.sampler["backend_suffix"]
        footer = self.sampler["backend_footer"]

        # emptly output files
        open(smplfile, "w").close()
        open(errfile, "w").close()

        script = ""

        # header
        if header:
            script += header.format(nt=self.nt) + "\n"

        if self.useheader:
            script += self.header + "\n"

        # report header
        reportinfo = self.state.copy()
        sampler = self.sampler.copy()
        del sampler["kernels"]
        reportinfo.update({
            "sampler": sampler,
            "submittime": time.time(),
            "ncalls": (len(list(self.range_eval(0))) *
                       (self.nrep + 1) * len(self.calls))
        })
        script += "cat > %s <<REPORTINFO\n%s\nREPORTINFO\n" % (
            smplfile, repr(reportinfo)
        )

        # timing
        script += "date +%%s >> %s\n" % smplfile

        ntvals = self.nt,
        if self.userange["outer"] == "threads":
            ntvals = self.ranges["threads"]
        for ntval in ntvals:
            if self.userange["outer"] == "threads":
                callfile = filebase + ".%d.calls" % ntval
            else:
                callfile = filebase + ".calls"

            # generate commands file
            cmds = self.generate_cmds(ntval)
            with open(callfile, "w") as fout:
                for cmd in cmds:
                    print(*cmd, file=fout)

            # add script part
            if prefix:
                script += prefix.format(nt=ntval) + " "
            script += "%(x)s < %(i)s >> %(o)s 2>> %(e)s" % {
                "x": self.sampler["sampler"],  # executable
                "i": callfile,  # input
                "o": smplfile,  # output
                "e": errfile  # error
            }
            if suffix:
                script += " " + suffix.format(nt=ntval)
            script += "\n"

            # delete call file
            script += "rm %s\n" % callfile

        # timing
        script += "date +%%s >> %s\n" % smplfile

        # if empty, delete errfile
        script += "[ -s %(e)s ] || rm %(e)s" % {"e": errfile}

        # delete script file
        script += "\nrm " + scriptfile

        if footer:
            script += "\n" + footer.format(nt=self.nt)

        # write script file (dubug)
        with open(scriptfile, "w") as fout:
            fout.write(script)

        # submit
        backend = self.backends[self.sampler["backend"]]
        jobid = backend.submit(script, nt=self.nt, jobname=jobname)

        # track progress
        self.jobprogress_add(jobid, smplfile)
        self.UI_jobprogress_show()
        self.log("submitted %r to %r" % (jobname, self.sampler["backend"]))

    # jobprogress
    def jobprogress_add(self, jobid, filename):
        nlines = (len(list(self.range_eval(0))) *
                  (self.nrep + 1) * len(self.calls))
        self.jobprogress.append({
            "backend": self.sampler["backend"],
            "id": jobid,
            "filename": filename,
            "progress": -1,
            "progressend": nlines
        })

    def jobprogress_update(self):
        for job in self.jobprogress:
            if job:
                with open(job["filename"]) as fin:
                    job["progress"] = len(fin.readlines()) - 2

    # kernel documentation
    def docs_get(self, routine):
        if routine not in self.docs:
            try:
                filename = os.path.join(self.docspath, routine + ".pydoc")
                with open(filename) as fin:
                    self.docs[routine] = eval(fin.read(), {}, {})
                self.log("loaded documentation for %r" % routine)
            except:
                self.docs[routine] = None
        return self.docs[routine]

    # user interface
    def UI_init(self):
        raise Exception("GUI needs to be subclassed")

    def UI_setall(self):
        self.UI_sampler_set()
        self.UI_sampler_about_set()
        self.UI_nt_setmax()
        self.UI_nt_set()
        self.UI_nrep_set()
        self.UI_usepapi_setenabled()
        self.UI_usepapi_set()
        self.UI_showargs_set()
        self.UI_usevary_set()
        self.UI_counters_setvisible()
        self.UI_counters_setoptions()
        self.UI_counters_set()
        self.UI_useheader_set()
        self.UI_header_setvisible()
        self.UI_header_set()
        self.UI_useranges_set()
        self.UI_ranges_set()
        self.UI_calls_init()
        self.UI_submit_setenabled()

    # event handlers
    def UI_submit(self, filename):
        if (self.userange["inner"] or self.userange["outer"]) and \
                (not any(isinstance(arg, symbolic.Expression)
                         for call in self.calls for arg in call)):
            self.UI_dialog(
                "warning", "range not used",
                "ranges are enabled but unused in the calls", {
                    "Ok": (self.submit, (filename,)),
                    "Cancel": None
                })
        else:
            self.submit(filename)

    def UI_state_reset(self):
        self.state_reset()
        self.UI_setall()

    def UI_state_import(self, filename):
        self.state_load(filename)
        self.UI_setall()

    def UI_sampler_change(self, samplername):
        newsampler = self.samplers[samplername]
        missing = set(call[0] for call in self.calls
                      if call[0] in self.sampler["kernels"]
                      and call[0] not in newsampler["kernels"])
        if missing:
            self.UI_dialog(
                "warning", "unsupported kernels",
                "%r does not support %s\nCorresponding calls will be removed"
                % (samplername, ", ".join(map(repr, missing))), {
                    "Ok": (self.sampler_set, (samplername,)),
                    "Cancel": None
                }
            )
        else:
            self.sampler_set(samplername)

    def UI_nt_change(self, nt):
        self.nt = nt

    def UI_usepapi_change(self, state):
        self.usepapi = state
        self.UI_counters_setvisible()

    def UI_useheader_change(self, state):
        self.useheader = state
        self.UI_header_setvisible()

    def UI_showargs_change(self, name, state):
        self.showargs[name] = state
        self.UI_showargs_apply()

    def UI_usevary_change(self, state):
        self.usevary = state
        self.UI_usevary_apply()

    def UI_counters_change(self, counters):
        self.counters = counters

    def UI_header_change(self, header):
        self.header = header

    def UI_userange_change(self, rangetype, rangename):
        if self.userange[rangetype]:
            oldname = self.userange[rangetype]
            subst = {self.rangevars[oldname]: self.ranges[oldname].max()}
            # get rid of old range in variables
            for call in self.calls:
                for argid, arg in enumerate(call):
                    if isinstance(arg, symbolic.Expression):
                        call[argid] = arg(**subst)
            # get rid of old range in inner range
            if rangetype == "outer":
                for innername in self.rangetypes["inner"]:
                    self.ranges[innername] = self.ranges[innername](**subst)
            self.data_update()
            self.UI_calls_set()
        self.userange[rangetype] = rangename
        if rangename == "threads":
            self.ranges["threads"] = symbolic.Range((1, 1, self.nt))
        self.userange[rangetype] = rangename
        self.UI_useranges_set()

    def UI_rangevar_change(self, rangename, value):
        if not value:
            # TODO: notify user
            return
        subst = {self.rangevars[rangename]: symbolic.Symbol(value)}
        for call in self.calls:
            for argid, arg in enumerate(call):
                if isinstance(arg, symbolic.Expression):
                    call[argid] = arg.substitute(**subst)
        if rangename in self.rangetypes["outer"]:
            for innername in self.rangetypes["inner"]:
                self.ranges[innername] = self.ranges[innername](**subst)
        self.rangevars[rangename] = value
        self.data_update()
        self.UI_calls_set()

    def UI_range_change(self, rangename, value):
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
        if nrep:
            self.nrep = int(nrep)
        # TODO: else notify user

    def UI_call_add_click(self):
        self.calls.append([""])
        self.UI_call_add()
        self.UI_submit_setenabled()
        self.UI_arg_setfocus(len(self.calls) - 1, 0)

    def UI_call_remove(self, callid):
        del self.calls[callid]
        self.connections_update()
        self.UI_calls_init()
        self.UI_submit_setenabled()

    def UI_calls_reorder(self, order):
        self.calls = [self.calls[i] for i in order]
        self.connections_update()

    def UI_arg_change(self, callid, argid, value):
        if argid == 0:
            self.routine_set(callid, value)
        else:
            self.arg_set(callid, argid, value)

    def UI_vary_change(self, callid, argid, state):
        name = self.calls[callid][argid]
        if name is None:
            return
        if state:
            self.vary.add(name)
        else:
            self.vary.discard(name)
        self.UI_data_viz()

    def UI_jobkill(self, jobid):
        job = self.jobprogress[jobid]
        self.backends[job["backend"]].kill(job["id"])
        self.jobprogress[jobid] = None

    def UI_jobview(self, jobid):
        job = self.jobprogress[jobid]
        self.UI_viewer_load(job["filename"])
