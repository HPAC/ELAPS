#!/bin/bash

# parse arguments
LINK_ONLY=0
while getopts lv opt; do
    case $opt in
        l)
            LINK_ONLY=1
            ;;
        v)
            VERBOSE="set -x"
            NOVERBOSE="exit"
            ;;
    esac
done
shift $((OPTIND-1))
[ "$#" -eq 0 ] && echo "usage: $0 [-l] [-v] config_file" && exit
CFG_FILE=$1

# load config file
[ ! -e "$CFG_FILE" ] && echo "no such file: $CFG_FILE" && exit
. "$CFG_FILE"

# set default values
: ${NAME:="`basename \"$1\" .cfg`"}
: ${TARGET_DIR:="build/$NAME"}
: ${NCORES:=1}
: ${THREADS_PER_CORE:=1}
: ${CC:=gcc}
[ "$CC" == "gcc" ] && : ${CFLAGS:="-fopenmp -O3"} || : {$CFLAGS:="-O3"}
: ${CXX:=g++}
[ "$CXX" == "g++" ] && : ${CXXFLAGS:="-fopenmp -O3"} || : ${CXXFLAGS:="-O3"}
: ${LINK_FLAGS:=""}
: ${INCLUDE_FLAGS:=""}
: ${KERNEL_HEADERS:="`echo ../resources/headers/{blas,lapack,utility}.h`"}
: ${BLAS_UNDERSCORE:=1}
: ${BLAS_COMPLEX_FUNCTIONS_AS_ROUTINES:=0}
: ${LAPACK_UNDERSCORE:=1}
: ${LAPACK_COMPLEX_FUNCTIONS_AS_ROUTINES:=0}
: ${OPENMP:=1}
: ${PAPI_COUNTERS_MAX:=0}
: ${PAPI_COUNTERS_AVAIL:=""}
: ${BACKEND:="local"}
: ${BACKEND_HEADER:=""}
: ${BACKEND_PREFIX:=""}
: ${BACKEND_SUFFIX:=""}
: ${BACKEND_FOOTER:=""}
[ -n "$DFLOPS_PER_CYCLE" ] && : ${SFLOPS_PER_CYCLE:=$((DFLOPS_PER_CYCLE * 2))}
[ -n "$SFLOPS_PER_CYCLE" ] && : ${DFLOPS_PER_CYCLE:=$((SFLOPS_PER_CYCLE / 2))}

# use absolute paths and remove newlines
TARGET_DIR="`readlink -f \"$TARGET_DIR\"`"
KERNEL_HEADERS="`for f in $KERNEL_HEADERS; do readlink -f $f; done | tr '\r\n' ' '`"
LINK_FLAGS="`echo $LINK_FLAGS | tr '\r\n' ' '`"

export TARGET_DIR NAME KERNEL_HEADERS 
export BLAS_UNDERSCORE BLAS_COMPLEX_FUNCTIONS_AS_ROUTINES
export LAPACK_UNDERSCORE LAPACK_COMPLEX_FUNCTIONS_AS_ROUTINES
export BACKEND BACKEND_HEADER BACKEND_PREFIX BACKEND_SUFFIX BACKEND_FOOTER
export PAPI_COUNTERS_MAX PAPI_COUNTERS_AVAIL OPENMP
export DFLOPS_PER_CYCLE SFLOPS_PER_CYCLE 
export CPU_MODEL FREQUENCY_HZ NCORES THREADS_PER_CORE

# print info
echo "Building Sampler  $NAME"
echo "build folder:     $TARGET_DIR"
echo "CPU (Hz):         $CPU_MODEL ($FREQUENCY_HZ)"
echo "#cores:           $NCORES"
echo "threads/core:     $THREADS_PER_CORE"
echo "flops/cycle:      $SFLOPS_PER_CYCLE (single) / $DFLOPS_PER_CYCLE (double)"
echo "headers:          $KERNEL_HEADERS"
if [ "${KERNEL_HEADERS/blas}" != "$KERNEL_HEADERS" ]; then
    echo -n "BLAS format:      "
    [ $BLAS_UNDERSCORE == 1 ] && echo "dgemm_" || echo "dgemm"
    [ $BLAS_COMPLEX_FUNCTIONS_AS_ROUTINES == 1 ] && \
        echo "                  complex functions are routines (e.g., cladiv)"
fi
if [ "${KERNEL_HEADERS/lapack}" != "$KERNEL_HEADERS" ]; then
    echo -n "LAPACK format:    "
    [ $LAPACK_UNDERSCORE == 1 ] && echo "dgetrf_" || echo "dgetrf"
    [ $LAPACK_COMPLEX_FUNCTIONS_AS_ROUTINES == 1 ] && \
        echo "                  complex functions are routines (e.g., cladiv)"
fi
echo "C compiler:       $CC $CFLAGS"
echo "C++ compiler:     $CXX $CXXFLAGS"
echo "include flags:    $INCLUDE_FLAGS"
echo "linker flags:     $LINK_FLAGS"
echo -n "OpenMP:           "
[ $OPENMP -eq 1 ] && echo "Enabled" || echo "Disabled"
if [ $PAPI_COUNTERS_MAX -eq 0 ]; then
    echo "PAPI:             Disabled"
else
    echo "#PAPI counters:   $PAPI_COUNTERS_MAX"
    echo "PAPI counters:    $PAPI_COUNTERS_AVAIL"
fi
echo "backend:          $BACKEND"
[ -z "$BACKEND_HEADER" ] || echo "backend header:   $BACKEND_HEADER"
[ -z "$BACKEND_PREFIX" ] || echo "backend prefix:   $BACKEND_PREFIX"
[ -z "$BACKEND_SUFFIX" ] || echo "backend suffix:   $BACKEND_SUFFIX"
[ -z "$BACKEND_FOOTER" ] || echo "backend footer:   $BACKEND_FOOTER"
[ -z "$VERBOSE" ] || echo ""

# set paths
cfg_h="$TARGET_DIR/cfg.h"
kernels_h="$TARGET_DIR/kernels.h"
sigs_cpp_inc="$TARGET_DIR/sigs.cpp.inc"
calls_c_inc="$TARGET_DIR/calls.c.inc"
info_py="$TARGET_DIR/info.py"

if [ $LINK_ONLY -ne 1 ]; then
    # -------------------- CONFIGURING --------------------
    ( $NOVERBOSE; echo -n "configuring " )

    # clean previous build
    ( $VERBOSE; rm -rf "$TARGET_DIR" )
    ( $NOVERBOSE; echo -n "." )

    # craete buld directory
    ( $VERBOSE; mkdir -p "$TARGET_DIR" )
    ( $NOVERBOSE; echo -n "." )

    # create headers file
    ( $VERBOSE; src/create_header.py > "$kernels_h" ) || exit
    ( $NOVERBOSE; echo -n "." )

    # create aux files
    ( $VERBOSE; $CC $CFLAGS -E -I. "$kernels_h" | src/create_incs.py "$cfg_h" "$kernels_h" "$sigs_cpp_inc" "$calls_c_inc" "$info_py" ) || exit
    ( $NOVERBOSE; echo -n "." )

    # -------------------- COMPILING --------------------
    ( $NOVERBOSE; echo -n " compiling " )

    # build C++ .o
    for x in main CallParser MemoryManager Sampler Signature; do
        ( $VERBOSE; $CXX $CXXFLAGS $INCLUDE_FLAGS -I. -c -D CFG_H="\"$cfg_h\"" src/$x.cpp -o "$TARGET_DIR/$x.o" ) || exit
        ( $NOVERBOSE; echo -n "." )
    done

    # build utility kernels
    ( $VERBOSE; mkdir "$TARGET_DIR/kernels" )
    for file in kernels/*.c; do
        ( $VERBOSE; $CC $CFLAGS -c $file -o "$TARGET_DIR/${file%.c}.o" ) || exit
        ( $NOVERBOSE; echo -n "." )
    done

    # build sample.o
    ( $VERBOSE; $CC $CFLAGS $INCLUDE_FLAGS -I. -c -D CFG_H="\"$cfg_h\"" src/sample.c -o "$TARGET_DIR/sample.o" ) || exit
    ( $NOVERBOSE; echo -n ". " )
fi

# -------------------- LINKING --------------------
( $NOVERBOSE; echo -n "linking " )

# link sampler.x
( $VERBOSE; $CXX $CXXFLAGS "$TARGET_DIR/"*.o "$TARGET_DIR/kernels/"*.o -o "$TARGET_DIR/sampler.x" $LINK_FLAGS ) || exit
( $NOVERBOSE; echo ". done!" )
