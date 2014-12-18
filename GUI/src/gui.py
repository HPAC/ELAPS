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
                "rangevar": "n",
                "range": (8, 32, 1000),
                "calls": [("",)],
                "counters": sampler["papi_counters_max"] * [None],
                "samplename": "",
            }
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

    def UI_init(self):
        alert("GUI_ needs to be subclassed")

    def UI_setall(self):
        sampler = self.samplers[self.state["sampler"]]
        self.UI_sampler_set(sampler["name"])
        self.UI_nt_setmax(sampler["nt_max"])
        self.UI_nt_set(self.state["nt"])
        self.UI_nrep_set(self.state["nrep"])
        self.UI_info_set(self.get_infostr())
        self.UI_usepapi_setenabled(sampler["papi_counters_max"] > 0)
        self.UI_usepapi_set(self.state["usepapi"])
        self.UI_useld_set(self.state["useld"])
        self.UI_usevary_set(self.state["usevary"])
        self.UI_userange_set(self.state["userange"])
        self.UI_counters_setvisible(self.state["usepapi"])
        self.UI_counters_setoptions(sampler["papi_counters_max"],
                                    sampler["papi_counters_avail"])
        self.UI_counters_set(self.state["counters"])
        self.UI_range_setvisible(self.state["userange"])
        self.UI_rangevar_set(self.state["rangevar"])
        self.UI_range_set(self.state["range"])
        # TODO: calls
        self.UI_samplename_set(self.state["samplename"])

    # event handlers
    def UI_sampler_change(self, samplername):
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

        # update calls (disable unavailable)
        # TODO

        # update UI
        self.UI_nt_setmax(sampler["nt_max"])
        self.UI_nt_set(self.state["nt"])
        self.UI_usepapi_setenabled(sampler["papi_counters_max"] > 0)
        self.UI_usepapi_set(self.state["usepapi"])
        self.UI_counters_setoptions(sampler["papi_counters_max"],
                                    sampler["papi_counters_avail"])
        self.UI_counters_set(self.state["counters"])

    def UI_nt_change(self, nt):
        self.state["nt"] = nt
        self.state_write()

    def UI_nrep_change(self, nrep):
        self.state["nrep"] = nrep
        self.state_write()

    def UI_usepapi_change(self, state):
        self.UI_counters_setvisible(state)
        self.state["usepapi"] = state
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
        self.UI_range_setvisible(state)
        self.state["userange"] = state
        self.state_write()

    def UI_rangevar_change(self, varname):
        self.state["rangevar"] = varname
        self.state_write()
        # TODO: effect on calls?

    def UI_range_change(self, range):
        self.state["range"] = range
        self.state_write()

    def UI_samplename_change(self, samplename):
        self.state["samplename"] = samplename
        self.state_write()

    def UI_submit_click(self):
        # TODO
        pass
