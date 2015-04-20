#include "fileio.h"
#include <stdio.h>

void readfile(char *filename, int *m, int *n, char *A, int *ldA, int *info) {
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

void ireadfile(char *filename, int *m, int *n, int *A, int *ldA, int *info) {
    int cm = *m * sizeof(int) / sizeof(char);
    int cldA = *ldA * sizeof(int) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

void sreadfile(char *filename, int *m, int *n, float *A, int *ldA, int *info) {
    int cm = *m * sizeof(float) / sizeof(char);
    int cldA = *ldA * sizeof(float) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

void dreadfile(char *filename, int *m, int *n, double *A, int *ldA, int *info) {
    int cm = *m * sizeof(double) / sizeof(char);
    int cldA = *ldA * sizeof(double) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

void creadfile(char *filename, int *m, int *n, float *A, int *ldA, int *info) {
    int cm = 2 * *m * sizeof(float) / sizeof(char);
    int cldA = 2 * *ldA * sizeof(float) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

void zreadfile(char *filename, int *m, int *n, double *A, int *ldA, int *info) {
    int cm = 2 * *m * sizeof(double) / sizeof(char);
    int cldA = 2 * *ldA * sizeof(double) / sizeof(char);
    readfile(filename, &cm, n, (char *) A, &cldA, info);
}

void writefile(char *filename, int *m, int *n, char *A, int *ldA, int *info) {
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

void iwritefile(char *filename, int *m, int *n, int *A, int *ldA, int *info) {
    int cm = *m * sizeof(int) / sizeof(char);
    int cldA = *ldA * sizeof(int) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}

void swritefile(char *filename, int *m, int *n, float *A, int *ldA, int *info) {
    int cm = *m * sizeof(float) / sizeof(char);
    int cldA = *ldA * sizeof(float) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}

void dwritefile(char *filename, int *m, int *n, double *A, int *ldA, int *info) {
    int cm = *m * sizeof(double) / sizeof(char);
    int cldA = *ldA * sizeof(double) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}

void cwritefile(char *filename, int *m, int *n, float *A, int *ldA, int *info) {
    int cm = 2 * *m * sizeof(float) / sizeof(char);
    int cldA = 2 * *ldA * sizeof(float) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}

void zwritefile(char *filename, int *m, int *n, double *A, int *ldA, int *info) {
    int cm = 2 * *m * sizeof(double) / sizeof(char);
    int cldA = 2 * *ldA * sizeof(double) / sizeof(char);
    writefile(filename, &cm, n, (char *) A, &cldA, info);
}
