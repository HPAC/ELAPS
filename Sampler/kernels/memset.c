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


/** Set all elements in a triangular integer matrix to a single value.
 *
 * \param uplo Lower (`'L'`) or upper (`'U'`) triangular.
 * \param diag norma ldiagonal (`"N"`) or untouched (`'U'`).
 * \param n Number of rows and columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void itrmemset(const char *uplo, const char *diag, const int *n, const int *alpha, int *A, const int *ldA) {
    int i, j;
    const int unit = diag[0] == 'U';
    if (uplo[0] == 'L') {
        for (j = 0; j < *n; j++)
            for (i = j + unit; i < *n; i++)
                A[i + j * *ldA] = *alpha;
    } else if (uplo[0] == 'U') {
        for (j = 0; j < *n; j++)
            for (i = 0; i <= j - unit; i++)
                A[i + j * *ldA] = *alpha;
    } else
        imemset(n, n, alpha, A, ldA);
}

/** Set all elements in a triangular single precision matrix to a single value.
 *
 * \param uplo Lower (`'L'`) or upper (`'U'`) triangular.
 * \param diag norma ldiagonal (`"N"`) or untouched (`'U'`).
 * \param n Number of rows and columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void strmemset(const char *uplo, const char *diag, const int *n, const float *alpha, float *A, const int *ldA) {
    int i, j;
    const int unit = diag[0] == 'U';
    if (uplo[0] == 'L') {
        for (j = 0; j < *n; j++)
            for (i = j + unit; i < *n; i++)
                A[i + j * *ldA] = *alpha;
    } else if (uplo[0] == 'U') {
        for (j = 0; j < *n; j++)
            for (i = 0; i <= j - unit; i++)
                A[i + j * *ldA] = *alpha;
    } else
        smemset(n, n, alpha, A, ldA);
}

/** Set all elements in a triangular double precision matrix to a single value.
 *
 * \param uplo Lower (`'L'`) or upper (`'U'`) triangular.
 * \param diag norma ldiagonal (`"N"`) or untouched (`'U'`).
 * \param n Number of rows and columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void dtrmemset(const char *uplo, const char *diag, const int *n, const double *alpha, double *A, const int *ldA) {
    int i, j;
    const int unit = diag[0] == 'U';
    if (uplo[0] == 'L') {
        for (j = 0; j < *n; j++)
            for (i = j + unit; i < *n; i++)
                A[i + j * *ldA] = *alpha;
    } else if (uplo[0] == 'U') {
        for (j = 0; j < *n; j++)
            for (i = 0; i <= j - unit; i++)
                A[i + j * *ldA] = *alpha;
    } else
        dmemset(n, n, alpha, A, ldA);
}

/** Set all elements in a triangular single precision complex matrix to a single value.
 *
 * \param uplo Lower (`'L'`) or upper (`'U'`) triangular.
 * \param diag norma ldiagonal (`"N"`) or untouched (`'U'`).
 * \param n Number of rows and columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void ctrmemset(const char *uplo, const char *diag, const int *n, const float *alpha, float *A, const int *ldA) {
    int i, j;
    const int unit = diag[0] == 'U';
    if (uplo[0] == 'L') {
        for (j = 0; j < *n; j++)
            for (i = j + unit; i < *n; i++)  {
                A[2 * (i + j * *ldA)] = alpha[0];
                A[2 * (i + j * *ldA)] = alpha[1];
            }
    } else if (uplo[0] == 'U') {
        for (j = 0; j < *n; j++)
            for (i = 0; i <= j - unit; i++)  {
                A[2 * (i + j * *ldA)] = alpha[0];
                A[2 * (i + j * *ldA)] = alpha[1];
            }
    } else
        cmemset(n, n, alpha, A, ldA);
}

/** Set all elements in a triangular double precision complex matrix to a single value.
 *
 * \param uplo Lower (`'L'`) or upper (`'U'`) triangular.
 * \param diag norma ldiagonal (`"N"`) or untouched (`'U'`).
 * \param n Number of rows and columns.
 * \param alpha Value.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 */
void ztrmemset(const char *uplo, const char *diag, const int *n, const double *alpha, double *A, const int *ldA) {
    int i, j;
    const int unit = diag[0] == 'U';
    if (uplo[0] == 'L') {
        for (j = 0; j < *n; j++)
            for (i = j + unit; i < *n; i++)  {
                A[2 * (i + j * *ldA)] = alpha[0];
                A[2 * (i + j * *ldA)] = alpha[1];
            }
    } else if (uplo[0] == 'U') {
        for (j = 0; j < *n; j++)
            for (i = 0; i <= j - unit; i++)  {
                A[2 * (i + j * *ldA)] = alpha[0];
                A[2 * (i + j * *ldA)] = alpha[1];
            }
    } else
        zmemset(n, n, alpha, A, ldA);
}
