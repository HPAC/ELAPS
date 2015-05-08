#ifndef SAMPLE_H
#define SAMPLE_H

#include <stddef.h>

#include "KernelCall.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifdef PAPI_ENABLED
/** Sample a given list of KernelCalls.
 *
 * \param calls The list of calls.
 * \param ncalls    The number of calls.
 * \param counters  The PAPI event codes.
 * \param ncounters The number of PAPI events.
 */
void sample(KernelCall *calls, size_t ncalls, int *counters, int ncounters);
#else
void sample(KernelCall *calls, size_t ncalls);
#endif

#ifdef __cplusplus
}
#endif

#endif /* SAMPLE_H */
