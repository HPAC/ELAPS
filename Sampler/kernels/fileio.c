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
void readfile(const char *filename, const int *m, const int *n, char *A, const int *ldA, int *info) {
    *info = 0;
    FILE *fin = fopen(filename, "rb");
    if (!fin) {
        *info = -1;
        return;
    }
    int j;
    for (j = 0; j < *n; j++)
        if (fread(A + *m + *n * *ldA, sizeof(char), (size_t) *m, fin) != (size_t) *m) {
            *info = j;
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
void ireadfile(const char *filename, const int *m, const int *n, int *A, const int *ldA, int *info) {
    int cm = *m * (int) (sizeof(int) / sizeof(char));
    int cldA = *ldA * (int) (sizeof(int) / sizeof(char));
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
void sreadfile(const char *filename, const int *m, const int *n, float *A, const int *ldA, int *info) {
    int cm = *m * (int) (sizeof(float) / sizeof(char));
    int cldA = *ldA * (int) (sizeof(float) / sizeof(char));
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
void dreadfile(const char *filename, const int *m, const int *n, double *A, const int *ldA, int *info) {
    int cm = *m * (int) (sizeof(double) / sizeof(char));
    int cldA = *ldA * (int) (sizeof(double) / sizeof(char));
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
void creadfile(const char *filename, const int *m, const int *n, float *A, const int *ldA, int *info) {
    int cm = *m * (int) (2 * sizeof(float) / sizeof(char));
    int cldA = *ldA * (int) (2 * sizeof(float) / sizeof(char));
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
void zreadfile(const char *filename, const int *m, const int *n, double *A, const int *ldA, int *info) {
    int cm = *m * (int) (2 * sizeof(double) / sizeof(char));
    int cldA = *ldA * (int) (2 * sizeof(double) / sizeof(char));
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
void writefile(const char *filename, const int *m, const int *n, const char *A, const int *ldA, int *info) {
    *info = 0;
    FILE *fin = fopen(filename, "wb");
    if (!fin) {
        *info = -1;
        return;
    }
    int j;
    for (j = 0; j < *n; j++)
        if (fwrite(A + *m + *n * *ldA, sizeof(char), (size_t) *m, fin) != (size_t) *m) {
            *info = j;
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
void iwritefile(const char *filename, const int *m, const int *n, const int *A, const int *ldA, int *info) {
    int cm = *m * (int) (sizeof(int) / sizeof(char));
    int cldA = *ldA * (int) (sizeof(int) / sizeof(char));
    writefile(filename, &cm, n, (const char *) A, &cldA, info);
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
void swritefile(const char *filename, const int *m, const int *n, const float *A, const int *ldA, int *info) {
    int cm = *m * (int) (sizeof(float) / sizeof(char));
    int cldA = *ldA * (int) (sizeof(float) / sizeof(char));
    writefile(filename, &cm, n, (const char *) A, &cldA, info);
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
void dwritefile(const char *filename, const int *m, const int *n, const double *A, const int *ldA, int *info) {
    int cm = *m * (int) (sizeof(double) / sizeof(char));
    int cldA = *ldA * (int) (sizeof(double) / sizeof(char));
    writefile(filename, &cm, n, (const char *) A, &cldA, info);
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
void cwritefile(const char *filename, const int *m, const int *n, const float *A, const int *ldA, int *info) {
    int cm = *m * (int) (2 * sizeof(float) / sizeof(char));
    int cldA = *ldA * (int) (2 * sizeof(float) / sizeof(char));
    writefile(filename, &cm, n, (const char *) A, &cldA, info);
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
void zwritefile(const char *filename, const int *m, const int *n, const double *A, const int *ldA, int *info) {
    int cm = *m * (int) (2 * sizeof(double) / sizeof(char));
    int cldA = *ldA * (int) (2 * sizeof(double) / sizeof(char));
    writefile(filename, &cm, n, (const char *) A, &cldA, info);
}
