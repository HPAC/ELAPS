#ifndef FILEIO_H
#define FILEIO_H

void readfile(char *filename, int *m, int *n, char *A, int *ldA, int *info);
void ireadfile(char *filename, int *m, int *n, int *A, int *ldA, int *info);
void sreadfile(char *filename, int *m, int *n, float *A, int *ldA, int *info);
void dreadfile(char *filename, int *m, int *n, double *A, int *ldA, int *info);
void creadfile(char *filename, int *m, int *n, float *A, int *ldA, int *info);
void zreadfile(char *filename, int *m, int *n, double *A, int *ldA, int *info);

void writefile(char *filename, int *m, int *n, char *A, int *ldA, int *info);
void iwritefile(char *filename, int *m, int *n, int *A, int *ldA, int *info);
void swritefile(char *filename, int *m, int *n, float *A, int *ldA, int *info);
void dwritefile(char *filename, int *m, int *n, double *A, int *ldA, int *info);
void cwritefile(char *filename, int *m, int *n, float *A, int *ldA, int *info);
void zwritefile(char *filename, int *m, int *n, double *A, int *ldA, int *info);

#endif /* FILEIO_H */
