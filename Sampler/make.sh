#!/bin/bash

[ "$#" -eq 0 ] && echo "usage: $0 config_file" && exit

# load config file
[ ! -e $1 ] && echo "no such file: $1" && exit
. $1

# set default values
[ -z "$BLAS_NAME" ] && echo "BLAS_NAME is not set" && exit
[ -z "$SYSTEM_NAME" ] && SYSTEM_NAME="local"
[ -z "$NAME" ] && NAME=`basename "$1" .cfg`
[ -z "$NCORES" ] && NCORES=1
[ -z "$THREADS_PER_CORE" ] && THREADS_PER_CORE=1
[ -z "$CC" ] && CC="gcc"
[ -z "$CFLAGS" ] && CFLAGS=""
[ -z "$CXX" ] && CXX="g++"
[ -z "$CXXFLAGS" ] && CXXFLAGS=""
[ -z "$LINK_FLAGS" ] && LINK_FLAGS=""
[ -z "$INCLUDE_FLAGS" ] && INCLUDE_FLAGS=""
[ -z "$KERNEL_HEADERS" ] && KERNEL_HEADERS="headers/blas.h headers/lapack.h"
[ -z "$PAPI_COUNTERS_MAX" ] && PAPI_COUNTERS_MAX=0
[ -z "$PAPI_COUNTERS_AVAIL" ] && PAPI_COUNTERS_AVAIL=""
[ -z "$BACKEND" ] && BACKEND="local"
[ -z "$BACKEND_HEADER" ] && BACKEND_HEADER=""
[ -z "$BACKEND_PREFIX" ] && BACKEND_PREFIX=""
[ -z "$BACKEND_SUFFIX" ] && BACKEND_SUFFIX=""
[ -z "$BACKEND_FOOTER" ] && BACKEND_FOOTER=""

export BLAS_NAME SYSTEM_NAME NAME KERNEL_HEADERS
export BACKEND BACKEND_HEADER BACKEND_PREFIX BACKEND_SUFFIX BACKEND_FOOTER
export PAPI_COUNTERS_MAX PAPI_COUNTERS_AVAIL
export DFLOPS_PER_CYCLE SFLOPS_PER_CYCLE 
export CPU_MODEL FREQUENCY_HZ NCORES THREADS_PER_CORE

# set paths
target_dir=build/$NAME
cfg_h=$target_dir/cfg.h
kernel_h=$target_dir/kernels.h
sigs_c_inc=$target_dir/sigs.c.inc
calls_c_inc=$target_dir/calls.c.inc
info_py=$target_dir/info.py

# clean previous build
rm -rf $target_dir

# craete buld directory
mkdir -p $target_dir

# create headers file
src/create_header.py > $kernel_h

# create aux files
$CC $CFLAGS -E -I. $kernel_h | src/create_incs.py $cfg_h $kernel_h $sigs_c_inc $calls_c_inc $info_py || exit

# build .o
for x in main CallParser MemoryManager Sampler Sampler_utility Signature; do
    $CXX $CXXFLAGS $INCLUDE_FLAGS -I. -c -D CFG_H="\"$cfg_h\"" src/$x.cpp -o $target_dir/$x.o || exit
done

# build sample.o
$CC $CFLAGS $INCLUDE_FLAGS -I. -c -D CFG_H="\"$cfg_h\"" src/sample.c -o $target_dir/sample.o || exit

# build sampler
$CXX $CXXFLAGS $target_dir/*.o -o $target_dir/sampler.x $LINK_FLAGS || exit
