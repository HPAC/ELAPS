#include "sample.h"

#include CFG_H

#ifdef PAPI_ENABLED
#include <papi.h>
#endif

// make sure omp flags are set
#ifdef OPENMP_ENABLED
#ifndef _OPENMP
#error "Compiler doesn't have OpenMP!"
#endif
#endif

#ifdef __x86_64__
#define get_cycles(var) { \
    unsigned long int lower, upper; \
    __asm__ volatile ("rdtsc" : "=a" (lower), "=d" (upper)); \
    var = ((unsigned long long) lower) | (((unsigned long long) upper) << 32); \
} while(0)
#elif defined(__powerpc__)
#define get_cycles(var) { \
    unsigned long int lower, upper, tmp; \
    __asm__ volatile ( \
        "0:\n" \
        "\tmftbu   %0\n" \
        "\tmftb    %1\n" \
        "\tmftbu   %2\n" \
        "\tcmpw    %2,%0\n" \
        "\tbne     0b\n" \
        : "=r"(upper),"=r"(lower),"=r"(tmp) \
    ); \
    var = ((unsigned long long) lower) | (((unsigned long long) upper) << 32); \
} while(0)
#endif


#define COUNTERS_START0 get_cycles(ticks0);
#define COUNTERS_END0   get_cycles(ticks1);

/** \ref sample specialization without PAPI and without OpenMP. */
static void sample_nopapi_noomp(KernelCall *calls, size_t ncalls) {
    // for each call
    size_t i;
    for (i = 0; i < ncalls; i++) {
        void (*fptr)() = calls[i].fptr;
        const size_t argc = calls[i].argc;
        void **argv = calls[i].argv;
        unsigned long ticks0 = 0, ticks1 = 0;

        // start and end counters
#define COUNTERS_START COUNTERS_START0
#define COUNTERS_END COUNTERS_END0

        // branch depending on #arguments
        // (actual routine invocations are automatically generated depending on
        // the number of arguments)
        switch (argc) {
#include CALLS_C_INC
        }

        // compute cycle count difference (time)
        calls[i].cycles = ticks1 - ticks0;

        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
    }
}

#ifdef OPENMP_ENABLED
/** \ref sample specialization with OpenMP but without PAPI. */
static void sample_nopapi_omp(KernelCall *calls, size_t ncalls) {
    unsigned long ticks0 = 0, ticks1 = 0;
    // for each call
    size_t i, nseq, lastpar, j;
    for (i = 0; i < ncalls; i++) {

        // count how many sequential regions are executed in parallel
        nseq = 1;
        for (lastpar = i; calls[lastpar].parallel; lastpar++)
            nseq += !calls[lastpar].sequential;

        if (lastpar > i) {
            // parallel calls
#define COUNTERS_START
#define COUNTERS_END

            // time parallel for loop
            const int i_start = i;
            COUNTERS_START0
#pragma omp parallel for
            for (j = 1; j <= nseq; j++) {
                int seqcounter = 1;

                // each thread checks all calls
                for (i = i_start; i <= lastpar; i++) {
                    if (j == seqcounter) {
                        // thread needs to execute this call
                        void (*fptr)() = calls[i].fptr;
                        const size_t argc = calls[i].argc;
                        void **argv = calls[i].argv;

                        // branch depending on #arguments
                        switch (argc) {
#include CALLS_C_INC
                        }
                    }

                    // increment sequential region counter
                    seqcounter += !calls[i].sequential;
                }
            }
            COUNTERS_END0

            i = lastpar;

            // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
        } else {
            // normal call
#define COUNTERS_START COUNTERS_START0
#define COUNTERS_END   COUNTERS_END0

            void (*fptr)() = calls[i].fptr;
            const size_t argc = calls[i].argc;
            void **argv = calls[i].argv;

            // branch depending on #arguments
            switch (argc) {
#include CALLS_C_INC
            }

            // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
        }

        // compute cycle count difference (time)
        calls[i].cycles = ticks1 - ticks0;
    }
}
#endif /* OMP */

// clean macros
#undef COUNTERS_START0
#undef COUNTERS_END0

////////////////////////////////////////////////////////////////////////////////
// PAPI                                                                       //
////////////////////////////////////////////////////////////////////////////////
#ifdef PAPI_ENABLED

#define COUNTERS_START0 PAPI_start_counters(counters, (int) ncounters); get_cycles(ticks0);
#define COUNTERS_END0   get_cycles(ticks1); PAPI_stop_counters(calls[i].counters, (int) ncounters);

/** \ref sample specialization with PAPI but without OpenMP. */
static void sample_papi_noomp(KernelCall *calls, size_t ncalls, int *counters, size_t ncounters) {
    // for each call
    size_t i;
    for (i = 0; i < ncalls; i++) {
        void (*fptr)() = calls[i].fptr;
        const size_t argc = calls[i].argc;
        void **argv = calls[i].argv;
        unsigned long ticks0 = 0, ticks1 = 0;

    // start and end counters
#define COUNTERS_START COUNTERS_START0
#define COUNTERS_END COUNTERS_END0

        // branch depending on #arguments
        // actual routine invocations are
        // automatically generated depending on the number of arguments
        switch (argc) {
#include CALLS_C_INC
        }

        // compute cycle count difference (time)
        calls[i].cycles = ticks1 - ticks0;

        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
    }
}

#ifdef OPENMP_ENABLED
/** \ref sample specialization with PAPI and OpenMP. */
static void sample_papi_omp(KernelCall *calls, size_t ncalls, int *counters, size_t ncounters) {
    unsigned long ticks0 = 0, ticks1 = 0;
    // for each call
    size_t i, nseq, lastpar, j;
    for (i = 0; i < ncalls; i++) {

        // count how many sequential regions are executed in parallel
        nseq = 1;
        for (lastpar = i; calls[lastpar].parallel; lastpar++)
            nseq += !calls[lastpar].sequential;

        if (lastpar > i) {
            // parallel calls
#define COUNTERS_START
#define COUNTERS_END

            // time parallel for loop
            const int i_start = i;
            COUNTERS_START0
#pragma omp parallel for
            for (j = 1; j <= nseq; j++) {
                int seqcounter = 1;

                // each thread checks all calls
                for (i = i_start; i <= lastpar; i++) {
                    if (j == seqcounter) {
                        // thread needs to execute this call
                        void (*fptr)() = calls[i].fptr;
                        const size_t argc = calls[i].argc;
                        void **argv = calls[i].argv;

                        // branch depending on #arguments
                        switch (argc) {
#include CALLS_C_INC
                        }
                    }

                    // increment sequential region counter
                    seqcounter += !calls[i].sequential;
                }
            }
            COUNTERS_END0

            i = lastpar;

            // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
        } else {
            // sequential call
#define COUNTERS_START COUNTERS_START0
#define COUNTERS_END   COUNTERS_END0

            void (*fptr)() = calls[i].fptr;
            const size_t argc = calls[i].argc;
            void **argv = calls[i].argv;

            // branch depending on #arguments
            switch (argc) {
#include CALLS_C_INC
            }

            // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
        }

        // compute cycle count difference (time)
        calls[i].cycles = ticks1 - ticks0;
    }
}
#endif /* OMP */


#endif /* PAPI */

// clean macros
#undef COUNTERS_START0
#undef COUNTERS_END0

/** \ref sample specialization without PAPI.
 * Forks into \ref sample_nopapi_omp an \ref sample_nopapi_noomp.
 * */
static void sample_nopapi(KernelCall *calls, size_t ncalls) {
#ifdef OPENMP_ENABLED
    size_t i;
    for (i = 0; i < ncalls; i++)
        if (calls[i].parallel)
            break;
    if (i < ncalls)
        sample_nopapi_omp(calls, ncalls);
    else
        sample_nopapi_noomp(calls, ncalls);
#else
    sample_nopapi_noomp(calls, ncalls);
#endif /* OPENMP_ENABLED */
}

#ifdef PAPI_ENABLED
/** \ref sample specialization with PAPI.
 * Forks into \ref sample_papi_omp an \ref sample_papi_noomp.
 * */
static void sample_papi(KernelCall *calls, size_t ncalls, int *counters, size_t ncounters) {
#ifdef OPENMP_ENABLED
    size_t i;
    for (i = 0; i < ncalls; i++)
        if (calls[i].parallel)
            break;
    if (i < ncalls)
        sample_papi_omp(calls, ncalls, counters, ncounters);
    else
        sample_papi_noomp(calls, ncalls, counters, ncounters);
#else
    sample_papi_noomp(calls, ncalls, counters, ncounters);
#endif /* OPENMP_ENABLED */
}
#endif /* _PAPI */

#ifdef PAPI_ENABLED
void sample(KernelCall *calls, size_t ncalls, int *counters, size_t ncounters) {
    if (ncounters > 0)
        sample_papi(calls, ncalls, counters, ncounters);
    else
        sample_nopapi(calls, ncalls);
}
#else
void sample(KernelCall *calls, size_t ncalls) {
    sample_nopapi(calls, ncalls);
}
#endif /* PAPI */
