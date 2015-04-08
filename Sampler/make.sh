#!/bin/bash

[ "$#" -eq 0 ] && echo "usage: $0 config_file" && exit

# load config file
[ ! -e $1 ] && echo "no such file: $1" && exit
. $1

# set default values
: ${NAME:=`basename "$1" .cfg`}
: ${TARGET_DIR:="build/$NAME"}
[ -z "$BLAS_NAME" ] && echo "BLAS_NAME is not set" && exit
: ${SYSTEM_NAME:="local"}
: ${NCORES:=1}
: ${THREADS_PER_CORE:=1}
: ${CC:=gcc}
[ "$CC" == "gcc" ] && : ${CFLAGS:="-fopenmp"} || : {$CFLAGS:=""}
: ${CXX:=g++}
[ "$CXX" == "g++" ] && : ${CXXFLAGS:="-fopenmp"} || : ${CXXFLAGS:=""}
: ${LINK_FLAGS:=""}
: ${INCLUDE_FLAGS:=""}
: ${KERNEL_HEADERS:=`echo ../resources/headers/{blas_,lapack_,utility}.h`}
: ${OPENMP:=1}
: ${PAPI_COUNTERS_MAX:=0}
: ${PAPI_COUNTERS_AVAIL:=""}
: ${BACKEND:="local"}
: ${BACKEND_HEADER:=""}
: ${BACKEND_PREFIX:=""}
: ${BACKEND_SUFFIX:=""}
: ${BACKEND_FOOTER:=""}

export TARGET_DIR NAME BLAS_NAME SYSTEM_NAME KERNEL_HEADERS
export BACKEND BACKEND_HEADER BACKEND_PREFIX BACKEND_SUFFIX BACKEND_FOOTER
export PAPI_COUNTERS_MAX PAPI_COUNTERS_AVAIL OPENMP
export DFLOPS_PER_CYCLE SFLOPS_PER_CYCLE 
export CPU_MODEL FREQUENCY_HZ NCORES THREADS_PER_CORE

# set paths
cfg_h=$TARGET_DIR/cfg.h
kernel_h=$TARGET_DIR/kernels.h
sigs_c_inc=$TARGET_DIR/sigs.c.inc
calls_c_inc=$TARGET_DIR/calls.c.inc
info_py=$TARGET_DIR/info.py

# clean previous build
rm -rf $TARGET_DIR

# craete buld directory
mkdir -p $TARGET_DIR

# create headers file
src/create_header.py > $kernel_h

# create aux files
$CC $CFLAGS -E -I. $kernel_h | src/create_incs.py $cfg_h $kernel_h $sigs_c_inc $calls_c_inc $info_py || exit

defines=-D\ CFG_H="\"$cfg_h\""
[ "$OPENMP" == "1" ] && defines+=" -D OPENMP_ENABLED"
[ "$PAPI_COUNTERS_MAX" -gt 0 ] && defines+=" -D PAPI_ENABLED"

# build .o
for x in main CallParser MemoryManager Sampler Sampler_utility Signature; do
    $CXX $CXXFLAGS $INCLUDE_FLAGS -I. -c $defines src/$x.cpp -o $TARGET_DIR/$x.o || exit
done

# build kernels
mkdir $TARGET_DIR/kernels
for file in kernels/*.c; do
    $CC $CFLAGS -c $file -o $TARGET_DIR/${file%.c}.o || exit
done

# build sample.o
$CC $CFLAGS $INCLUDE_FLAGS -I. -c $defines src/sample.c -o $TARGET_DIR/sample.o || exit

# build sampler
$CXX $CXXFLAGS $TARGET_DIR/*.o $TARGET_DIR/kernels/*.o -o $TARGET_DIR/sampler.x $LINK_FLAGS || exit
