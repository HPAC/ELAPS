#ifndef LAPACK_FACTORIZATION_CSD_H
#define LAPACK_FACTORIZATION_CSD_H

////////////////////////////////////////////////////////////////////////////////
// CSD
////////////////////////////////////////////////////////////////////////////////

//bdsqr (CSD)
int sbdsqr_(char*, int*, int*, int*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int dbdsqr_(char*, int*, int*, int*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);
int cbdsqr_(char*, int*, int*, int*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int zbdsqr_(char*, int*, int*, int*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);

#endif /* LAPACK_FACTORIZATION_CSD_H */
