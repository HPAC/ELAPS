#include "gerand.h"

#include <stdlib.h>

/** Randomize an integer matrix.
 * Random values taken from \f$\{0, 1, \ldots, \min({\tt RAND\_MAX}, {\tt
 * INT\_MAX}) - 1\}\f$.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void igerand(const int *m, const int *n, int *A, const int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = rand() % (*m * *n);
}

/** Randomize a single precision matrix.
 * Random values taken from \f$[0, 1)\f$.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void sgerand(const int *m, const int *n, float *A, const int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = ((float) rand()) / RAND_MAX;
}

/** Randomize a double precision matrix.
 * Random values taken from \f$[0, 1)\f$.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void dgerand(const int *m, const int *n, double *A, const int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++)
            A[i + j * *ldA] = ((double) rand()) / RAND_MAX;
}

/** Randomize a single precision complex matrix.
 * Random values taken from \f$[0, 1) + [0, 1) i\f$.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void cgerand(const int *m, const int *n, float *A, const int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = ((float) rand()) / RAND_MAX;
            A[2 * (i + j * *ldA)] = ((float) rand()) / RAND_MAX;
        }
}

/** Randomize a double precision complex matrix.
 * Random values taken from \f$[0, 1) + [0, 1) i\f$.
 *
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void zgerand(const int *m, const int *n, double *A, const int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
            A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
        }
}
