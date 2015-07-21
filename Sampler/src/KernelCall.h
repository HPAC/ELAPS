#ifndef KERNELCALL_H
#define KERNELCALL_H

#include CFG_H

#ifdef __cplusplus
extern "C" {
#endif

/** Minimal kernel call structure for the sampling process. */
typedef struct {

    /** Function pointer. */
    void (*fptr)();

    /** Number of arguments (including routine name). */
    char argc;

    /** Argument pointers. */
    void *argv[KERNEL_MAX_ARGS];

#ifdef OPENMP_ENABLED
    /** Call is in parallel with next call. */
    char parallel;
#endif

    /** After execution: measured number of clock cycles. */
    unsigned long cycles;

#ifdef PAPI_ENABLED
    /** After execution: measured PAPI counter values. */
    long long counters[MAX_COUNTERS];
#endif
} KernelCall;

#ifdef __cplusplus
}
#endif

#endif /* KERNELCALL_H */
