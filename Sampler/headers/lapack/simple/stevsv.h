#ifndef LAPACK_SIMPLE_STEVSV_H
#define LAPACK_SIMPLE_STEVSV_H

////////////////////////////////////////////////////////////////////////////////
// Simple and Divide and Conquer Driver Routines for Standard Eigenvalue and Singular Value Problems
////////////////////////////////////////////////////////////////////////////////

//syev
int dsyev_(char*, char*, int*, double*, int*, double*, double*, int*, int*);
int ssyev_(char*, char*, int*, float*, int*, float*, float*, int*, int*);

//heev
int cheev_(char*, char*, int*, float*, int*, float*, float*, int*, float*, int*);
int zheev_(char*, char*, int*, double*, int*, double*, double*, int*, double*, int*);

//syevd
int ssyevd_(char*, char*, int*, float*, int*, float*, float*, int*, int*, int*, int*);
int dsyevd_(char*, char*, int*, double*, int*, double*, double*, int*, int*, int*, int*);

//heevd
int cheevd_(char*, char*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*, int*);
int zheevd_(char*, char*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*, int*);

//spev
int sspev_(char*, char*, int*, float*, float*, float*, int*, float*, int*);
int dspev_(char*, char*, int*, double*, double*, double*, int*, double*, int*);

//hpev
int chpev_(char*, char*, int*, float*, float*, float*, int*, float*, float*, int*);
int zhpev_(char*, char*, int*, double*, double*, double*, int*, double*, double*, int*);

//spevd
int sspevd_(char*, char*, int*, float*, float*, float*, int*, float*, int*, int*, int*, int*);
int dspevd_(char*, char*, int*, double*, double*, double*, int*, double*, int*, int*, int*, int*);

//hpevd
int chpevd_(char*, char*, int*, float*, float*, float*, int*, float*, int*, float*, int*, int*, int*, int*);
int zhpevd_(char*, char*, int*, double*, double*, double*, int*, double*, int*, double*, int*, int*, int*, int*);

//sbev
int ssbev_(char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int dsbev_(char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//hbev
int chbev_(char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*);
int zhbev_(char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*);

//sbevd
int dsbevd_(char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*, int*);
int ssbevd_(char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*, int*);

//hbevd
int chbevd_(char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*, int*, int*);
int zhbevd_(char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*, int*, int*);

//stev
int sstev_(char*, int*, float*, float*, float*, int*, float*, int*);
int dstev_(char*, int*, double*, double*, double*, int*, double*, int*);

//stevd
int sstevd_(char*, int*, float*, float*, float*, int*, float*, int*, int*, int*, int*);
int dstevd_(char*, int*, double*, double*, double*, int*, double*, int*, int*, int*, int*);

//gees
int sgees_(char*, char*, void*, int*, float*, int*, int*, float*, float*, float*, int*, float*, int*, int*, int*);
int dgees_(char*, char*, void*, int*, double*, int*, int*, double*, double*, double*, int*, double*, int*, int*, int*);
int cgees_(char*, char*, void*, int*, float*, int*, int*, float*, float*, int*, float*, int*, float*, int*, int*);
int zgees_(char*, char*, void*, int*, double*, int*, int*, double*, double*, int*, double*, int*, double*, int*, int*);

//geev
int sgeev_(char*, char*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, int*);
int dgeev_(char*, char*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, int*);
int cgeev_(char*, char*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int zgeev_(char*, char*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, double*, int*);

//gesvd
int sgesvd_(char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*);
int dgesvd_(char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*);
int cgesvd_(char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int zgesvd_(char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, double*, int*);

//gesdd
int sgesdd_(char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*, int*);
int dgesdd_(char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*, int*);
int cgesdd_(char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int zgesdd_(char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

#endif /* LAPACK_SIMPLE_STEVSV_H */
