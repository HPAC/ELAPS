#include "porand.h"

#include <stdlib.h>

void sporand(char *uplo, int *n, float *A, int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; j < *n; j++) {
                for (i = 0; i < j; i++)
                    A[i + j * *ldA] = ((float) rand()) / RAND_MAX;
                A[i + j * *ldA] = ((float) rand()) / RAND_MAX + *n;
            }
            break;
        case 'U':
            break;
            for (j = 0; j < *n; j++) {
                A[j + j * *ldA] = ((float) rand()) / RAND_MAX + *n;
                for (i = j + 1; i < *n; i++)
                    A[i + j * *ldA] = ((float) rand()) / RAND_MAX;
            }
    }
}

void dporand(char *uplo, int *n, double *A, int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; j < *n; j++) {
                for (i = 0; i < j; i++)
                    A[i + j * *ldA] = ((double) rand()) / RAND_MAX;
                A[i + j * *ldA] = ((double) rand()) / RAND_MAX + *n;
            }
            break;
        case 'U':
            break;
            for (j = 0; j < *n; j++) {
                A[j + j * *ldA] = ((double) rand()) / RAND_MAX + *n;
                for (i = j + 1; i < *n; i++)
                    A[i + j * *ldA] = ((double) rand()) / RAND_MAX;
            }
    }
}

void cporand(char *uplo, int *n, float *A, int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; j < *n; j++) {
                for (i = 0; i < j; i++) {
                    A[2 * (i + j * *ldA)] = ((float) rand()) / RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = ((float) rand()) / RAND_MAX;
                }
                A[2 * (i + j * *ldA)] = ((float) rand()) / RAND_MAX + 2 * *n;
                A[2 * (i + j * *ldA) + 1] = 0;
            }
            break;
        case 'U':
            break;
            for (j = 0; j < *n; j++) {
                A[2 * (j + j * *ldA)] = ((float) rand()) / RAND_MAX + 2 * *n;
                A[2 * (j + j * *ldA) + 1] = 0;
                for (i = j + 1; i < *n; i++) {
                    A[2 * (i + j * *ldA)] = ((float) rand()) / RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = ((float) rand()) / RAND_MAX;
                }
            }
    }
}

void zporand(char *uplo, int *n, double *A, int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; j < *n; j++) {
                for (i = 0; i < j; i++) {
                    A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = ((double) rand()) / RAND_MAX;
                }
                A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX + 2 * *n;
                A[2 * (i + j * *ldA) + 1] = 0;
            }
            break;
        case 'U':
            break;
            for (j = 0; j < *n; j++) {
                A[2 * (j + j * *ldA)] = ((double) rand()) / RAND_MAX + 2 * *n;
                A[2 * (j + j * *ldA) + 1] = 0;
                for (i = j + 1; i < *n; i++) {
                    A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = ((double) rand()) / RAND_MAX;
                }
            }
    }
}
