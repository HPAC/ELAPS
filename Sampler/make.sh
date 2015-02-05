#!/bin/bash

[ "$#" -eq 0 ] && echo "usage: $0 config_file" && exit

# load config file
[ ! -e $1 ] && echo "no such file: $1" && exit
. $1

# set default values
[ -z "$BLAS_NAME" ] && echo "BLAS_NAME is not set" && exit
: ${SYSTEM_NAME:="local"}
: ${NAME:=`basename "$1" .cfg`}
: ${NCORES:=1}
: ${THREADS_PER_CORE:=1}
: ${CC:=gcc}
: ${CFLAGS:=""}
: ${CXX:=g++}
: ${CXXFLAGS:=""}
: ${LINK_FLAGS:=""}
: ${INCLUDE_FLAGS:=""}
: ${KERNEL_HEADERS:="headers/blas.h headers/lapack.h"}
: ${OPENMP:=1}
: ${PAPI_COUNTERS_MAX:=0}
: ${PAPI_COUNTERS_AVAIL:=""}
: ${BACKEND:="local"}
: ${BACKEND_HEADER:=""}
: ${BACKEND_PREFIX:=""}
: ${BACKEND_SUFFIX:=""}
: ${BACKEND_FOOTER:=""}

export BLAS_NAME SYSTEM_NAME NAME KERNEL_HEADERS
export BACKEND BACKEND_HEADER BACKEND_PREFIX BACKEND_SUFFIX BACKEND_FOOTER
export PAPI_COUNTERS_MAX PAPI_COUNTERS_AVAIL OPENMP
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

defines=-D\ CFG_H="\"$cfg_h\""
[ "$OPENMP" == "1" ] && defines+=" -D OPENMP_ENABLED"
[ "$PAPI_COUNTERS_MAX" -gt 0 ] && defines+=" -D PAPI_ENABLED"

# build .o
for x in main CallParser MemoryManager Sampler Sampler_utility Signature; do
    $CXX $CXXFLAGS $INCLUDE_FLAGS -I. -c $defines src/$x.cpp -o $target_dir/$x.o || exit
done

# build sample.o
$CC $CFLAGS $INCLUDE_FLAGS -I. -c $defines src/sample.c -o $target_dir/sample.o || exit

# build sampler
$CXX $CXXFLAGS $target_dir/*.o -o $target_dir/sampler.x $LINK_FLAGS || exit
