#ifndef LAPACK_EXPERT_GEEV_H
#define LAPACK_EXPERT_GEEV_H

////////////////////////////////////////////////////////////////////////////////
// Expert Driver Routines for Standard and Generalized Nonsymmetric Eigenvalue Problems
////////////////////////////////////////////////////////////////////////////////

//geesx
int sgeesx_(char*, char*, void*, char*, int*, float*, int*, int*, float*, float*, float*, int*, float*, float*, float*, int*, int*, int*, int*, int*);
int dgeesx_(char*, char*, void*, char*, int*, double*, int*, int*, double*, double*, double*, int*, double*, double*, double*, int*, int*, int*, int*, int*);
int cgeesx_(char*, char*, void*, char*, int*, float*, int*, int*, float*, float*, int*, float*, float*, float*, int*, float*, int*, int*);
int zgeesx_(char*, char*, void*, char*, int*, double*, int*, int*, double*, double*, int*, double*, double*, double*, int*, double*, int*, int*);

//ggesx
int sggesx_(char*, char*, char*, void*, char*, int*, float*, int*, float*, int*, int*, float*, float*, float*, float*, int*, float*, int*, float*, float*, float*, int*, int*, int*, int*, int*);
int dggesx_(char*, char*, char*, void*, char*, int*, double*, int*, double*, int*, int*, double*, double*, double*, double*, int*, double*, int*, double*, double*, double*, int*, int*, int*, int*, int*);
int cggesx_(char*, char*, char*, void*, char*, int*, float*, int*, float*, int*, int*, float*, float*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*, int*, int*);
int zggesx_(char*, char*, char*, void*, char*, int*, double*, int*, double*, int*, int*, double*, double*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*, int*, int*);

//geevx
int sgeevx_(char*, char*, char*, char*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*, int*, float*, float*, float*, float*, float*, int*, int*, int*);
int dgeevx_(char*, char*, char*, char*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*, int*, double*, double*, double*, double*, double*, int*, int*, int*);
int cgeevx_(char*, char*, char*, char*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*, float*, float*, float*, float*, float*, int*, float*, int*);
int zgeevx_(char*, char*, char*, char*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*, double*, double*, double*, double*, double*, int*, double*, int*);

//ggevx
int sggevx_(char*, char*, char*, char*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, float*, int*, int*, int*, float*, float*, float*, float*, float*, float*, float*, int*, int*, int*, int*);
int dggevx_(char*, char*, char*, char*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, double*, int*, int*, int*, double*, double*, double*, double*, double*, double*, double*, int*, int*, int*, int*);
int cggevx_(char*, char*, char*, char*, int*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*, int*, float*, float*, float*, float*, float*, float*, float*, int*, float*, int*, int*, int*);
int zggevx_(char*, char*, char*, char*, int*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*, int*, double*, double*, double*, double*, double*, double*, double*, int*, double*, int*, int*, int*);

#endif /* LAPACK_EXPERT_GEEV_H */
