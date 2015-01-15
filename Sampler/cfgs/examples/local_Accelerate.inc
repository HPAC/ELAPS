#!/bin/bash

BLAS_NAME="Accelerate"
SYSTEM_NAME="local"

LINK_FLAGS="-framework Accelerate"
INCLUDE_FLAGS=""
KERNEL_HEADERS="headers/blas.h headers/lapack.h"
CXXFLAGS="-g -Wall"
CFLAGS="-g -Wall"

BACKEND_HEADER="export VECLIB_MAXIMUM_THREADS={nt}"

NT_MAX=2
FREQUENCY_MHZ=2000
CPU_MODEL="Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz"
FLOPS_PER_CYCLE=8
