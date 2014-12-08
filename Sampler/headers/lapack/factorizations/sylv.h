#ifndef LAPACK_FACTORIZATION_SYLV_H
#define LAPACK_FACTORIZATION_SYLV_H

////////////////////////////////////////////////////////////////////////////////
// sylv
////////////////////////////////////////////////////////////////////////////////

//tgsyl (generalized sylv)
int stgsyl_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*, int*);
int dtgsyl_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*, int*);
int ctgsyl_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*, int*);
int ztgsyl_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*, int*);

//trsyl (sylv)
int strsyl_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*);
int dtrsyl_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*);
int ctrsyl_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*);
int ztrsyl_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*);

#endif /* LAPACK_FACTORIZATION_SYLV_H */
