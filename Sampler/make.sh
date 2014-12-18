#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "usage: $0 config_file"
    exit
fi

. $1

# set default values
[ -z "$SYSTEM_NAME" ] && SYSTEM_NAME="local"
[ -z "$NAME" ] && NAME=${SYSTEM_NAME}_$BLAS_NAME
[ -z "$KERNEL_HEADERS" ] && KERNEL_HEADERS="headers/blas.h headers/lapack.h"
[ -z "$PAPI_COUNTERS_MAX" ] && PAPI_COUNTERS_MAX=0
[ -z "$BACKEND" ] && BACKEND="local"
[ -z "$BACKEND_HEADER" ] && BACKEND_HEADER=""
[ -z "$BACKEND_OPTIONS" ] && BACKEND_OPTIONS=""
if [ -z "$NT_MAX"]; then
    if [ "$BACKEND" = "local" ]; then
        NT_MAX=`grep -c ^processor /proc/cpuinfo`
    else
        echo "assuming NT_MAX=1 for non-local system"
        NT_MAX=1
    fi
fi
[ -z "$FLOPS_PER_CYCLE" ] && echo "FLOPS_PER_CYCLE not provided (no GFLOPS and efficiencies)"


export BLAS_NAME SYSTEM_NAME NAME KERNEL_HEADERS
export BACKEND BACKEND_HEADER BACKEND_OPTIONS
export PAPI_COUNTERS_MAX PAPI_COUNTERS_AVAIL
export FLOPS_PER_CYCLE DFLOPS_PER_CYCLE SFLOPS_PER_CYCLE 
export CPU_MODEL FREQUENCY_MHZ NT_MAX

target_dir=build/$NAME

cfg_h=$target_dir/cfg.h
kernel_h=$target_dir/kernels.h
sigs_c_inc=$target_dir/sigs.c.inc
calls_c_inc=$target_dir/calls.c.inc
info_py=$target_dir/info.py

# clean previous build
rm -r $target_dir

# craete buld directory
mkdir -p $target_dir

# create headers file
src/create_header.py > $kernel_h

# create aux files
$CC $CFLAGS -E -I. $kernel_h | src/create_incs.py $cfg_h $kernel_h $sigs_c_inc $calls_c_inc $info_py

# build .o
for x in main CallParser MemoryManager Sampler Signature; do
    $CXX $CXXFLAGS $INCLUDE_FLAGS -I. -c -D CFG_H="\"$cfg_h\"" src/$x.cpp -o $target_dir/$x.o
done

# build sample.o
$CC $CFLAGS $INCLUDE_FLAGS -I. -c -D CFG_H="\"$cfg_h\"" src/sample.c -o $target_dir/sample.o

# build sampler
$CXX $CXXFLAGS $LINK_FLAGS $target_dir/*.o -o $target_dir/sampler.x
