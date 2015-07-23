#include "memset.h"

/** Set all elements in an integer matrix to a single value.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void imemset(const int *m, const int *n, const int *alpha, int *A, const int *ldA) {
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
void smemset(const int *m, const int *n, const float *alpha, float *A, const int *ldA) {
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
void dmemset(const int *m, const int *n, const double *alpha, double *A, const int *ldA) {
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
void cmemset(const int *m, const int *n, const float *alpha, float *A, const int *ldA) {
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
void zmemset(const int *m, const int *n, const double *alpha, double *A, const int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = alpha[0];
            A[2 * (i + j * *ldA)] = alpha[1];
        }
}
