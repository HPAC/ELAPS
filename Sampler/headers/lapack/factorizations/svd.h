#ifndef LAPACK_FACTORIZATION_SVD_H
#define LAPACK_FACTORIZATION_SVD_H

////////////////////////////////////////////////////////////////////////////////
// SVD
////////////////////////////////////////////////////////////////////////////////


//bdscd (SVD)
int sbdsdc_(char*, char*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dbdsdc_(char*, char*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//gejsv (SVD)
int sgejsv_(char*, char*, char*, char*, char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*, int*);
int dgejsv_(char*, char*, char*, char*, char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*, int*);

//gesvj (SVD)
int sgesvj_(char*, char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dgesvj_(char*, char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//ggsvp (gen. SVD preprocessing)
int sggsvp_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, int*, float*, int*, int*, float*, float*, int*);
int dggsvp_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, int*, double*, int*, int*, double*, double*, int*);
int cggsvp_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, int*, float*, int*, int*, float*, float*, float*, int*);
int zggsvp_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, int*, double*, int*, int*, double*, double*, double*, int*);

//gsvj0 (SVD preprocessing)
int sgsvj0_(char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*);
int dgsvj0_(char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*);

//gsvj1 (SVD preprocessing)
int sgsvj1_(char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*);
int dgsvj1_(char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*);

//tgsja (GSVD)
int stgsja_(char*, char*, char*, int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dtgsja_(char*, char*, char*, int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);
int ctgsja_(char*, char*, char*, int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int ztgsja_(char*, char*, char*, int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

#endif /* LAPACK_FACTORIZATION_SVD_H */
