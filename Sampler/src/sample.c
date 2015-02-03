#include "sample.h"

#ifdef PAPI
#include <papi.h>
#endif

// read time stamp counter (CPU register)
#define rdtsc(var) { \
    unsigned int __a, __d; \
    asm volatile("rdtsc" : "=a" (__a), "=d" (__d)); \
    var = ((unsigned long) __a) | (((unsigned long) __d) << 32); \
} while(0)

////////////////////////////////////////////////////////////////////////////////
// no PAPI                                                                    //
////////////////////////////////////////////////////////////////////////////////

#define COUNTERS_START0 rdtsc(ticks0);
#define COUNTERS_END0   rdtsc(ticks1);

void sample_nopapi_noomp(KernelCall *calls, size_t ncalls) {
    // for each call
    int i;
    for (i = 0; i < ncalls; i++) {
        void **argv = calls[i].argv;
        unsigned long ticks0, ticks1; 

        // start and end counters
#define COUNTERS_START COUNTERS_START0
#define COUNTERS_END COUNTERS_END0

        // branch depending on #arguments
        // (actual routine invocations are automatically generated depending on
        // the number of arguments)
        switch (calls[i].argc) {
#include CALLS_C_INC
        }

        // compute rdtsc dfference (time)
        calls[i].rdtsc = ticks1 - ticks0;

        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
    }
}

#ifdef _OPENMP
void sample_nopapi_omp(KernelCall *calls, size_t ncalls) {
#pragma omp parallel
    {
#pragma omp single nowait
        {
            unsigned long ticks0, ticks1; 
            char lastparallel = 0;
            // for each call
            int i;
            for (i = 0; i < ncalls; i++) {
                void **argv = calls[i].argv;
                if (lastparallel) {
                    if (calls[i].parallel) {
                        // start task, no counters
#define COUNTERS_START _Pragma("omp task")
#define COUNTERS_END

                        // branch depending on #arguments
                        switch (calls[i].argc) {
#include CALLS_C_INC
                        }

                        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
                    } else {
                        // wait for tasks, end counters
#define COUNTERS_START
#define COUNTERS_END   _Pragma("omp taskwait") COUNTERS_END0

                        // branch depending on #arguments
                        switch (calls[i].argc) {
#include CALLS_C_INC
                        }

                        // compute rdtsc dfference (time)
                        calls[i].rdtsc = ticks1 - ticks0;

                        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
                    }
                } else {
                    if (calls[i].parallel) {
                        // start tasks, start counters
#define COUNTERS_START COUNTERS_START0 _Pragma("omp task")
#define COUNTERS_END

                        // branch depending on #arguments
                        switch (calls[i].argc) {
#include CALLS_C_INC
                        }

                        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
                    } else {
                        // no tasks, start and end counters
#define COUNTERS_START COUNTERS_START0
#define COUNTERS_END   COUNTERS_END0

                        // branch depending on #arguments
                        switch (calls[i].argc) {
#include CALLS_C_INC
                        }

                        // compute rdtsc dfference (time)
                        calls[i].rdtsc = ticks1 - ticks0;

                        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
                    }
                }
                lastparallel = calls[i].parallel;
            }
        }
    }
}
#endif /* _OPENMP */

// clean macros
#undef COUNTERS_START0
#undef COUNTERS_END0

////////////////////////////////////////////////////////////////////////////////
// PAPI                                                                       //
////////////////////////////////////////////////////////////////////////////////
//
#define COUNTERS_START0 PAPI_start_counters(counters, ncounters); rdtsc(ticks0);
#define COUNTERS_END0   rdtsc(ticks1); PAPI_stop_counters(calls[i].counters, ncounters);

#ifdef PAPI
void sample_papi_noomp(KernelCall *calls, size_t ncalls, int *counters, int ncounters) {
    // macros start and end everywhere
#define COUNTERS_START COUNTERS_START0
#define COUNTERS_END COUNTERS_END0
    // for each call
    int i;
    for (i = 0; i < ncalls; i++) {
        void **argv = calls[i].argv;
        unsigned long ticks0, ticks1; 

        // branch depending on #arguments
        switch (calls[i].argc) {
            // actual routine invocations are 
            // automatically generated depending on the number of arguments
#include CALLS_C_INC
        }

        // compute rdtsc dfference (time)
        calls[i].rdtsc = ticks1 - ticks0;
    }
}

#ifdef _OPENMP
void sample_nopapi_omp(KernelCall *calls, size_t ncalls) {
#pragma omp parallel
    {
#pragma omp single nowait
        {
            unsigned long ticks0, ticks1; 
            char lastparallel = 0;
            // for each call
            int i;
            for (i = 0; i < ncalls; i++) {
                void **argv = calls[i].argv;
                if (lastparallel) {
                    if (calls[i].parallel) {
                        // start task, no counters
#define COUNTERS_START _Pragma("omp task")
#define COUNTERS_END

                        // branch depending on #arguments
                        switch (calls[i].argc) {
#include CALLS_C_INC
                        }

                        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
                    } else {
                        // wait for tasks, end counters
#define COUNTERS_START
#define COUNTERS_END   _Pragma("omp taskwait") COUNTERS_END0

                        // branch depending on #arguments
                        switch (calls[i].argc) {
#include CALLS_C_INC
                        }

                        // compute rdtsc dfference (time)
                        calls[i].rdtsc = ticks1 - ticks0;

                        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
                    }
                } else {
                    if (calls[i].parallel) {
                        // start tasks, start counters
#define COUNTERS_START COUNTERS_START0 _Pragma("omp task")
#define COUNTERS_END

                        // branch depending on #arguments
                        switch (calls[i].argc) {
#include CALLS_C_INC
                        }

                        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
                    } else {
                        // no tasks, start and end counters
#define COUNTERS_START COUNTERS_START0
#define COUNTERS_END   COUNTERS_END0

                        // branch depending on #arguments
                        switch (calls[i].argc) {
#include CALLS_C_INC
                        }

                        // compute rdtsc dfference (time)
                        calls[i].rdtsc = ticks1 - ticks0;

                        // clean macros
#undef COUNTERS_START
#undef COUNTERS_END
                    }
                }
                lastparallel = calls[i].parallel;
            }
        }
    }
}
#endif /* _OPENMP */

#endif /* PAPI */

// clean macros
#undef COUNTERS_START0
#undef COUNTERS_END0

////////////////////////////////////////////////////////////////////////////////
// branching for PAPI and _OPENMP                                             //
////////////////////////////////////////////////////////////////////////////////

void sample_nopapi(KernelCall *calls, size_t ncalls) {
#ifdef _OPENMP
    // TODO: branch to noomp if no parallel is set
    sample_nopapi_omp(calls, ncalls);
#else
    sample_nopapi_noomp(calls, ncalls);
#endif /* _OPENMP */
}

#ifdef _PAPI
void sample_papi(KernelCall *calls, size_t ncalls, int *counters, int ncounters) {
#ifdef _OPENMP
    // TODO: branch to noomp if no parallel is set
    sample_papi_omp(calls, ncalls, counters, ncounters);
#else
    sample_papi_noomp(calls, ncalls, counters, ncounters);
#endif /* _OPENMP */
}
#endif /* _PAPI */

#ifdef _PAPI
void sample(KernelCall *calls, size_t ncalls, int *counters, int ncounters) {
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
