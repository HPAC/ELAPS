#!/usr/bin/env python
from __future__ import division, print_function

import signature
import symbolic

import sys
import os


class GUI():
    def __init__(self):
        self.rootpath = ".."
        if os.path.split(os.getcwd())[1] == "src":
            self.rootpath = os.path.join("..", "..")

        self.samplers_init()
        self.signatures_init()
        self.state_init()
        self.UI_init()
        self.UI_setall()
        self.UI_start()

    def log(self, *args):
        print(*args)

    def alert(self, *args):
        print(*args, file=sys.stderr)

    def samplers_init(self):
        self.samplers = {}
        samplerpath = os.path.join(self.rootpath, "Sampler", "build")
        for path, dirs, files in os.walk(samplerpath, followlinks=True):
            if "info.py" in files and "sampler.x" in files:
                with open(os.path.join(path, "info.py")) as fin:
                    system = eval(fin.read())
                system["sampler"] = os.path.join(path, "sampler.x")
                self.samplers[system["name"]] = system
        self.log("loaded", len(self.samplers), "samplers")

    def signatures_init(self):
        self.signatures = {}
        signaturepath = os.path.join(self.rootpath, "GUI", "signatures")
        for path, dirs, files in os.walk(signaturepath, followlinks=True):
            for filename in files:
                if filename[0] == ".":
                    continue
                sig = signature.Signature(file=os.path.join(path, filename))
                self.signatures[str(sig[0])] = sig
        self.log("loaded", len(self.signatures), "signatures")

    def state_init(self):
        self.statefile = os.path.join(self.rootpath, "GUI", ".state.py")
        try:
            with open(self.statefile) as fin:
                self.state = eval(fin.read()) + 1
        except:
            sampler = self.samplers[min(self.samplers)]
            self.state = {
                "sampler": sampler["name"],
                "nt": 1,
                "nrep": 10,
                "usepapi": False,
                "useld": False,
                "usevary": False,
                "userange": False,
                "rangevar": "n",
                "range": (8, 32, 1000),
                "counters": sampler["papi_counters_max"] * [None],
                "samplename": "",
                "calls": [("",)],
                "data": {},
                "datascale": 100,
            }
            if "dgemm_" in sampler["kernels"]:
                self.state["calls"][0] = ("dgemm_", "N", "N", 1000, 1000, 1000,
                                          1, "A", 1000, "B", 1000, 1, "C",
                                          1000)
        calls = self.state["calls"]
        for callid, call in enumerate(calls):
            if call[0] in self.signatures:
                calls[callid] = self.signatures[call[0]](*call[1:])
            self.infer_data(callid)
        self.state_write()

    def state_write(self):
        callobjects = self.state["calls"]
        self.state["calls"] = map(list, self.state["calls"])
        with open(self.statefile, "w") as fout:
            try:
                import pprint
                print(pprint.pformat(self.state, 4), file=fout)
            except:
                print(repr(self.state), file=fout)
        self.state["calls"] = callobjects

    def get_infostr(self):
        sampler = self.samplers[self.state["sampler"]]
        info = "System:\t%s\n" % sampler["system_name"]
        if sampler["backend"] != "local":
            info += "  (via %s(\n" % sampler["backend"]
        info += "  %s\n" % sampler["cpu_model"]
        info += "  %.2f MHz\n" % (sampler["frequency"] / 1e6)
        info += "\nBLAS:\t%s\n" % sampler["blas_name"]
        return info

    def data_clean(self):
        needed = []
        for call in self.state["calls"]:
            if isinstance(call, signature.Call):
                for argid, arg in enumerate(call.sig):
                    if isinstance(arg, signature.Data) and call[argid]:
                        needed.append(call[argid])
        self.state["data"] = {k: v for k, v in self.state["data"].iteritems()
                              if k in needed}

    def data_maxdim(self):
        return max(max(data["dimmin"] + data["dimmax"])
                   for data in self.state["data"].itervalues())

    def infer_lds(self, callid):
        call = self.state["calls"][callid]
        call2 = call.copy()
        assert isinstance(call, signature.Call)
        for i, arg in enumerate(call2.sig):
            if isinstance(arg, (signature.Ld, signature.Inc)):
                call2[i] = None
        call2.complete()
        for i, arg in enumerate(call2.sig):
            if isinstance(arg, (signature.Ld, signature.Inc)):
                if self.state["useld"] and not isinstance(call2[i],
                                                          symbolc.Expression):
                    call[i] = max(call2[i], call[i])
                else:
                    call[i] = call2[i]

    def infer_data(self, callid):
        call = self.state["calls"][callid]
        call2 = call.copy()
        assert isinstance(call, signature.Call)
        for i, arg in enumerate(call2.sig):
            if isinstance(arg, (signature.Dim, signature.Ld, signature.Inc)):
                call2[i] = symbolic.Symbol("." + arg.name)
            if isinstance(arg, signature.Data):
                call2[i] = None
        call2.complete()
        argdict = {"." + key: val for key, val in call.argdict().iteritems()}
        for i, arg in enumerate(call2.sig):
            if not (isinstance(arg, signature.Data) and call[i]):
                continue
            size = call2[i].substitute(**argdict)
            if isinstance(size, symbolic.Prod):
                size = size[1:]
            else:
                size = (size,)
            userange = self.state["userange"]
            if userange:
                rangevar = self.state["rangevar"]
                rangemin = self.state["range"][0]
                rangemax = self.state["range"][2]
            dimmin = []
            dimmax = []
            for dim in size:
                if userange and isinstance(dim, symbolic.Expression):
                    dmin = dim(**{rangevar: rangemin})
                    dmax = dim(**{rangevar: rangemax})
                else:
                    dmin = dmax = dim
                try:
                    dimmin.append(int(dmin))
                except:
                    dimmin.append(None)
                try:
                    dimmax.append(int(dmax))
                except:
                    dimmax.append(None)
            self.state["data"][call[i]] = {
                "dimmin": dimmin,
                "dimmax": dimmax
            }

    def sampler_set(self, samplername):
        self.state["sampler"] = samplername
        sampler = self.samplers[samplername]
        self.state["nt"] = max(self.state["nt"], sampler["nt_max"])

        # update countes (kill unavailable, adjust length)
        papi_counters_max = sampler["papi_counters_max"]
        self.state["usepapi"] &= papi_counters_max > 0
        counters = []
        for counter in self.state["counters"]:
            if counter in sampler["papi_counters_avail"]:
                counters.append(counter)
        counters = counternames[:papi_counters_max]
        counters += (papi_counters_max - len(counternames)) * [None]
        self.state["counters"] = counternames

        # remove unavailable calls
        # TODO

        # update UI
        self.UI_nt_setmax()
        self.UI_nt_set()
        self.UI_usepapi_setenabled()
        self.UI_usepapi_set()
        self.UI_counters_setoptions()
        self.UI_counters_set()
        self.UI_calls_set()

    def routine_set(self, callid, value):
        if value in self.signatures:
            # TODO: default argument values
            call = self.signatures[value]()
            for i, arg in enumerate(call.sig):
                if isinstance(arg, signature.Dim):
                    call[i] = 1000
                elif isinstance(arg, signature.Data):
                    for name in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        if name not in self.state["data"]:
                            call[i] = name
                            self.state["data"][name] = None
                            break
            self.state["calls"][callid] = call
            self.infer_lds(callid)
            self.infer_data(callid)
        else:
            self.state["calls"][callid] = [value]
        self.UI_call_set(callid, 0)
        self.state_write()

    def arg_set(self, callid, argid, value):
        call = self.state["calls"][callid]
        arg = call.sig[argid]
        if isinstance(arg, signature.Flag):
            call[argid] = value
        elif isinstance(arg, signature.Scalar):
            if isinstance(arg, (signature.sScalar, signature.dScalar)):
                try:
                    call[argid] = float(value)
                except:
                    call[argid] = None
            else:
                try:
                    call[argid] = complex(value)
                except:
                    call[argid] = None
        elif isinstance(arg, signature.Dim):
            try:
                if self.state["userange"]:
                    var = self.state["rangevar"]
                    value = eval(value, {}, {var: symbolic.Symbol(var)})
                else:
                    value = int(eval(value, {}, {}))
            except:
                value = None
            call[argid] = value
            self.infer_lds(callid)
            self.infer_data(callid)
            self.UI_call_set(callid, argid)
            self.UI_data_set()
        elif isinstance(arg, signature.Data):
            if value in self.data:
                self.data_override(callid, argid, value)
            else:
                call[argid] = value
                self.infer_data(callid)
                self.data_clean()
                # self.UI_call_set(callid, argid)
        elif isinstance(arg, (signature.Ld, signature.Inc)):
            # TODO: rangevar + error checking + conflict checking
            call[argid] = int(value) if value else None
            self.infer_data(callid)
        self.state_write()

    def data_override(self, callid, argid, value):
        call = self.state["calls"][callid]
        oldvalue = call[argid]
        olddata = self.state["data"][value].copy()
        call[argid] = value
        self.infer_data(callid)
        if self.state["data"][value] != olddata:
            call[argid] = oldvalue
            self.state["Data"][value] = olddata
            self.UI_choose_data_override(callid, argid, value)
        else:
            # self.UI_call_set(callid, argid)
            pass

    def data_override_this(self, callid, argid, value):
        pass

    def data_override_other(self, callid, argid, value):
        pass

    def data_override_cancel(self, callid, argid, value):
        self.UI_call_set(callid, argid)

    def UI_init(self):
        self.alert("GUI_ needs to be subclassed")

    def UI_setall(self):
        self.UI_sampler_set()
        self.UI_nt_setmax()
        self.UI_nt_set()
        self.UI_nrep_set()
        self.UI_info_set(self.get_infostr())
        self.UI_usepapi_setenabled()
        self.UI_usepapi_set()
        self.UI_useld_set()
        self.UI_usevary_set()
        self.UI_userange_set()
        self.UI_counters_setvisible()
        self.UI_counters_setoptions()
        self.UI_counters_set()
        self.UI_range_setvisible()
        self.UI_rangevar_set()
        self.UI_range_set()
        self.UI_calls_set()
        self.UI_samplename_set()

    # event handlers
    def UI_sampler_change(self, samplername):
        # TODO: check for missing call routine conflicts
        self.sampler_set(samplername)

    def UI_nt_change(self, nt):
        self.state["nt"] = nt
        self.state_write()

    def UI_nrep_change(self, nrep):
        self.state["nrep"] = nrep
        self.state_write()

    def UI_usepapi_change(self, state):
        self.state["usepapi"] = state
        self.UI_counters_setvisible()
        self.state_write()

    def UI_useld_change(self, state):
        self.state["useld"] = state
        self.UI_useld_apply()
        self.state_write()

    def UI_usevary_change(self, state):
        self.state["usevary"] = state
        self.state_write()
        # TODO

    def UI_counters_change(self, counters):
        self.state["counters"] = counters
        self.state_write()

    def UI_userange_change(self, state):
        self.state["userange"] = state
        self.UI_range_setvisible()
        self.state_write()

    def UI_rangevar_change(self, varname):
        self.state["rangevar"] = varname
        self.state_write()

    def UI_range_change(self, range):
        self.state["range"] = range
        self.state_write()

    def UI_call_add(self):
        self.state["calls"].append([""])
        self.UI_calls_set()
        self.state_write()

    def UI_call_remove(self, callid):
        del self.state["calls"][callid]
        self.UI_calls_set()
        self.state_write()

    def UI_call_moveup(self, callid):
        calls = self.state["calls"]
        calls[callid], calls[callid - 1] = calls[callid - 1], calls[callid]
        self.UI_calls_set()
        self.state_write()

    def UI_call_movedown(self, callid):
        calls = self.state["calls"]
        calls[callid + 1], calls[callid] = calls[callid], calls[callid + 1]
        self.UI_calls_set()
        self.state_write()

    def UI_arg_change(self, callid, argid, value):
        if argid == 0:
            self.routine_set(callid, value)
        else:
            self.arg_set(callid, argid, value)

    def UI_samplename_change(self, samplename):
        self.state["samplename"] = samplename
        self.state_write()

    def UI_submit_click(self):
        self.alert("submit_click")
