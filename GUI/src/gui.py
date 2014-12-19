#!/usr/bin/env python
from __future__ import division, print_function

from signature import Signature

import sys
import os


def alert(*args):
    print(*args, file=sys.stderr)


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

    def samplers_init(self):
        self.samplers = {}
        samplerpath = os.path.join(self.rootpath, "Sampler", "build")
        for path, dirs, files in os.walk(samplerpath, followlinks=True):
            if "info.py" in files and "sampler.x" in files:
                with open(os.path.join(path, "info.py")) as fin:
                    system = eval(fin.read())
                system["sampler"] = os.path.join(path, "sampler.x")
                self.samplers[system["name"]] = system

    def signatures_init(self):
        self.signatures = {}
        signaturepath = os.path.join(self.rootpath, "GUI", "signatures")
        for path, dirs, files in os.walk(signaturepath, followlinks=True):
            for filename in files:
                sig = Signature(file=os.path.join(path, filename))
                self.signatures[str(sig[0])] = sig

    def state_init(self):
        self.statefile = os.path.join(self.rootpath, "GUI", ".state.py")
        try:
            with open(self.statefile) as fin:
                self.state = eval(fin)
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
                # "rangevar": "n",
                "range": (8, 32, 1000),
                "calls": [("",)],
                "counters": sampler["papi_counters_max"] * [None],
                "samplename": "",
            }
            if "dgemm_" in sampler["kernels"] and "dgemm_" in self.signatures:
                sig = self.signatures["dgemm_"]
                self.state["calls"] = [sig("N", "N", 1000, 1000, 1000, 1, "A",
                                           1000, "B", 1000, 1, "C", 1000)]
            self.state_write()

    def state_write(self):
        with open(self.statefile, "w") as fout:
            try:
                import pprint
                print(pprint.pformat(self.state, 4), file=fout)
            except:
                print(repr(self.state), file=fout)

    def get_infostr(self):
        sampler = self.samplers[self.state["sampler"]]
        info = "System:\t%s\n" % sampler["system_name"]
        if sampler["backend"] != "local":
            info += "  (via %s(\n" % sampler["backend"]
        info += "  %s\n" % sampler["cpu_model"]
        info += "  %.2f MHz\n" % (sampler["frequency"] / 1e6)
        info += "\nBLAS:\t%s\n" % sampler["blas_name"]
        return info

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

    def UI_init(self):
        alert("GUI_ needs to be subclassed")

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
        # self.UI_rangevar_set()
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
        self.state_write()
        # TODO

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

    # def UI_rangevar_change(self, varname):
    #     self.state["rangevar"] = varname
    #     self.state_write()

    def UI_range_change(self, range):
        self.state["range"] = range
        self.state_write()

    def UI_call_add(self):
        alert("call_add")

    def UI_call_remove(self, callid):
        alert("call_remove", callid)

    def UI_call_moveup(self, callid):
        alert("call_moveup", callid)

    def UI_call_movedown(self, callid):
        alert("call_movedown", callid)

    def UI_routine_cahnge(self, callid, routinename):
        alert("routine_change", callid, routinename)

    def UI_arg_change(self, callid, argid, value):
        alert("arg_change", callid, argid, value)

    def UI_samplename_change(self, samplename):
        self.state["samplename"] = samplename
        self.state_write()

    def UI_submit_click(self):
        alert("submit_click")
