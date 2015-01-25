#!/bin/bash
# Template for Sampler configuration files.
# This file will be sourced in make.sh at built time.

# Environment variables are used if available but overwritten by the variables
# in this file.
# Variables commented out have default values, which are used if they are set
# neither here nor in the environment.
# items that are only relevant for the GUI are marked [GUI]


# SYSTEM, COMPILERS and LIBRARIES

# Name of the BLAS library (e.g., "MKL", "OpenBLAS", "BLIS")
#
BLAS_NAME=

# Name of the System (e.g., "local", "cluster", "E5450")
#
#SYSTEM_NAME="local"

# Name of the Sampler
#
#NAME=#{SYSTEM_NAME}_${BLAS_NAME}

# Number of cores
#
#NT_MAX=1

# C compiler (default: "gcc")
#
#CC=

# C compiler flags (default: "")
#
#CFLAGS=

# C++ compiler (default: "g++")
#
#CXX=

# C++ compiler flags (default: "")
#
#CXXFLAGS=

# Linker flags (e.g., "-lopenblas")
#
#LINK_FLAGS=

# Include flags (e.g. "-I${PAPI_ROOT}/include)
#
#INCLUDE_FLAGS=


# KERNELS

# Header files for kernels
# Will be processed by C preprocessor.
# Should only contain function declarations.
#
#KERNEL_HEADERS="headers/blas.h headers/lapack.h"


# PAPI

# If PAPI is installed, the following information can be optained from
# papi_avail.

# Number of counters the CPU supports simmultaneously (default: 0)
# 0: disable PAPI support entirely.
# Listed as "Number Hardware Counters" in papi_avail
#
#PAPI_COUNTERS_MAX=0

# Whitespac separated list of counter names available on the system [GUI]
# e.g. "PAPI_L1_DCM PAPI_L1_ICM PAPI_L2_DCM"
#
#PAPI_COUNTERS_AVAIL=


# BACKEND

# Name of the backend for job submissions [GUI]
# Requires a match script in GUI/src/backends/${BACKEND}.py
# local: jobs run on the system runnig the GUI, i.e., the frontend.
#
#BACKEND="local"

# Header inserted at the top of job scripts [GUI]
# {nt} will be replaced by the number of threads.
# e.g.: "#BSUB -a phi"
#
#BACKEND_HEADER=

# Prefix immediately before the sampler invocation [GUI]
# {nt} will be replaced by the number of threads.
# e.g.: "OMP_NUM_THREADS={nt}"
#
#BACKEND_PREFIX=

# Suffix immediately after sampler invocation [GUI]
# {nt} will be replaced by the number of threads.
#
#BACKEND_SUFFIX=

# Footer inserted at the end of the job script [GUI]
# {nt} will be replaced by the number of threads.
#
#BACKEND_FOOTER=


# CPU INFORMATION

# These are required to e.g. compute performance and efficiencies in the GUI

# Full CPU model name [GUI]
# e.g. from /proc/cpuinfo
#
CPU_MODEL=

# CPU Frequency in MHz [GUI]
#
FREQUENCY_MHZ=

# Maximum number of double preicion floating point operations issued per cycle
# [GUI]
#
DFLOPS_PER_CYCLE=

# Maxiumum number of single precision floating point operations issued per cycle
# [GUI
#
#SFLOPS_PER_CYCLE=$((2 * DFLOPS_PER_CYCLE))
