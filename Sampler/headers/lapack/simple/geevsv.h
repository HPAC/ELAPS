#ifndef LAPACK_SIMPLE_GEEVSV_H
#define LAPACK_SIMPLE_GEEVSV_H

////////////////////////////////////////////////////////////////////////////////
// Simple and Divide and Conquer Driver Routines for Generalized Eigenvalue and Singular Value Problems
////////////////////////////////////////////////////////////////////////////////

//sygv
int ssygv_(int*, char*, char*, int*, float*, int*, float*, int*, float*, float*, int*, int*);
int dsygv_(int*, char*, char*, int*, double*, int*, double*, int*, double*, double*, int*, int*);

//hegv
int chegv_(int*, char*, char*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*);
int zhegv_(int*, char*, char*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*);

//sygvd
int ssygvd_(int*, char*, char*, int*, float*, int*, float*, int*, float*, float*, int*, int*, int*, int*);
int dsygvd_(int*, char*, char*, int*, double*, int*, double*, int*, double*, double*, int*, int*, int*, int*);

//hegvd
int chegvd_(int*, char*, char*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*, int*);
int zhegvd_(int*, char*, char*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*, int*);

//spgv
int sspgv_(int*, char*, char*, int*, float*, float*, float*, float*, int*, float*, int*);
int dspgv_(int*, char*, char*, int*, double*, double*, double*, double*, int*, double*, int*);

//hpgv
int chpgv_(int*, char*, char*, int*, float*, float*, float*, float*, int*, float*, float*, int*);
int zhpgv_(int*, char*, char*, int*, double*, double*, double*, double*, int*, double*, double*, int*);

//spgvd
int dspgvd_(int*, char*, char*, int*, double*, double*, double*, double*, int*, double*, int*, int*, int*, int*);
int sspgvd_(int*, char*, char*, int*, float*, float*, float*, float*, int*, float*, int*, int*, int*, int*);

//hpgvd
int chpgvd_(int*, char*, char*, int*, float*, float*, float*, float*, int*, float*, int*, float*, int*, int*, int*, int*);
int zhpgvd_(int*, char*, char*, int*, double*, double*, double*, double*, int*, double*, int*, double*, int*, int*, int*, int*);

//sbgv
int ssbgv_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*);
int dsbgv_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*);

//hbgv
int chbgv_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*);
int zhbgv_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*);

//sbgvd
int dsbgvd_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*, int*);
int ssbgvd_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*, int*);

//gges
int sgges_(char*, char*, char*, void*, int*, float*, int*, float*, int*, int*, float*, float*, float*, float*, int*, float*, int*, float*, int*, int*, int*);
int dgges_(char*, char*, char*, void*, int*, double*, int*, double*, int*, int*, double*, double*, double*, double*, int*, double*, int*, double*, int*, int*, int*);
int cgges_(char*, char*, char*, void*, int*, float*, int*, float*, int*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int zgges_(char*, char*, char*, void*, int*, double*, int*, double*, int*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//ggev
int sggev_(char*, char*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, float*, int*, float*, int*, int*);
int dggev_(char*, char*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, double*, int*, double*, int*, int*);
int cggev_(char*, char*, int*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int zggev_(char*, char*, int*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);

//ggsvd
int sggsvd_(char*, char*, char*, int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dggsvd_(char*, char*, char*, int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);
int cggsvd_(char*, char*, char*, int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, int*, int*);
int zggsvd_(char*, char*, char*, int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, int*, int*);

#endif /* LAPACK_SIMPLE_GEEVSV_H */
