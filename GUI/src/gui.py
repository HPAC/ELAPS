#!/usr/bin/env python
from __future__ import division, print_function

import signature
import symbolic

import sys
import os
import imp
import pprint
import time
import subprocess
from collections import defaultdict
from __builtin__ import intern  # fix for pyflake error


class GUI(object):
    requiredbuildversion = 1422278229
    requiredstateversion = 1422278229
    state = {}

    def __init__(self, loadstate=True):
        thispath = os.path.dirname(__file__)
        if thispath not in sys.path:
            sys.path.append(thispath)
        self.rootpath = os.path.abspath(os.path.join(thispath, "..", ".."))
        self.reportpath = os.path.join(self.rootpath, "GUI", "reports")
        self.statefile = os.path.join(self.rootpath, "GUI", ".guistate.py")

        self.backends_init()
        self.samplers_init()
        self.signatures_init()
        self.state_init(loadstate)
        self.jobprogress_init()
        self.UI_init()
        self.UI_setall()

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

    def state_init(self, load=True):
        sampler = self.samplers[min(self.samplers)]
        state = {
            "statetime": time.time(),
            "stateverions": self.requiredstateversion,
            "samplername": sampler["name"],
            "nt": 1,
            "usentrange": False,
            "userange": True,
            "usesumrange": False,
            "usepapi": False,
            "usevary": False,
            "showargs": {
                "flags": True,
                "scalars": True,
                "lds": False,
                "infos": False
            },
            "counters": sampler["papi_counters_max"] * [None],
            "ntrange": (1, 1, 1),
            "rangevar": "n",
            "range": (8, 32, 1000),
            "nrep": 10,
            "sumrangevar": "m",
            "sumrange": (1, 1, 10),
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
        if load:
            try:
                with open(self.statefile) as fin:
                    oldstate = eval(fin.read(), symbolic.__dict__)
                if oldstate["stateversion"] > self.requiredstateversion:
                    state = oldstate
                    self.log("loaded state from",
                             os.path.relpath(self.statefile))
            except:
                pass
        self.state_fromflat(state)
        self.connections_update()
        self.data_update()
        self.state_write()

    def jobprogress_init(self):
        self.jobprogress = []

    # state routines
    def state_toflat(self):
        state = self.state.copy()
        state["calls"] = tuple(map(tuple, self.calls))
        state["counters"] = tuple(state["counters"])
        return state

    def state_fromflat(self, state):
        state = state.copy()
        calls = list(map(list, state["calls"]))
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
        self.state = state

    def state_write(self):
        with open(self.statefile, "w") as fout:
            print(pprint.pformat(self.state_toflat(), 4), file=fout)

    # info string
    def get_infostr(self):
        sampler = self.sampler
        info = "System:\t%s\n" % sampler["system_name"]
        info += "BLAS:\t%s\n" % sampler["blas_name"]
        if sampler["backend"] != "local":
            info += "  (via %s)\n" % sampler["backend"]
        info += "\n"
        info += "CPU:\t%s\n" % sampler["cpu_model"]
        info += "Mhz:\t%.2f\n" % (sampler["frequency"] / 1e6)
        info += "Cores:\t%d\n" % sampler["nt_max"]
        info += "Gflops/s:\t%.2f (peak)" % (
            sampler["dflops/cycle"] * sampler["frequency"] * sampler["nt_max"]
            / 1e9
        )
        return info

    # range routines
    def range_get(self):
        if self.userange:
            lower, step, upper = self.range
            if lower <= upper:
                return range(lower, upper + 1, step)
            else:
                return [lower]
        elif self.usentrange:
            lower, step, upper = self.ntrange
            if lower <= upper:
                return range(lower, upper + 1, step)
            else:
                return [lower]
        else:
            return [None]

    def sumrange_get(self, rangeval=None):
        if not self.usesumrange:
            return [None]
        lower, step, upper = self.sumrange
        if rangeval is not None:
            lower = self.range_eval(lower, rangeval, dosumrange=False)
            step = self.range_eval(step, rangeval, dosumrange=False)
            upper = self.range_eval(upper, rangeval, dosumrange=False)
        if lower <= upper:
            return range(lower, upper + 1, step)
        else:
            return [lower]

    def range_eval(self, expr, rangeval=None, sumrangeval=None,
                   dorange=True, dosumrange=True):
        if rangeval is None and dorange:
            if self.userange or self.usentrange:
                return [
                    self.range_eval(expr, val, sumrangeval, dorange,
                                    dosumrange)
                    for val in self.range_get()
                ]
            else:
                return [
                    self.range_eval(expr, None, sumrangeval, False, dosumrange)
                ]
        if sumrangeval is None and dosumrange:
            if self.usesumrange:
                return [
                    self.range_eval(expr, rangeval, val, dorange, dosumrange)
                    for val in self.sumrange_get(rangeval)
                ]
            else:
                return [
                    self.range_eval(expr, rangeval, None, dorange, False)
                ]
        symdict = {}
        if dorange:
            if self.usentrange:
                symdict["nt"] = rangeval
            elif self.userange:
                symdict[self.rangevar] = rangeval
        if dosumrange and self.usesumrange:
            symdict[self.sumrangevar] = sumrangeval
        if isinstance(expr, symbolic.Expression):
            return expr(**symdict)
        return expr

    def range_parse(self, text, dorange=True, dosumrange=True):
        try:
            symbols = {}
            if self.usentrange and dorange:
                symbols["nt"] = symbolic.Symbol("nt")
            if self.userange and dorange:
                symbols[self.rangevar] = symbolic.Symbol(self.rangevar)
            if self.usesumrange and dosumrange:
                symbols[self.sumrangevar] = symbolic.Symbol(self.sumrangevar)
            return eval(text, {}, symbols)
        except:
            return None

    # simple data operations
    def data_maxdim(self):
        result = 0
        for data in self.data.itervalues():
            sym = data["sym"]
            if isinstance(sym, symbolic.Prod):
                datamax = max(max(sum(self.range_eval(val), []))
                              for val in sym[1:])
            else:
                datamax = max(sum(self.range_eval(sym), []))
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

        # update UI
        self.UI_nt_setmax()
        self.UI_nt_set()
        self.UI_usepapi_setenabled()
        self.UI_usepapi_set()
        self.UI_counters_setoptions()
        self.UI_counters_set()
        self.UI_calls_init()

    def rangevar_set(self, varname):
        if varname:
            subst = {self.rangevar: symbolic.Symbol(varname)}
            for callid, call in enumerate(self.calls):
                for argid, arg in enumerate(call):
                    if isinstance(arg, symbolic.Expression):
                        call[argid] = arg.substitute(**subst)
            self.rangevar = varname
            self.data_update()
            self.UI_calls_set()

    def sumrangevar_set(self, varname):
        if varname:
            subst = {self.sumrangevar: symbolic.Symbol(varname)}
            for callid, call in enumerate(self.calls):
                for argid, arg in enumerate(call):
                    if isinstance(arg, symbolic.Expression):
                        call[argid] = arg.substitute(**subst)
            self.sumrangevar = varname
            self.data_update()
            self.UI_calls_set()

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
        self.state_write()
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
            self.state_write()
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
            self.state_write()
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
                self.state_write()
                self.UI_call_set(callid, argid)
        elif isinstance(arg, (signature.Ld, signature.Inc)):
            call[argid] = self.range_parse(value)
            self.data_update()
            self.state_write()
            self.UI_calls_set(callid, argid)
        # calls without proper signatures
        else:
            if value is None:
                call[callid] = None
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
            self.state_write()
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
        self.state_write()
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

        rangevals = [0]
        if self.usentrange:
            rangevals = [ntrangeval]
        if self.userange:
            rangevals = self.range_get()

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
            if name not in self.vary:
                if self.usentrange:
                    size = max(self.range_eval(data["comp"], ntrangeval))
                else:
                    size = max(sum(self.range_eval(data["comp"]), []))
                cmds.append([cmdprefix + "malloc", name, size])
                continue
            # argument varies
            size = (self.nrep + 1)
            if self.usentrange:
                size *= sum(self.range_eval(data["comp"], ntrangeval))
            else:
                size *= max(map(sum, self.range_eval(data["comp"])))
            cmds.append([cmdprefix + "malloc", name, size])
            for rangeval in rangevals:
                if self.userange:
                    if self.usesumrange:
                        cmds.append([])
                    cmds.append(["# %s = %d" % (self.rangevar, rangeval)])
                sumrangevals = [0]
                if self.usesumrange:
                    sumrangevals = self.sumrange_get(rangeval)
                offset = 0
                for rep in range(self.nrep + 1):
                    if self.usesumrange:
                        cmds.append(["# repetition %d" % rep])
                    for sumrangeval in sumrangevals:
                        cmds.append([
                            cmdprefix + "offset", name, offset,
                            "%s_%d_%d_%d" % (name, rangeval, rep, sumrangeval)
                        ])
                        offset += self.range_eval(data["comp"], rangeval,
                                                  sumrangeval)
        if len(self.data):
            cmds.append([])
            cmds.append([])

        # calls
        cmds.append(["########################################"])
        cmds.append(["# calls                                #"])
        cmds.append(["########################################"])
        for rangeval in rangevals:
            if self.userange:
                cmds.append([])
                cmds.append(["# %s = %d" % (self.rangevar, rangeval)])
            sumrangevals = [0]
            if self.usesumrange:
                sumrangevals = self.sumrange_get(rangeval)
            for rep in range(self.nrep + 1):
                if self.usesumrange:
                    cmds.append([])
                    cmds.append(["# repetition %d" % rep])
                for sumrangeval in sumrangevals:
                    for call in self.calls:
                        if isinstance(call, signature.Call):
                            call = call.sig(*[
                                self.range_eval(value, rangeval, sumrangeval)
                                for value in call[1:]
                            ])
                            cmd = call.format_sampler()
                            for argid in call.sig.dataargs():
                                name = call[argid]
                                if name in self.vary:
                                    cmd[argid] = "%s_%d_%d_%d" % (
                                        name, rangeval, rep, sumrangeval
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
                                        parsed = self.range_parse(value[1:-1])
                                        if parsed is not None:
                                            value = self.range_eval(
                                                parsed, rangeval, sumrangeval
                                            )
                                        call[argid] = "[" + str(value) + "]"
                                else:
                                    parsed = self.range_parse(value)
                                    if parsed is not None:
                                        value = self.range_eval(
                                            parsed, rangeval, sumrangeval
                                        )
                                        call[argid] = str(value)
                        cmds.append(cmd)
            cmds.append(["go"])

        return cmds

    def submit(self, filename):
        filebase = filename
        if filename[-5:] == ".smpl":
            filebase = filebase[:-5]
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

        # report header
        reportinfo = self.state.copy()
        sampler = self.sampler.copy()
        reportinfo["counters"] = tuple(filter(None, reportinfo["counters"]))
        del sampler["kernels"]
        reportinfo.update({
            "sampler": sampler,
            "submittime": time.time()
        })
        script += "cat > %s <<REPORTINFO\n%s\nREPORTINFO\n" % (
            smplfile, repr(reportinfo)
        )

        # timing
        script += "date +%%s >> %s\n" % smplfile

        ntrangevals = [self.nt]
        if self.usentrange:
            ntrangevals = self.range_get()
        for ntrangeval in ntrangevals:
            if self.usentrange:
                callfile = filebase + ".%d.calls" % ntrangeval
            else:
                callfile = filebase + ".calls"

            # generate commands file
            cmds = self.generate_cmds(ntrangeval)
            with open(callfile, "w") as fout:
                for cmd in cmds:
                    print(*cmd, file=fout)

            # add script part
            if prefix:
                script += prefix.format(nt=ntrangeval) + " "
            script += "%(x)s < %(i)s >> %(o)s 2>> %(e)s" % {
                "x": self.sampler["sampler"],  # executable
                "i": callfile,  # input
                "o": smplfile,  # output
                "e": errfile  # error
            }
            if suffix:
                script += " " + suffix.format(nt=ntrangeval)
            script += "\n"

        # timing
        script += "date +%%s >> %s\n" % smplfile

        # if empty, delete errfile
        script += "[ -s %(e)s ] || rm %(e)s" % {"e": errfile}

        if footer:
            script += "\n" + footer.format(nt=self.nt)

        # submit
        backend = self.backends[self.sampler["backend"]]
        jobid = backend.submit(script, nt=self.nt, jobname=jobname)

        # track progress
        self.jobprogress_add(jobid, smplfile)
        self.UI_jobprogress_show()
        self.log("submitted %r to %r" % (jobname, self.sampler["backend"]))

    # jobprogress
    def jobprogress_add(self, jobid, filename):
        nlines = len(sum(self.range_eval(0), []))
        nlines *= (self.nrep + 1) * len(self.calls)
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

    # user interface
    def UI_init(self):
        raise Exception("GUI needs to be subclassed")

    def UI_setall(self):
        self.UI_sampler_set()
        self.UI_nt_setmax()
        self.UI_nt_set()
        self.UI_nrep_set()
        self.UI_usepapi_setenabled()
        self.UI_usepapi_set()
        self.UI_showargs_set()
        self.UI_usevary_set()
        self.UI_userange_setenabled()
        self.UI_usentrange_set()
        self.UI_userange_set()
        self.UI_usesumrange_set()
        self.UI_counters_setvisible()
        self.UI_counters_setoptions()
        self.UI_counters_set()
        self.UI_usentrange_apply()
        self.UI_ntrange_set()
        self.UI_userange_apply()
        self.UI_rangevar_set()
        self.UI_range_set()
        self.UI_usesumrange_apply()
        self.UI_sumrangevar_set()
        self.UI_sumrange_set()
        self.UI_calls_init()
        self.UI_submit_setenabled()

    # event handlers
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
        self.state_write()

    def UI_usepapi_change(self, state):
        self.usepapi = state
        self.state_write()
        self.UI_counters_setvisible()

    def UI_showargs_change(self, name, state):
        self.showargs[name] = state
        self.state_write()
        self.UI_showargs_apply()

    def UI_usevary_change(self, state):
        self.usevary = state
        self.state_write()
        self.UI_usevary_apply()

    def UI_counters_change(self, counters):
        self.counters = counters
        self.state_write()

    def UI_usentrange_change(self, state):
        if state:
            self.ntrange = (self.nt, 1, self.nt)
            self.UI_ntrange_set()
        else:
            self.UI_nt_set()
            for call in self.calls:
                for argid, arg in enumerate(call):
                    call[argid] = self.range_eval(
                        arg, self.nt, dosumrange=False,
                    )
            self.data_update()
            self.UI_calls_set()
        self.usentrange = state
        self.state_write()
        self.UI_userange_setenabled()
        self.UI_usentrange_apply()

    def UI_ntrange_change(self, ntrange):
        lower, step, upper = ntrange
        if lower is None or lower <= 0:
            return
        if upper is None:
            return
        self.ntrange = ntrange
        self.nt = upper
        self.data_update()
        self.state_write()
        self.UI_data_viz()

    def UI_userange_change(self, state):
        if not state:
            for call in self.calls:
                for argid, arg in enumerate(call):
                    call[argid] = self.range_eval(
                        arg, self.range[-1], dosumrange=False
                    )
            self.data_update()
            self.UI_calls_set()
        self.userange = state
        self.state_write()
        self.UI_userange_setenabled()
        self.UI_userange_apply()

    def UI_rangevar_change(self, varname):
        self.rangevar_set(varname)
        self.state_write()

    def UI_range_change(self, range):
        lower, step, upper = range
        if lower is None:
            return
        if upper is None:
            return
        self.range = range
        self.data_update()
        self.state_write()
        self.UI_data_viz()

    def UI_usesumrange_change(self, state):
        if not state:
            for call in self.calls:
                print(call)
                for argid, arg in enumerate(call):
                    call[argid] = self.range_eval(
                        arg, sumrangeval=self.sumrange[-1], dorange=False
                    )
                print(call)
            self.data_update()
            self.UI_calls_set()
        self.usesumrange = state
        self.state_write()
        self.UI_usesumrange_apply()

    def UI_sumrangevar_change(self, varname):
        self.sumrangevar_set(varname)
        self.state_write()

    def UI_sumrange_change(self, sumrange):
        lower, step, upper = sumrange
        lower = self.range_parse(lower, dosumrange=False)
        step = self.range_parse(step, dosumrange=False)
        upper = self.range_parse(upper, dosumrange=False)
        if lower is None:
            return
        if step is None:
            step = 1
        if upper is None:
            return
        self.sumrange = (lower, step, upper)
        self.data_update()
        self.state_write()
        self.UI_data_viz()

    def UI_nrep_change(self, nrep):
        self.nrep = nrep
        self.state_write()

    def UI_submit(self, filename):
        msg = None
        if not any(isinstance(arg, symbolic.Expression)
                   for call in self.calls for arg in call):
            if self.userange:
                if self.usesumrange:
                    msg = ("Range and sum over are"
                           "but %r and %r are not used in any call")
                    msg %= (self.rangevar, self.sumrangevar)
                else:
                    msg = "Range is enabled but %r is not used in any call"
                    msg %= self.rangevar
            elif self.usesumrange:
                msg = "Sum over is enabled but %r is not used in any call"
                msg %= self.sumrangevar
        if msg:
            self.UI_dialog(
                "warning", "range not used", msg, {
                    "Ok": (self.submit, (filename,)),
                    "Cancel": None
                })
        else:
            self.submit(filename)

    def UI_call_add(self):
        self.calls.append([""])
        self.state_write()
        self.UI_calls_init()
        self.UI_submit_setenabled()

    def UI_call_remove(self, callid):
        del self.calls[callid]
        self.connections_update()
        self.state_write()
        self.UI_calls_init()
        self.UI_submit_setenabled()

    def UI_call_moveup(self, callid):
        calls = self.calls
        calls[callid], calls[callid - 1] = calls[callid - 1], calls[callid]
        self.connections_update()
        self.state_write()
        self.UI_calls_init()

    def UI_call_movedown(self, callid):
        calls = self.calls
        calls[callid + 1], calls[callid] = calls[callid], calls[callid + 1]
        self.connections_update()
        self.state_write()
        self.UI_calls_init()

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
        self.state_write()
        self.UI_data_viz()

    def UI_jobkill(self, jobid):
        job = self.jobprogress[jobid]
        self.backends[job["backend"]].kill(job["id"])
        self.jobprogress[jobid] = None

    def UI_jobview(self, jobid):
        job = self.jobprogress[jobid]
        viewerpath = os.path.join(self.rootpath, "GUI", "Viewer.py")
        subprocess.Popen([viewerpath, job["filename"]])
