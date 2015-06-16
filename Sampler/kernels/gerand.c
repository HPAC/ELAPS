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
void igerand(int *m, int *n, int *A, int *ldA) {
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
void sgerand(int *m, int *n, float *A, int *ldA) {
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
void dgerand(int *m, int *n, double *A, int *ldA) {
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
void cgerand(int *m, int *n, float *A, int *ldA) {
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
void zgerand(int *m, int *n, double *A, int *ldA) {
    int i, j;
    for (j = 0; j < *n; j++)
        for (i = 0; i < *m; i++) {
            A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
            A[2 * (i + j * *ldA)] = ((double) rand()) / RAND_MAX;
        }
}
