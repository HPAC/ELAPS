#include "gerand.h"

#include <stdlib.h>

void sgerand(int *m, int *n, float *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = ((float) rand()) / RAND_MAX;
}

void dgerand(int *m, int *n, double *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = ((double) rand()) / RAND_MAX;
}

void cgerand(int *m, int *n, float *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = ((float) rand()) / RAND_MAX;
            A[2 * (i + j * *ldA)] = ((float) rand()) / RAND_MAX;
        }
}

void zgerand(int *m, int *n, double *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
            A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
        }
}
