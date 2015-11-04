#include "porand.h"

#include <stdlib.h>

/** Randomize a single precision SPD matrix.
 * Random values taken from \f$[0, 1)\f$ (off-diagonal), \f$[0, 1) + n\f$
 * (diagonal).
 *
 * \param uplo Lower (`"L"`) or upper (`"U"`) triangular.
 * \param n Number of rows and columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void sporand(const char *uplo, const int *n, float *A, const int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; j < *n; j++) {
                for (i = 0; i < j; i++)
                    A[i + j * *ldA] = rand() / (float) RAND_MAX;
                A[j + j * *ldA] = rand() / (float) RAND_MAX + *n;
            }
            break;
        case 'U':
            for (j = 0; j < *n; j++) {
                A[j + j * *ldA] = rand() / (float) RAND_MAX + *n;
                for (i = j + 1; i < *n; i++)
                    A[i + j * *ldA] = rand() / (float) RAND_MAX;
            }
            break;
    }
}

/** Randomize a double precision SPD matrix.
 * Random values taken from \f$[0, 1)\f$ (off-diagonal), \f$[0, 1) + n\f$
 * (diagonal).
 *
 * \param uplo Lower (`"L"`) or upper (`"U"`) triangular.
 * \param n Number of rows and columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void dporand(const char *uplo, const int *n, double *A, const int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; j < *n; j++) {
                for (i = 0; i < j; i++)
                    A[i + j * *ldA] = rand() / (double) RAND_MAX;
                A[j + j * *ldA] = rand() / (double) RAND_MAX + *n;
            }
            break;
        case 'U':
            for (j = 0; j < *n; j++) {
                A[j + j * *ldA] = rand() / (double) RAND_MAX + *n;
                for (i = j + 1; i < *n; i++)
                    A[i + j * *ldA] = rand() / (double) RAND_MAX;
            }
            break;
    }
}

/** Randomize a single precision complex HPD matrix.
 * Random values taken from \f$[0, 1) + [0, 1) i\f$ (off-diagonal), \f$[0, 1) +
 * 2 n\f$ (diagonal).
 *
 * \param uplo Lower (`"L"`) or upper (`"U"`) triangular.
 * \param n Number of rows and columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void cporand(const char *uplo, const int *n, float *A, const int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; j < *n; j++) {
                for (i = 0; i < j; i++) {
                    A[2 * (i + j * *ldA)] = rand() / (float) RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = rand() / (float) RAND_MAX;
                }
                A[2 * (j + j * *ldA)] = rand() / (float) RAND_MAX + 2 * *n;
                A[2 * (j + j * *ldA) + 1] = 0;
            }
            break;
        case 'U':
            for (j = 0; j < *n; j++) {
                A[2 * (j + j * *ldA)] = rand() / (float) RAND_MAX + 2 * *n;
                A[2 * (j + j * *ldA) + 1] = 0;
                for (i = j + 1; i < *n; i++) {
                    A[2 * (i + j * *ldA)] = rand() / (float) RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = rand() / (float) RAND_MAX;
                }
            }
            break;
    }
}

/** Randomize a double precision complex HPD matrix.
 * Random values taken from \f$[0, 1) + [0, 1) i\f$ (off-diagonal), \f$[0, 1) +
 * 2 n\f$ (diagonal).
 *
 * \param uplo Lower (`"L"`) or upper (`"U"`) triangular.
 * \param n Number of rows and columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void zporand(const char *uplo, const int *n, double *A, const int *ldA) {
    int i, j;
    switch(uplo[0]) {
        case 'L':
            for (j = 0; j < *n; j++) {
                for (i = 0; i < j; i++) {
                    A[2 * (i + j * *ldA)] = rand() / (double) RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = rand() / (double) RAND_MAX;
                }
                A[2 * (j + j * *ldA)] = rand() / (double) RAND_MAX + 2 * *n;
                A[2 * (j + j * *ldA) + 1] = 0;
            }
            break;
        case 'U':
            for (j = 0; j < *n; j++) {
                A[2 * (j + j * *ldA)] = rand() / (double) RAND_MAX + 2 * *n;
                A[2 * (j + j * *ldA) + 1] = 0;
                for (i = j + 1; i < *n; i++) {
                    A[2 * (i + j * *ldA)] = rand() / (double) RAND_MAX;
                    A[2 * (i + j * *ldA) + 1] = rand() / (double) RAND_MAX;
                }
            }
            break;
    }
}
