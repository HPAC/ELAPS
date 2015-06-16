#include "fileio.h"
#include <stdio.h>

/** Read a `char` matrix from a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void readfile(char *filename, int *m, int *n, char *A, int *ldA, int *info) {
    *info = 0;
    FILE *fin = fopen(filename, "rb");
    if (!fin) {
        *info = -1;
        return;
    }
    int j;
    for (j = 0; j < *n; j++)
        if (fread(A + *m + *n * *ldA, sizeof(char), *m, fin) != *m) {
            *info = -1;
            return;
        }
}

/** Read an integer matrix from a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void ireadfile(char *filename, int *m, int *n, int *A, int *ldA, int *info) {
    int cm = *m * sizeof(int) / sizeof(char);
    int cldA = *ldA * sizeof(int) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Read a single precision matrix from a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void sreadfile(char *filename, int *m, int *n, float *A, int *ldA, int *info) {
    int cm = *m * sizeof(float) / sizeof(char);
    int cldA = *ldA * sizeof(float) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Read a double precision matrix from a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void dreadfile(char *filename, int *m, int *n, double *A, int *ldA, int *info) {
    int cm = *m * sizeof(double) / sizeof(char);
    int cldA = *ldA * sizeof(double) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Read a single precision complex matrix from a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void creadfile(char *filename, int *m, int *n, float *A, int *ldA, int *info) {
    int cm = 2 * *m * sizeof(float) / sizeof(char);
    int cldA = 2 * *ldA * sizeof(float) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Read a double precision complex matrix from a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void zreadfile(char *filename, int *m, int *n, double *A, int *ldA, int *info) {
    int cm = 2 * *m * sizeof(double) / sizeof(char);
    int cldA = 2 * *ldA * sizeof(double) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Write a `char` matrix to a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void writefile(char *filename, int *m, int *n, char *A, int *ldA, int *info) {
    *info = 0;
    FILE *fin = fopen(filename, "wb");
    if (!fin) {
        *info = -1;
        return;
    }
    int j;
    for (j = 0; j < *n; j++)
        if (fwrite(A + *m + *n * *ldA, sizeof(char), *m, fin) != *m) {
            *info = -1;
            return;
        }
}

/** Write an integer matrix to a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void iwritefile(char *filename, int *m, int *n, int *A, int *ldA, int *info) {
    int cm = *m * sizeof(int) / sizeof(char);
    int cldA = *ldA * sizeof(int) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Write a single precision matrix to a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void swritefile(char *filename, int *m, int *n, float *A, int *ldA, int *info) {
    int cm = *m * sizeof(float) / sizeof(char);
    int cldA = *ldA * sizeof(float) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Write a double precision matrix to a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void dwritefile(char *filename, int *m, int *n, double *A, int *ldA, int *info) {
    int cm = *m * sizeof(double) / sizeof(char);
    int cldA = *ldA * sizeof(double) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Write a single precision complex matrix to a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void cwritefile(char *filename, int *m, int *n, float *A, int *ldA, int *info) {
    int cm = 2 * *m * sizeof(float) / sizeof(char);
    int cldA = 2 * *ldA * sizeof(float) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}

/** Write a double precision complex matrix to a binary file.
 *
 * \param filename Filename.
 * \param m Number of rows.
 * \param n Number of columns.
 * \param A Matrix pointer.
 * \param ldA Leading dimension.
 * \param info Error status, 0 on success.
 */
void zwritefile(char *filename, int *m, int *n, double *A, int *ldA, int *info) {
    int cm = 2 * *m * sizeof(double) / sizeof(char);
    int cldA = 2 * *ldA * sizeof(double) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}
