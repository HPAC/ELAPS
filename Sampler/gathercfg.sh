#!/bin/bash

if hash sysctl 2>/dev/null; then
    echo "CPU_MODEL=`sysctl -n machdep.cpu.brand_string`"
    echo "FREQUENCY_HZ=`sysctl -n hw.cpufrequency`"
    echo "NCORES=`sysctl -n hw.physicalcpu`"
    echo "THREADS_PER_CORE=$((`sysctl -n hw.logicalcpu` / `sysctl -n hw.physicalcpu`))"
    echo "L1I_SIZE=`sysctl -n hw.l1icachesize`"
    echo "L1D_SIZE=`sysctl -n hw.l1dcachesize`"
    echo "L2_SIZE=`sysctl -n hw.l2cachesize`"
    echo "L3_SIZE=`sysctl -n hw.l3cachesize`"
fi
if hash papi_avail 2>dev/null; then
else
    echo "PAPI_COUNTERS_MAX=0"
fi
