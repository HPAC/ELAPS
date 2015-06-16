#include "memset.h"

/** Set all elements in an integer matrix to a single value.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void imemset(int *m, int *n, int *alpha, int *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = *alpha;
}

/** Set all elements in a single precision matrix to a single value.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void smemset(int *m, int *n, float *alpha, float *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = *alpha;
}

/** Set all elements in a double precision matrix to a single value.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void dmemset(int *m, int *n, double *alpha, double *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = *alpha;
}

/** Set all elements in a single precision complex matrix to a single value.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void cmemset(int *m, int *n, float *alpha, float *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = alpha[0];
            A[2 * (i + j * *ldA)] = alpha[1];
        }
}

/** Set all elements in a double precision complex matrix to a single value.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void zmemset(int *m, int *n, double *alpha, double *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = alpha[0];
            A[2 * (i + j * *ldA)] = alpha[1];
        }
}
