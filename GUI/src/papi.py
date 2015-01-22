#!/usr/bin/env python
from __future__ import division, print_function

events = {
    "PAPI_L1_DCM": {
        "short": "L1D cache misses",
        "long": "Level 1 data cache misses"
    },
    "PAPI_L1_ICM": {
        "short": "L1I cache misses",
        "long": "Level 1 instruction cache misses"
    },
    "PAPI_L2_DCM": {
        "short": "L2D cache misses",
        "long": "Level 2 data cache misses"
    },
    "PAPI_L2_ICM": {
        "short": "L2I cache misses",
        "long": "Level 2 instruction cache misses"
    },
    "PAPI_L3_DCM": {
        "short": "L3D cache misses",
        "long": "Level 3 data cache misses"
    },
    "PAPI_L3_ICM": {
        "short": "L3I cache misses",
        "long": "Level 3 instruction cache misses"
    },
    "PAPI_L1_TCM": {
        "short": "L1 cache misses",
        "long": "Level 1 cache misses"
    },
    "PAPI_L2_TCM": {
        "short": "L2 cache misses",
        "long": "Level 2 cache misses"
    },
    "PAPI_L3_TCM": {
        "short": "L3 cache misses",
        "long": "Level 3 cache misses"
    },
    "PAPI_CA_SNP": {
        "short": "Snoop Requests",
        "long": "Requests for a snoop"
    },
    "PAPI_CA_SHR": {
        "short": "Ex Acces shared CL",
        "long": "Requests for exclusive access to shared cache line"
    },
    "PAPI_CA_CLN": {
        "short": "Ex Access clean CL",
        "long": "Requests for exclusive access to clean cache line"
    },
    "PAPI_CA_INV": {
        "short": "Cache ln invalid",
        "long": "Requests for cache line invalidation"
    },
    "PAPI_CA_ITV": {
        "short": "Cache ln intervene",
        "long": "Requests for cache line intervention"
    },
    "PAPI_L3_LDM": {
        "short": "L3 load misses",
        "long": "Level 3 load misses"
    },
    "PAPI_L3_STM": {
        "short": "L3 store misses",
        "long": "Level 3 store misses"
    },
    "PAPI_BRU_IDL": {
        "short": "Branch idle cycles",
        "long": "Cycles branch units are idle"
    },
    "PAPI_FXU_IDL": {
        "short": "IU idle cycles",
        "long": "Cycles integer units are idle"
    },
    "PAPI_FPU_IDL": {
        "short": "FPU idle cycles",
        "long": "Cycles floating point units are idle"
    },
    "PAPI_LSU_IDL": {
        "short": "L/SU idle cycles",
        "long": "Cycles load/store units are idle"
    },
    "PAPI_TLB_DM": {
        "short": "Data TLB misses",
        "long": "Data translation lookaside buffer misses"
    },
    "PAPI_TLB_IM": {
        "short": "Instr TLB misses",
        "long": "Instruction translation lookaside buffer misses"
    },
    "PAPI_TLB_TL": {
        "short": "Total TLB misses",
        "long": "Total translation lookaside buffer misses"
    },
    "PAPI_L1_LDM": {
        "short": "L1 load misses",
        "long": "Level 1 load misses"
    },
    "PAPI_L1_STM": {
        "short": "L1 store misses",
        "long": "Level 1 store misses"
    },
    "PAPI_L2_LDM": {
        "short": "L2 load misses",
        "long": "Level 2 load misses"
    },
    "PAPI_L2_STM": {
        "short": "L2 store misses",
        "long": "Level 2 store misses"
    },
    "PAPI_BTAC_M": {
        "short": "Br targt addr miss",
        "long": "Branch target address cache misses"
    },
    "PAPI_PRF_DM": {
        "short": "Data prefetch miss",
        "long": "Data prefetch cache misses"
    },
    "PAPI_L3_DCH": {
        "short": "L3D cache hits",
        "long": "Level 3 data cache hits"
    },
    "PAPI_TLB_SD": {
        "short": "TLB shootdowns",
        "long": "Translation lookaside buffer shootdowns"
    },
    "PAPI_CSR_FAL": {
        "short": "Failed store cond",
        "long": "Failed store conditional instructions"
    },
    "PAPI_CSR_SUC": {
        "short": "Good store cond",
        "long": "Successful store conditional instructions"
    },
    "PAPI_CSR_TOT": {
        "short": "Total store cond",
        "long": "Total store conditional instructions"
    },
    "PAPI_MEM_SCY": {
        "short": "Stalled mem cycles",
        "long": "Cycles Stalled Waiting for memory accesses"
    },
    "PAPI_MEM_RCY": {
        "short": "Stalled rd cycles",
        "long": "Cycles Stalled Waiting for memory Reads"
    },
    "PAPI_MEM_WCY": {
        "short": "Stalled wr cycles",
        "long": "Cycles Stalled Waiting for memory writes"
    },
    "PAPI_STL_ICY": {
        "short": "No instr issue",
        "long": "Cycles with no instruction issue"
    },
    "PAPI_FUL_ICY": {
        "short": "Max instr issue",
        "long": "Cycles with maximum instruction issue"
    },
    "PAPI_STL_CCY": {
        "short": "No instr done",
        "long": "Cycles with no instructions completed"
    },
    "PAPI_FUL_CCY": {
        "short": "Max instr done",
        "long": "Cycles with maximum instructions completed"
    },
    "PAPI_HW_INT": {
        "short": "Hdw interrupts",
        "long": "Hardware interrupts"
    },
    "PAPI_BR_UCN": {
        "short": "Uncond branch",
        "long": "Unconditional branch instructions"
    },
    "PAPI_BR_CN": {
        "short": "Cond branch",
        "long": "Conditional branch instructions"
    },
    "PAPI_BR_TKN": {
        "short": "Cond branch taken",
        "long": "Conditional branch instructions taken"
    },
    "PAPI_BR_NTK": {
        "short": "Cond br not taken",
        "long": "Conditional branch instructions not taken"
    },
    "PAPI_BR_MSP": {
        "short": "Cond br mspredictd",
        "long": "Conditional branch instructions mispredicted"
    },
    "PAPI_BR_PRC": {
        "short": "Cond br predicted",
        "long": "Conditional branch instructions correctly predicted"
    },
    "PAPI_FMA_INS": {
        "short": "FMAs completed",
        "long": "FMA instructions completed"
    },
    "PAPI_TOT_IIS": {
        "short": "Instr issued",
        "long": "Instructions issued"
    },
    "PAPI_TOT_INS": {
        "short": "Instr completed",
        "long": "Instructions completed"
    },
    "PAPI_INT_INS": {
        "short": "Int instructions",
        "long": "Integer instructions"
    },
    "PAPI_FP_INS": {
        "short": "FP instructions",
        "long": "Floating point instructions"
    },
    "PAPI_LD_INS": {
        "short": "Loads",
        "long": "Load instructions"
    },
    "PAPI_SR_INS": {
        "short": "Stores",
        "long": "Store instructions"
    },
    "PAPI_BR_INS": {
        "short": "Branches",
        "long": "Branch instructions"
    },
    "PAPI_VEC_INS": {
        "short": "Vector/SIMD instr",
        "long": "Vector/SIMD instructions (could include integer)"
    },
    "PAPI_RES_STL": {
        "short": "Stalled res cycles",
        "long": "Cycles stalled on any resource"
    },
    "PAPI_FP_STAL": {
        "short": "Stalled FPU cycles",
        "long": "Cycles the FP unit(s) are stalled"
    },
    "PAPI_TOT_CYC": {
        "short": "Total cycles",
        "long": "Total cycles"
    },
    "PAPI_LST_INS": {
        "short": "L/S completed",
        "long": "Load/store instructions completed"
    },
    "PAPI_SYC_INS": {
        "short": "Syncs completed",
        "long": "Synchronization instructions completed"
    },
    "PAPI_L1_DCH": {
        "short": "L1D cache hits",
        "long": "Level 1 data cache hits"
    },
    "PAPI_L2_DCH": {
        "short": "L2D cache hits",
        "long": "Level 2 data cache hits"
    },
    "PAPI_L1_DCA": {
        "short": "L1D cache accesses",
        "long": "Level 1 data cache accesses"
    },
    "PAPI_L2_DCA": {
        "short": "L2D cache accesses",
        "long": "Level 2 data cache accesses"
    },
    "PAPI_L3_DCA": {
        "short": "L3D cache accesses",
        "long": "Level 3 data cache accesses"
    },
    "PAPI_L1_DCR": {
        "short": "L1D cache reads",
        "long": "Level 1 data cache reads"
    },
    "PAPI_L2_DCR": {
        "short": "L2D cache reads",
        "long": "Level 2 data cache reads"
    },
    "PAPI_L3_DCR": {
        "short": "L3D cache reads",
        "long": "Level 3 data cache reads"
    },
    "PAPI_L1_DCW": {
        "short": "L1D cache writes",
        "long": "Level 1 data cache writes"
    },
    "PAPI_L2_DCW": {
        "short": "L2D cache writes",
        "long": "Level 2 data cache writes"
    },
    "PAPI_L3_DCW": {
        "short": "L3D cache writes",
        "long": "Level 3 data cache writes"
    },
    "PAPI_L1_ICH": {
        "short": "L1I cache hits",
        "long": "Level 1 instruction cache hits"
    },
    "PAPI_L2_ICH": {
        "short": "L2I cache hits",
        "long": "Level 2 instruction cache hits"
    },
    "PAPI_L3_ICH": {
        "short": "L3I cache hits",
        "long": "Level 3 instruction cache hits"
    },
    "PAPI_L1_ICA": {
        "short": "L1I cache accesses",
        "long": "Level 1 instruction cache accesses"
    },
    "PAPI_L2_ICA": {
        "short": "L2I cache accesses",
        "long": "Level 2 instruction cache accesses"
    },
    "PAPI_L3_ICA": {
        "short": "L3I cache accesses",
        "long": "Level 3 instruction cache accesses"
    },
    "PAPI_L1_ICR": {
        "short": "L1I cache reads",
        "long": "Level 1 instruction cache reads"
    },
    "PAPI_L2_ICR": {
        "short": "L2I cache reads",
        "long": "Level 2 instruction cache reads"
    },
    "PAPI_L3_ICR": {
        "short": "L3I cache reads",
        "long": "Level 3 instruction cache reads"
    },
    "PAPI_L1_ICW": {
        "short": "L1I cache writes",
        "long": "Level 1 instruction cache writes"
    },
    "PAPI_L2_ICW": {
        "short": "L2I cache writes",
        "long": "Level 2 instruction cache writes"
    },
    "PAPI_L3_ICW": {
        "short": "L3I cache writes",
        "long": "Level 3 instruction cache writes"
    },
    "PAPI_L1_TCH": {
        "short": "L1 cache hits",
        "long": "Level 1 total cache hits"
    },
    "PAPI_L2_TCH": {
        "short": "L2 cache hits",
        "long": "Level 2 total cache hits"
    },
    "PAPI_L3_TCH": {
        "short": "L3 cache hits",
        "long": "Level 3 total cache hits"
    },
    "PAPI_L1_TCA": {
        "short": "L1 cache accesses",
        "long": "Level 1 total cache accesses"
    },
    "PAPI_L2_TCA": {
        "short": "L2 cache accesses",
        "long": "Level 2 total cache accesses"
    },
    "PAPI_L3_TCA": {
        "short": "L3 cache accesses",
        "long": "Level 3 total cache accesses"
    },
    "PAPI_L1_TCR": {
        "short": "L1 cache reads",
        "long": "Level 1 total cache reads"
    },
    "PAPI_L2_TCR": {
        "short": "L2 cache reads",
        "long": "Level 2 total cache reads"
    },
    "PAPI_L3_TCR": {
        "short": "L3 cache reads",
        "long": "Level 3 total cache reads"
    },
    "PAPI_L1_TCW": {
        "short": "L1 cache writes",
        "long": "Level 1 total cache writes"
    },
    "PAPI_L2_TCW": {
        "short": "L2 cache writes",
        "long": "Level 2 total cache writes"
    },
    "PAPI_L3_TCW": {
        "short": "L3 cache writes",
        "long": "Level 3 total cache writes"
    },
    "PAPI_FML_INS": {
        "short": "FPU multiply",
        "long": "Floating point multiply instructions"
    },
    "PAPI_FAD_INS": {
        "short": "FPU add",
        "long": "Floating point add instructions"
    },
    "PAPI_FDV_INS": {
        "short": "FPU divide",
        "long": "Floating point divide instructions"
    },
    "PAPI_FSQ_INS": {
        "short": "FPU square root",
        "long": "Floating point square root instructions"
    },
    "PAPI_FNV_INS": {
        "short": "FPU inverse",
        "long": "Floating point inverse instructions"
    },
    "PAPI_FP_OPS": {
        "short": "FP operations",
        "long": "Floating point operations"
    },
    "PAPI_SP_OPS": {
        "short": "SP operations",
        "long": "Floating point operations; optimized to count scaled single "
                "precision vector operations"
    },
    "PAPI_DP_OPS": {
        "short": "DP operations",
        "long": "Floating point operations; optimized to count scaled double "
                "precision vector operations"
    },
    "PAPI_VEC_SP": {
        "short": "SP Vector/SIMD instr",
        "long": "Single precision vector/SIMD instructions"
    },
    "PAPI_VEC_DP": {
        "short": "DP Vector/SIMD instr",
        "long": "Double precision vector/SIMD instructions"
    }
}
