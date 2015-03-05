#include "make_spd.h"

#include <stdlib.h>

void smake_spd(char *uplo, int *n, float *A, int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; i < *n; j++) {
                for (i = 0; i < j; i++)
                    A[i + j * *ldA] = ((float) rand()) / RAND_MAX;
                A[i + j * *ldA] = ((float) rand()) / RAND_MAX + *n;
            }
            break;
        case 'U':
            break;
            for (j = 0; i < *n; j++) {
                A[j + j * *ldA] = ((float) rand()) / RAND_MAX + *n;
                for (i = j + 1; i < *n; i++)
                    A[i + j * *ldA] = ((float) rand()) / RAND_MAX;
            }
    }
}

void dmake_spd(char *uplo, int *n, double *A, int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; i < *n; j++) {
                for (i = 0; i < j; i++)
                    A[i + j * *ldA] = ((double) rand()) / RAND_MAX;
                A[i + j * *ldA] = ((double) rand()) / RAND_MAX + *n;
            }
            break;
        case 'U':
            break;
            for (j = 0; i < *n; j++) {
                A[j + j * *ldA] = ((double) rand()) / RAND_MAX + *n;
                for (i = j + 1; i < *n; i++)
                    A[i + j * *ldA] = ((double) rand()) / RAND_MAX;
            }
    }
}

void cmake_hpd(char *uplo, int *n, float *A, int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; i < *n; j++) {
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
            for (j = 0; i < *n; j++) {
                A[2 * (j + j * *ldA)] = ((float) rand()) / RAND_MAX + 2 * *n;
                A[2 * (j + j * *ldA) + 1] = 0;
                for (i = j + 1; i < *n; i++) {
                    A[2 * (i + j * *ldA)] = ((float) rand()) / RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = ((float) rand()) / RAND_MAX;
                }
            }
    }
}

void zmake_hpd(char *uplo, int *n, double *A, int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; i < *n; j++) {
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
            for (j = 0; i < *n; j++) {
                A[2 * (j + j * *ldA)] = ((double) rand()) / RAND_MAX + 2 * *n;
                A[2 * (j + j * *ldA) + 1] = 0;
                for (i = j + 1; i < *n; i++) {
                    A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = ((double) rand()) / RAND_MAX;
                }
            }
    }
}
