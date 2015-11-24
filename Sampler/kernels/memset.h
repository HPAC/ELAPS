#ifndef MEMSET_H
#define MEMSET_H

void imemset(const int *, const int *, const int *, int *, const int *);
void smemset(const int *, const int *, const float *, float *, const int *);
void dmemset(const int *, const int *, const double *, double *, const int *);
void cmemset(const int *, const int *, const float *, float *, const int *);
void zmemset(const int *, const int *, const double *, double *, const int *);

void itrmemset(const char *, const char *, const int *, const int *, int *, const int *);
void strmemset(const char *, const char *, const int *, const float *, float *, const int *);
void dtrmemset(const char *, const char *, const int *, const double *, double *, const int *);
void ctrmemset(const char *, const char *, const int *, const float *, float *, const int *);
void ztrmemset(const char *, const char *, const int *, const double *, double *, const int *);

#endif /* MEMSET_H */
