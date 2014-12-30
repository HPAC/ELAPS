#!/usr/bin/env python
from __future__ import division, print_function

import signature
import symbolic

import sys
import os
from copy import deepcopy


class GUI(object):
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

    # state access attributes
    @property
    def calls(self):
        return self.state["calls"]

    @calls.setter
    def calls(self, value):
        self.state["calls"] = value

    @property
    def data(self):
        return self.state["data"]

    @data.setter
    def data(self, value):
        self.state["data"] = value

    # utility
    def log(self, *args):
        print(*args)

    def alert(self, *args):
        print(*args, file=sys.stderr)

    # initializers
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
                self.calls[0] = ("dgemm_", "N", "N", 1000, 1000, 1000,
                                 1, "A", 1000, "B", 1000, 1, "C", 1000)
        for callid, call in enumerate(self.calls):
            if call[0] in self.signatures:
                self.calls[callid] = self.signatures[call[0]](*call[1:])
        self.data = self.infer_alldata(self.calls)
        self.state_write()

    # utility type routines
    def state_write(self):
        callobjects = self.calls
        self.calls = map(list, self.calls)
        with open(self.statefile, "w") as fout:
            try:
                import pprint
                print(pprint.pformat(self.state, 4), file=fout)
            except:
                print(repr(self.state), file=fout)
        self.calls = callobjects

    def get_infostr(self):
        sampler = self.samplers[self.state["sampler"]]
        info = "System:\t%s\n" % sampler["system_name"]
        if sampler["backend"] != "local":
            info += "  (via %s(\n" % sampler["backend"]
        info += "  %s\n" % sampler["cpu_model"]
        info += "  %.2f MHz\n" % (sampler["frequency"] / 1e6)
        info += "\nBLAS:\t%s\n" % sampler["blas_name"]
        return info

    # simple data operations
    def data_clean(self):
        needed = []
        for call in self.calls:
            if isinstance(call, signature.Call):
                for argid, arg in enumerate(call.sig):
                    if isinstance(arg, signature.Data) and call[argid]:
                        needed.append(call[argid])
        self.data = {k: v for k, v in self.data.iteritems() if k in needed}

    def data_maxdim(self):
        return max(max(data["dimmin"] + data["dimmax"])
                   for data in self.data.itervalues())

    # inference system
    def infer_lds(self, call):
        # make sure we don't alter the input
        call = deepcopy(call)
        call2 = deepcopy(call)
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
        return call

    def infer_data(self, call, argid=None):
        self.log("infer_data", call, argid)
        assert isinstance(call, signature.Call)
        # make sure we don't alter the input
        call = deepcopy(call)
        symcall = deepcopy(call)
        for i, arg in enumerate(symcall.sig):
            if isinstance(arg, (signature.Dim, signature.Ld, signature.Inc)):
                symcall[i] = symbolic.Symbol("." + arg.name)
            if isinstance(arg, signature.Data):
                symcall[i] = None
        symcall.complete()
        argdict = {"." + key: val for key, val in call.argdict().iteritems()}
        data = {}
        for i, arg in enumerate(symcall.sig):
            if not (isinstance(arg, signature.Data) and call[i]):
                continue
            if argid is not None and i != argid:
                continue
            size = symcall[i].substitute(**argdict)
            if isinstance(size, symbolic.Prod):
                size = size[1:]
            else:
                size = [size]
            # TODO: move dimmin dimmax away from here
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
            data[call[i]] = {
                "dimmin": dimmin,
                "dimmax": dimmax,
                "dim": size
            }
        return data

    def infer_alldata(self, calls):
        self.log("infer_alldata", map(str, calls))
        data = {}
        for call in calls:
            data.update(self.infer_data(call))
        return data

    def infer_dims(self, call, argid, data=None):
        assert isinstance(call, signature.Call)
        self.log("infer_dims", call, argid)
        if data is None:
            data = self.data
        # make sure we don't alter the input
        call = deepcopy(call)
        data = data[call[argid]]
        symcall = deepcopy(call)
        for i, arg in enumerate(call.sig):
            if isinstance(arg, signature.Dim):
                symcall[i] = symbolic.Symbol("." + arg.name)
            if isinstance(arg, (signature.Data, signature.Ld, signature.Inc)):
                symcall[i] = None
        symcall.complete()
        symdim = symcall[argid]
        if isinstance(symdim, symbolic.Prod):
            symdim = symdim[1:]
        else:
            symdim = [symdim]
        if len(symdim) != len(data["dim"]):
            self.alert("data dimensionality mismatch:", call[argid])
            self.alert(symdim, data["dim"])
            return
        for symbol, dim in zip(symdim, data["dim"]):
            setattr(call, symbol.name[1:], dim)
        return call

    def infer_call(self, call, argid=None, data=None):
        assert isinstance(call, signature.Call)
        self.log("infer_call", call, argid)
        if data is None:
            data = self.data
        # make sure we don't alter the input
        call = deepcopy(call)
        data = deepcopy(data)
        changed = []
        if argid:
            if isinstance(call.sig[argid], signature.Data):
                call = self.infer_dims(call, argid, data)
            else:
                changed.append(argid)
        call = self.infer_lds(call)
        dataargids = call.sig.dataargs()
        if len(dataargids) == len(set(call[argid] for argid in dataargids)):
            return call
        hashes = []
        newhash = hash(tuple(call))
        while newhash not in hashes:
            hashes.append(newhash)
            for dargid in dataargids():
                newdata = self.infer_data(call, dargid)
                if newdata[call[dargid]] == data[call[dargid]]:
                    continue
                data.update(self.infer_data(call, dargid))
                # data changed
                for dargid2 in dataargids:
                    # check for occurence of the same data
                    if dargid == dargid2 or call[dargid] != call[dargid2]:
                        continue
                    tmpcall = self.infer_dims(call, dargid2, data)
                    for argid, val in enumerate(tmpcall):
                        if val == call[argid] or argid in changed:
                            # arg didn't change or already changed before
                            continue
                        # arg changed now
                        call[argid] = val
                        changed.append(argid)
                call = self.infer_lds(call)
            newhash = hash(tuple(call))
        return call

    def infer_calls(self, calls, callid, argid=None, data=None):
        self.log("infer_calls", map(str, calls), callid, argid)
        if data is None:
            data = self.data
        # make sure we don't alter the inputs
        calls = deepcopy(calls)
        data = deepcopy(data)
        changedargs = []
        if argid:
            # infer calls[callid] and set up changedargs
            changedargs.append((callid, argid))
            call = calls[callid]
            newcall = self.infer_call(call, argid, data)
            for argid, val in enumerate(newcall):
                if val != call[argid]:
                    call[argid] = val
                    changedargs.append((callid, argid))
        if len(calls) == 1:
            return calls
        changedcalls = [callid]
        hashes = []
        newhash = hash(tuple(map(tuple, calls) + changedcalls))
        if newhash not in hashes and len(changedcalls):
            hashes.append(newhash)
            callid = changedcalls.pop(0)
            newdata = self.infer_data(calls[callid])
            changeddata = [val for val in newdata if newdata[val] != data[val]]
            data.update(newdata)
            for callid2, call in enumerate(calls):
                if callid == callid2:
                    continue
                for argid in call.sig.dataargs():
                    if call[argid] not in changeddata:
                        continue
                    tmpcall = self.infer_call(call, argid, data)
                    for argid2, val in enumerate(tmpcall):
                        if val == call[argid2]:
                            # arg didn't change
                            continue
                        if (callid2, argid2) in changedargs:
                            # arg may only change once
                            continue
                        # argument changed now
                        call[argid2] = val
                        changedargs.append((callid2, argid2))
                        if callid2 not in changedcalls:
                            changedcalls.append(callid2)
            newhash = hash(tuple(map(tuple, calls) + changedcalls))
        return calls

    # treat changes for the calls
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
                        if name not in self.data:
                            call[i] = name
                            self.data[name] = None
                            break
            self.calls[callid] = self.infer_lds(call)
            self.data.update(self.infer_data(call))
        else:
            self.calls[callid] = [value]
        self.UI_call_set(callid, 0)
        self.state_write()

    def arg_set(self, callid, argid, value):
        call = self.calls[callid]
        arg = call.sig[argid]
        if isinstance(arg, signature.Flag):
            call[argid] = value
            self.calls = self.infer_call(self.calls)
            self.UI_call_set(callid, argid)
            self.UI_data_set()  # data viz scale may have changed anywhere
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
            self.calls = self.infer_calls(self.calls, callid, argid)
            self.data = self.infer_alldata(self.calls)
            for callid2 in range(len(self.calls)):
                self.UI_call_set(callid2, argid if callid2 == callid else None)
            self.UI_data_set()  # data viz scale may have changed anywhere
        elif isinstance(arg, signature.Data):
            if value in self.data:
                # resolve potential conflicts
                self.data_override(callid, argid, value)
            else:
                call[argid] = value
                self.data.update(self.infer_data(call))
                self.data_clean()
                self.UI_call_set(callid, argid)
        elif isinstance(arg, (signature.Ld, signature.Inc)):
            # TODO: proper ld treatment
            call[argid] = int(value) if value else None
            self.data.update(self.infer_data(call))
        self.state_write()

    # catch and handle data conflicts
    def data_override(self, callid, argid, value):
        call = deepcopy(self.calls[callid])
        call[argid] = value
        newdata = self.infer_data(call, argid)
        if self.data[value] != newdata[value]:
            self.UI_choose_data_override(callid, argid, value)
        else:
            # no conflict
            self.calls[callid][argid] = value

    def data_override_this(self, callid, argid, value):
        self.calls[callid][argid] = value
        self.calls = self.infer_call(self.calls, callid, argid)
        self.data = self.infer_alldata(self.calls)
        for callid2 in range(len(self.calls)):
            if callid2 == callid:
                self.UI_call_set(callid, argid)
            else:
                self.UI_call_set(callid)

    def data_override_other(self, callid, argid, value):
        self.calls[callid][argid] = value
        self.calls = self.infer_call(self.calls, callid)
        self.data = self.infer_alldata(self.calls)
        for callid2 in range(len(self.calls)):
            if callid2 == callid:
                self.UI_call_set(callid, argid)
            else:
                self.UI_call_set(callid)

    def data_override_cancel(self, callid, argid, value):
        self.UI_call_set(callid)

    # user interface
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
        self.calls.append([""])
        self.UI_calls_set()
        self.state_write()

    def UI_call_remove(self, callid):
        del self.calls[callid]
        self.UI_calls_set()
        self.state_write()

    def UI_call_moveup(self, callid):
        calls = self.calls
        calls[callid], calls[callid - 1] = calls[callid - 1], calls[callid]
        self.UI_calls_set()
        self.state_write()

    def UI_call_movedown(self, callid):
        calls = self.calls
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
