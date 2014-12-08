#ifndef LAPACK_FACTORIZATION_LDL_H
#define LAPACK_FACTORIZATION_LDL_H

////////////////////////////////////////////////////////////////////////////////
// LDL
////////////////////////////////////////////////////////////////////////////////

//hetrf (LDL)
int chetrf_(char*, int*, float*, int*, int*, float*, int*, int*);
int zhetrf_(char*, int*, double*, int*, int*, double*, int*, int*);

//hptrf (packed LDL)
int chptrf_(char*, int*, float*, int*, int*);
int zhptrf_(char*, int*, double*, int*, int*);

//pttrf (tridiag LDL)
int spttrf_(int*, float*, float*, int*);
int dpttrf_(int*, double*, double*, int*);
int cpttrf_(int*, float*, float*, int*);
int zpttrf_(int*, double*, double*, int*);

//sptrf (packed LDL)
int ssptrf_(char*, int*, float*, int*, int*);
int dsptrf_(char*, int*, double*, int*, int*);
int csptrf_(char*, int*, float*, int*, int*);
int zsptrf_(char*, int*, double*, int*, int*);

//sytrf (LDL)
int ssytrf_(char*, int*, float*, int*, int*, float*, int*, int*);
int dsytrf_(char*, int*, double*, int*, int*, double*, int*, int*);
int csytrf_(char*, int*, float*, int*, int*, float*, int*, int*);
int zsytrf_(char*, int*, double*, int*, int*, double*, int*, int*);

#endif /* LAPACK_FACTORIZATION_LDL_H */
