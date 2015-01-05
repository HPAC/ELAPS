#!/usr/bin/env python
from __future__ import division, print_function

import signature
import symbolic

import sys
import os
import imp
import pprint
from collections import defaultdict


class GUI(object):
    state = {}

    def __init__(self):
        self.rootpath = ".."
        if os.path.split(os.getcwd())[1] == "src":
            self.rootpath = os.path.join("..", "..")

        self.backends_init()
        self.samplers_init()
        self.signatures_init()
        self.state_init()
        self.UI_init()
        self.UI_setall()
        self.UI_start()

    # state access attributes
    def __getattr__(self, name):
        if name in self.__dict__["state"]:
            return self.__dict__["state"][name]
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))

    def __setattr__(self, name, value):
        if name in self.state:
            self.state[name] = value
        else:
            super(GUI, self).__setattr__(name, value)

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
            self.backends[name] = getattr(module, name)()
        self.log("loaded", len(self.backends), "backends:",
                 *sorted(self.backends))

    def samplers_init(self):
        self.samplers = {}
        samplerpath = os.path.join(self.rootpath, "Sampler", "build")
        for path, dirs, files in os.walk(samplerpath, followlinks=True):
            if "info.py" in files and "sampler.x" in files:
                with open(os.path.join(path, "info.py")) as fin:
                    sampler = eval(fin.read())
                if sampler["backend"] not in self.backends:
                    self.alert("missing backend %r for sampler %r"
                               % (sampler["backend"], sampler["name"]))
                    continue
                sampler["sampler"] = os.path.join(path, "sampler.x")
                if isinstance(__builtins__, dict):
                    intern = __builtins__["intern"]  # supress pyflakes error
                sampler["kernels"] = {kernel[0]: tuple(map(intern, kernel))
                                      for kernel in sampler["kernels"]}
                self.samplers[sampler["name"]] = sampler
        self.log("loaded", len(self.samplers), "samplers:",
                 *sorted(self.samplers))

    def signatures_init(self):
        self.signatures = {}
        signaturepath = os.path.join(self.rootpath, "GUI", "signatures")
        for path, dirs, files in os.walk(signaturepath, followlinks=True):
            for filename in files:
                if filename[0] == ".":
                    continue
                sig = signature.Signature(file=os.path.join(path, filename))
                self.signatures[str(sig[0])] = sig
        self.log("loaded", len(self.signatures), "signatures:",
                 *sorted(self.signatures))

    def state_init(self):
        self.statefile = os.path.join(self.rootpath, "GUI", ".state.py")
        try:
            with open(self.statefile) as fin:
                state = eval(fin.read(), symbolic.__dict__)
            self.log("loaded state from", self.statefile)
        except:
            sampler = self.samplers[min(self.samplers)]
            state = {
                "sampler": sampler["name"],
                "nt": 1,
                "nrep": 10,
                "usepapi": False,
                "useld": False,
                "usevary": False,
                "userange": False,
                "rangevar": "n",
                "range": (8, 1000, 32),
                "counters": sampler["papi_counters_max"] * [None],
                "samplename": "",
                "calls": [[""]],
                "vary": {},
                "datascale": 100,
            }
            if "dgemm_" in sampler["kernels"]:
                state["calls"][0] = ("dgemm_", "N", "N", 1000, 1000, 1000,
                                     1, "A", 1000, "B", 1000, 1, "C", 1000)
        self.state_fromflat(state)
        self.connections_update()
        self.data_update()
        self.state_write()

    # utility type routines
    def state_toflat(self):
        state = self.state.copy()
        state["calls"] = map(list, self.calls)
        return state

    def state_fromflat(self, state):
        state = state.copy()
        calls = state["calls"]
        for callid, call in enumerate(calls):
            if call[0] in self.signatures:
                calls[callid] = self.signatures[call[0]](*call[1:])
        state["calls"] = calls
        self.state = state

    def state_write(self):
        with open(self.statefile, "w") as fout:
            print(pprint.pformat(self.state_toflat(), 4), file=fout)

    def get_infostr(self):
        sampler = self.samplers[self.sampler]
        info = "System:\t%s\n" % sampler["system_name"]
        if sampler["backend"] != "local":
            info += "  (via %s(\n" % sampler["backend"]
        info += "  %s\n" % sampler["cpu_model"]
        info += "  %.2f MHz\n" % (sampler["frequency"] / 1e6)
        info += "\nBLAS:\t%s\n" % sampler["blas_name"]
        return info

    def range_eval(self, expr, value=None):
        if not self.userange:
            if value is None:
                return expr
            return [expr]
        if value is None:
            return [self.range_eval(expr, val) for val in range(*self.range)]
        if isinstance(expr, symbolic.Expression):
            return expr(**{self.rangevar: value})
        return expr

    # simple data operations
    def data_maxdim(self):
        result = 0
        for data in self.data.itervalues():
            sym = data["sym"]
            if isinstance(sym, symbolic.Prod):
                result = max(result, max(max(self.range_eval(value))
                                         for value in sym[1:]))
            else:
                result = max(result, max(self.range_eval(sym)))
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
        for i, arg in enumerate(call2.sig):
            if isinstance(arg, (signature.Ld, signature.Inc)):
                if self.useld and not isinstance(call2[i],
                                                 symbolic.Expression):
                    call[i] = max(call2[i], call[i])
                else:
                    call[i] = call2[i]

    def data_update(self, callid=None):
        if callid is None:
            self.data = {}
            for callid in range(len(self.calls)):
                self.data_update(callid)
            self.vary = {name: value for name, value in self.vary.iteritems()
                         if name in self.data}
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
        argdict = {"." + arg.name: value for arg, value in zip(call.sig, call)}
        argnamedict = {"." + arg.name: symbolic.Symbol(arg.name)
                       for arg in call.sig}
        for argid in call.sig.dataargs():
            name = call[argid]
            if name is None:
                continue
            self.data[name] = {
                "comp": compcall[argid],
                "min": mincall[argid],
                "sym": symcall[argid].substitute(**argdict),
                "symnames": symcall[argid].substitute(**argnamedict),
                "type": call.sig[argid].__class__,
            }
            if name not in self.vary:
                self.vary[name] = False

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
                else:
                    self.alert("don't know how to handle datasize for",
                               call.sig[argid], "in", call.sig, ":", datasize)
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
        # TODO: lds as connections?
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
        self.sampler = samplername
        sampler = self.samplers[samplername]
        self.nt = max(self.nt, sampler["nt_max"])

        # update countes (kill unavailable, adjust length)
        papi_counters_max = sampler["papi_counters_max"]
        self.usepapi &= papi_counters_max > 0
        counters = []
        for counter in self.counters:
            if counter in sampler["papi_counters_avail"]:
                counters.append(counter)
        counters = counters[:papi_counters_max]
        counters += (papi_counters_max - len(counters)) * [None]
        self.counters = counters

        # remove unavailable calls
        # TODO

        # update UI
        self.UI_nt_setmax()
        self.UI_nt_set()
        self.UI_usepapi_setenabled()
        self.UI_usepapi_set()
        self.UI_counters_setoptions()
        self.UI_counters_set()
        self.UI_calls_init()

    def routine_set(self, callid, value):
        if value in self.signatures:
            # TODO: non-static default argument values
            call = self.signatures[value]()
            owndata = []
            for i, arg in enumerate(call.sig):
                if isinstance(arg, signature.Dim):
                    call[i] = 1000
                elif isinstance(arg, signature.Data):
                    for name in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        if name not in self.data and name not in owndata:
                            call[i] = name
                            owndata.append(name)
                            break
            self.calls[callid] = call
            self.infer_lds(callid)
            self.data_update()
        else:
            self.calls[callid] = [value]
        self.UI_call_set(callid, 0)
        self.state_write()

    def arg_set(self, callid, argid, value):
        call = self.calls[callid]
        arg = call.sig[argid]
        if isinstance(arg, signature.Flag):
            call[argid] = value
            self.connections_update()
            self.connections_apply(callid)
            self.state_write()
            self.UI_calls_set(callid, argid)
            self.UI_data_viz()
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
            # evaluate value
            try:
                if self.userange:
                    var = self.rangevar
                    value = eval(value, {}, {var: symbolic.Symbol(var)})
                else:
                    value = int(eval(value, {}, {}))
            except:
                value = None
            call[argid] = value
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
            # TODO: proper ld treatment
            call[argid] = int(value) if value else None
            self.data_update()
            self.state_write()
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
                self.UI_choose_data_override(callid, argid, value)
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

    # submit
    def generate_cmds(self):
        cmds = []

        rangevals = [0]
        if self.userange:
            rangevals = range(*self.range)

        if len(self.counters):
            cmds.append(["########################################"])
            cmds.append(["# counters                             #"])
            cmds.append(["########################################"])
            cmds.append([])
            cmds.append(["set_counters"] + self.counters)
            cmds.append([])
            cmds.append([])

        cmds.append(["########################################"])
        cmds.append(["# data                                 #"])
        cmds.append(["########################################"])

        # data
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
            size = max(self.range_eval(data["comp"]))
            if not self.vary[name]:
                cmds.append([cmdprefix + "malloc", name, size])
                continue
            # argument varies
            fullsize = size * self.nrep
            cmds.append([cmdprefix + "malloc", name, fullsize])
            rangesizes = self.range_eval(data["comp"])
            for rangeval, rangesize in zip(rangevals, rangesizes):
                if self.userange:
                    cmds.append(["# %s = %d" % (self.rangevar, rangeval)])
                for rep in range(self.nrep):
                    cmds.append([cmdprefix + "offset", name, rep * rangesize,
                                 "%s_%d_%d" % (name, rangeval, rep)])
        cmds.append([])
        cmds.append([])

        # calls
        cmds.append(["########################################"])
        cmds.append(["# calls                                #"])
        cmds.append(["########################################"])
        cmds.append([])
        for rangeid, rangeval in enumerate(rangevals):
            if self.userange:
                cmds.append(["# %s = %d" % (self.rangevar, rangeval)])
            for rep in range(self.nrep):
                for call in self.calls:
                    call = call.sig(*[self.range_eval(arg, rangeval)
                                      for arg in call[1:]])
                    cmd = call.format_sampler()
                    for argid in call.sig.dataargs():
                        name = call[argid]
                        if self.vary[name]:
                            cmd[argid] = "%s_%d_%d" % (name, rangeval, rep)
                    cmds.append(cmd)

        return cmds

    def generate_script(self, cmds):
        ofilename = os.path.join(self.rootpath, "meas",
                                 self.samplename + ".pysmpl")
        efilename = os.path.join(self.rootmath, "meas",
                                 self.samplename + ".err")
        script = "cat > " + ofilename + " 2> " + efilename
        script += " << 1234END5678\n"
        script += "{'state':\n" + pprint.pformat(self.state_toflat(), 4)
        script += ",\n 'cmds': [\n"
        for cmd in cmds:
            script += "\t" + repr(cmd) + ",\n"
        script += "],\n 'rawdata': '''\n"
        script += "1234END5678\n"
        script += self.samplers[self.sampler]["sampler"] + " >> " + ofilename
        script += " 2>> " + efilename + " <<1234END5678\n"
        for cmd in cmds:
            script += "\t".join(map(str, cmd)) + "\n"
        script += "1234END5678\n"
        script += "echo \"'''}\" >> " + ofilename + " 2>> " + efilename
        script += "[ -s " + efilename + " ] || rm " + efilename
        return script

    def submit(self):
        sampler = self.samplers[self.sampler]
        cmds = self.generate_cmds()
        script = self.generate_script(cmds)
        self.backends[sampler["backend"]].submit(script, nt=self.nt,
                                                 jobname=self.samplename)
        self.UI_alert("Submitted job %r to backend %r" %
                      (self.samplename, sampler["backend"]))
        self.log("submitted %r to %r" %
                 (self.samplename, sampler["backend"]))

    # user interface
    def UI_init(self):
        self.alert("GUI needs to be subclassed")

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
        self.UI_calls_init()
        self.UI_samplename_set()
        self.UI_submit_setenabled()

    # event handlers
    def UI_sampler_change(self, samplername):
        # TODO: check for missing call routine conflicts
        self.sampler_set(samplername)

    def UI_nt_change(self, nt):
        self.nt = nt
        self.state_write()

    def UI_nrep_change(self, nrep):
        self.nrep = nrep
        self.state_write()

    def UI_usepapi_change(self, state):
        self.usepapi = state
        self.UI_counters_setvisible()
        self.state_write()

    def UI_useld_change(self, state):
        self.useld = state
        self.state_write()
        self.UI_useld_apply()

    def UI_usevary_change(self, state):
        self.usevary = state
        self.state_write()
        self.UI_usevary_apply()

    def UI_counters_change(self, counters):
        self.counters = counters
        self.state_write()

    def UI_userange_change(self, state):
        self.userange = state
        self.state_write()
        self.UI_range_setvisible()

    def UI_rangevar_change(self, varname):
        self.rangevar = varname
        self.state_write()

    def UI_range_change(self, range):
        self.range = range
        self.data_update()
        self.state_write()

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
        self.vary[name] = state
        self.state_write()
        self.UI_data_viz()

    def UI_samplename_change(self, samplename):
        self.samplename = samplename
        self.state_write()

    def UI_submit_click(self):
        self.submit()
