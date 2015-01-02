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

void sample_nopapi(KernelCall *calls, size_t ncalls) {
    // for each call
    int i;
    for (i = 0; i < ncalls; i++) {
        void **argv = calls[i].argv;
        unsigned long ticks0, ticks1; 

        // branch depending on #arguments
        switch (calls[i].argc) {
            // capture rdtsc
#define COUNTERS_START() rdtsc(ticks0);
#define COUNTERS_END()   rdtsc(ticks1);

            // actual routine invocations are 
            // automatically generated depending on the number of arguments
#include CALLS_C_INC

            // clean up macros
#undef COUNTERS_START
#undef COUNTERS_END
        }

        // compute rdtsc dfference (time)
        calls[i].rdtsc = ticks1 - ticks0;
    }
}

#ifdef PAPI
void sample_papi(KernelCall *calls, size_t ncalls, int *counters, int ncounters) {
    // for each call
    int i;
    for (i = 0; i < ncalls; i++) {
        void **argv = calls[i].argv;
        unsigned long ticks0, ticks1; 

        // branch depending on #arguments
        switch (calls[i].argc) {
            // start and stop papi counters (used in CALLS_C_INC) and capture rdtsc
#define COUNTERS_START() PAPI_start_counters(counters, ncounters); rdtsc(ticks0);
#define COUNTERS_END()   rdtsc(ticks1); PAPI_stop_counters(calls[i].counters, ncounters);

            // actual routine invocations are 
            // automatically generated depending on the number of arguments
#include CALLS_C_INC

            // clean up macros
#undef COUNTERS_START
#undef COUNTERS_END
        }

        // compute rdtsc dfference (time)
        calls[i].rdtsc = ticks1 - ticks0;
    }
}
#endif

#ifdef PAPI
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
#endif
