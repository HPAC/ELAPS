#include "memset.h"

void imemset(int *m, int *n, int *alpha, int *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = *alpha;
}

void smemset(int *m, int *n, float *alpha, float *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = *alpha;
}

void dmemset(int *m, int *n, double *alpha, double *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = *alpha;
}

void cmemset(int *m, int *n, float *alpha, float *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = alpha[0];
            A[2 * (i + j * *ldA)] = alpha[1];
        }
}

void zmemset(int *m, int *n, double *alpha, double *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = alpha[0];
            A[2 * (i + j * *ldA)] = alpha[1];
        }
}
