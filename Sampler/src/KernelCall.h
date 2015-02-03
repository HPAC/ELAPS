#ifndef KERNELCALL_H
#define KERNELCALL_H

#include CFG_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    char argc;
    void *argv[KERNEL_MAX_ARGS + 1];
#ifdef _OPENMP
    char parallel;
#endif
    unsigned long rdtsc;
#ifdef PAPI
    long long counters[MAX_COUNTERS];
#endif
} KernelCall;

#ifdef __cplusplus
}
#endif

#endif /* KERNELCALL_H */
