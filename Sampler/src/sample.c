#include "sample.h"

#ifdef PAPI
#include <papi.h>
#endif

#define rdtsc(var) { \
    unsigned int __a, __d; \
    asm volatile("rdtsc" : "=a" (__a), "=d" (__d)); \
    var = ((unsigned long) __a) | (((unsigned long) __d) << 32); \
} while(0)

void sample_nopapi(KernelCall *calls, size_t ncalls) {
#define COUNTERS_START() rdtsc(ticks0);
#define COUNTERS_END()   rdtsc(ticks1);
    int i;
    for (i = 0; i < ncalls; i++) {
        void **argv = calls[i].argv;
        unsigned long ticks0, ticks1; 
        switch (calls[i].argc) {
#include CALLS_C_INC
        }
        calls[i].rdtsc = ticks1 - ticks0;
    }
#undef COUNTERS_START
#undef COUNTERS_END
}

#ifdef PAPI
void sample_papi(KernelCall *calls, size_t ncalls, int *counters, int ncounters) {
#define COUNTERS_START() PAPI_start_counters(counters, ncounters); rdtsc(ticks0);
#define COUNTERS_END()   rdtsc(ticks1); PAPI_stop_counters(calls[i].counters, ncounters);
    int i;
    for (i = 0; i < ncalls; i++) {
        void **argv = calls[i].argv;
        unsigned long ticks0, ticks1; 
        switch (calls[i].argc) {
#include CALLS_C_INC
        }
        calls[i].rdtsc = ticks1 - ticks0;
    }
#undef COUNTERS_START
#undef COUNTERS_END
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
