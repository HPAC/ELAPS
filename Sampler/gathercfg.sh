#!/bin/bash

if [ -e /proc/cpuinfo ]; then
    # Linux stuff
    CPU_MODEL_=`< /proc/cpuinfo sed -n "s/model name\\s*: \(.*\)/\1/p" | tail -n 1`
    MHZ=`< /proc/cpuinfo sed -n "s/cpu MHz\\s*: \(.*\)/\1/p" | tail -n 1`
    FREQUENCY_HZ_=`bc -l <<< "$MHZ * 1000000"`
    CORES_PER_CPU=`< /proc/cpuinfo sed -n "s/cpu cores\\s*: \(.*\)/\1/p" | tail -n 1`
    SIBLINGS=`< /proc/cpuinfo sed -n "s/siblings\\s*: \(.*\)/\1/p" | tail -n 1`
    THREADS_PER_CORE_=$(($SIBLINGS / $CORES_PER_CPU))
    NPROCS=$((`< /proc/cpuinfo sed -n "s/processor\\s*: \(.*\)/\1/p" | tail -n 1` + 1))
    NCORES_=$((NPROCS / $THREADS_PER_CORE_))
    if hash lscpu 2>/dev/null; then
        MHZ=`lscpu | sed -n "s/CPU MHz:\\s*\(.*\)/\1/p" | tr , .`
        [ -z "$MHZ" ] || FREQUENCY_HZ_=`bc -l <<< "$MHZ * 1000000"`
        MHZ=`lscpu | sed -n "s/CPU max MHz:\\s*\(.*\)/\1/p" | tr , .`
        [ -z "$MHZ" ] || FREQUENCY_HZ_=`bc -l <<< "$MHZ * 1000000"`
    fi
elif hash sysctl 2>/dev/null; then
    # MAC stuff
    CPU_MODEL_="`sysctl -n machdep.cpu.brand_string`"
    FREQUENCY_HZ_=`sysctl -n hw.cpufrequency`
    NCORES_=`sysctl -n hw.physicalcpu`
    THREADS_PER_CORE_=$((`sysctl -n hw.logicalcpu` / `sysctl -n hw.physicalcpu`))
fi

if hash papi_avail 2>/dev/null; then
    # PAPI
    PAPI_COUNTERS_MAX_=`papi_avail 2>/dev/null | sed -n "s/Number Hardware Counters\\s*: \(.*\)/\1/p"`
    PAPI_COUNTERS_AVAIL_=`papi_avail -a 2>/dev/null | sed -n "s/\(PAPI_.*\) 0x.*/\1/p" | tr "\n" " "`
else
    PAPI_COUNTERS_MAX_=0
    PAPI_COUNTERS_AVAIL_=""
fi

if [ "$0" == "$BASH_SOURCE" ]; then
    echo "CPU_MODEL=\"$CPU_MODEL_\""
    echo "FREQUENCY_HZ=$FREQUENCY_HZ_"
    echo "NCORES=$NCORES_"
    echo "THREADS_PER_CORE=$THREADS_PER_CORE_"
    echo "PAPI_COUNTERS_MAX=$PAPI_COUNTERS_MAX_"
    echo "PAPI_COUNTERS_AVAIL=\"$PAPI_COUNTERS_AVAIL_\""
else
    : ${CPU_MODEL:="$CPU_MODEL_"}
    : ${FREQUENCY_HZ:=$FREQUENCY_HZ_}
    : ${NCORES:=$NCORES_}
    : ${THREADS_PER_CORE:=$THREADS_PER_CORE_}
    : ${PAPI_COUNTERS_MAX:=$PAPI_COUNTERS_MAX_}
    : ${PAPI_COUNTERS_AVAIL:="$PAPI_COUNTERS_AVAIL_"}
fi
