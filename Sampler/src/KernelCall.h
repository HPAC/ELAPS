#ifndef KERNELCALL_H
#define KERNELCALL_H

#include CFG_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    char argc;
    void *argv[KERNEL_MAX_ARGS + 1];
#ifdef OPENMP_ENABLED
    char parallel;
#endif
    unsigned long cycles;
#ifdef PAPI_ENABLED
    long long counters[MAX_COUNTERS];
#endif
} KernelCall;

#ifdef __cplusplus
}
#endif

#endif /* KERNELCALL_H */
