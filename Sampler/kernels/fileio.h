#ifndef FILEIO_H
#define FILEIO_H

void readfile(const char *, const int *, const int *, char *, const int *, int *);
void ireadfile(const char *, const int *, const int *, int *, const int *, int *);
void sreadfile(const char *, const int *, const int *, float *, const int *, int *);
void dreadfile(const char *, const int *, const int *, double *, const int *, int *);
void creadfile(const char *, const int *, const int *, float *, const int *, int *);
void zreadfile(const char *, const int *, const int *, double *, const int *, int *);

void writefile(const char *, const int *, const int *, const char *, const int *, int *);
void iwritefile(const char *, const int *, const int *, const int *, const int *, int *);
void swritefile(const char *, const int *, const int *, const float *, const int *, int *);
void dwritefile(const char *, const int *, const int *, const double *, const int *, int *);
void cwritefile(const char *, const int *, const int *, const float *, const int *, int *);
void zwritefile(const char *, const int *, const int *, const double *, const int *, int *);

#endif /* FILEIO_H */
