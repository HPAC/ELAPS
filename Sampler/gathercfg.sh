#!/bin/bash

if [ -e /proc/cpuinfo ]; then
    # Linux stuff
    CPU_MODEL=`< /proc/cpuinfo sed -n "s/model name\\s*: \(.*\)/\1/p" | tail -n 1`
    MHZ=`< /proc/cpuinfo sed -n "s/cpu MHz\\s*: \(.*\)/\1/p" | tail -n 1`
    FREQUENCY_HZ=`bc -l <<< "$MHZ * 1000000"`
    CORES_PER_CPU=`< /proc/cpuinfo sed -n "s/cpu cores\\s*: \(.*\)/\1/p" | tail -n 1`
    SIBLINGS=`< /proc/cpuinfo sed -n "s/siblings\\s*: \(.*\)/\1/p" | tail -n 1`
    THREADS_PER_CORE=$(($SIBLINGS / $CORES_PER_CPU))
    NPROCS=$((`< /proc/cpuinfo sed -n "s/processor\\s*: \(.*\)/\1/p" | tail -n 1` + 1))
    NCORES=$((NPROCS / $THREADS_PER_CORE))
    if hash lscpu 2>/dev/null; then
        MHZ=`lscpu | sed -n "s/CPU MHz:\\s*\(.*\)/\1/p" | tr , .`
        [ -z "$MHZ" ] || FREQUENCY_HZ=`bc -l <<< "$MHZ * 1000000"`
        MHZ=`lscpu | sed -n "s/CPU max MHz:\\s*\(.*\)/\1/p" | tr , .`
        [ -z "$MHZ" ] || FREQUENCY_HZ=`bc -l <<< "$MHZ * 1000000"`
    fi
elif hash sysctl 2>/dev/null; then
    # MAC stuff
    CPU_MODEL="`sysctl -n machdep.cpu.brand_string`"
    FREQUENCY_HZ=`sysctl -n hw.cpufrequency`
    NCORES=`sysctl -n hw.physicalcpu`
    THREADS_PER_CORE=$((`sysctl -n hw.logicalcpu` / `sysctl -n hw.physicalcpu`))
fi

if hash papi_avail 2>/dev/null; then
    # PAPI
    PAPI_COUNTERS_MAX=`papi_avail 2>/dev/null | sed -n "s/Number Hardware Counters\\s*: \(.*\)/\1/p"`
    PAPI_COUNTERS_AVAIL=`papi_avail -a 2>/dev/null | sed -n "s/\(PAPI_.*\) 0x.*/\1/p" | tr "\n" " "`
else
    PAPI_COUNTERS_MAX=0
    PAPI_COUNTERS_AVAIL=""
fi

# TODO: check if sourced

echo "CPU_MODEL=\"$CPU_MODEL\""
echo "FREQUENCY_HZ=$FREQUENCY_HZ"
echo "NCORES=$NCORES"
echo "THREADS_PER_CORE=$THREADS_PER_CORE"
echo "PAPI_COUNTERS_MAX=$PAPI_COUNTERS_MAX"
echo "PAPI_COUNTERS_AVAIL=\"$PAPI_COUNTERS_AVAIL\""

export CPU_MODEL
export FREQUENCY_HZ
export NCORES
export THREADS_PER_CORE
export PAPI_COUNTERS_MAX
export PAPI_COUNTERS_AVAIL
