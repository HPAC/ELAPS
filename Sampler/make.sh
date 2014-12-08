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
[ -z "$PAPI_MAX_COUNTERS" ] && PAPI_MAX_COUNTERS=0

target_dir=build/$NAME

cfg_h=$target_dir/cfg.h
kernel_h=$target_dir/kernels.h
sigs_c_inc=$target_dir/sigs.c.inc
calls_c_inc=$target_dir/calls.c.inc

# clean previous build
rm -r $target_dir

# craete buld directory
mkdir -p $target_dir

# create headers file
src/create_header.py $KERNEL_HEADERS > $kernel_h

# create aux files
$CC $CFLAGS -E -I. $kernel_h | src/create_incs.py $cfg_h $kernel_h $sigs_c_inc $calls_c_inc $PAPI_MAX_COUNTERS

# build .o
for x in main CallParser MemoryManager Sampler Signature; do
    $CXX $CXXFLAGS -I. -c -D CFG_H="\"$cfg_h\"" src/$x.cpp -o $target_dir/$x.o
done

# build sample.o
$CC $CFLAGS -I. -c -D CFG_H="\"$cfg_h\"" src/sample.c -o $target_dir/sample.o

# build sampler
$CXX $CXXFLAGS $LINK_FLAGS $target_dir/*.o -o $target_dir/sampler.x
