#ifndef LAPACK_FACTORIZATION_H
#define LAPACK_FACTORIZATION_H

////////////////////////////////////////////////////////////////////////////////
// Computational routines (found by hand)
////////////////////////////////////////////////////////////////////////////////

//bbcsd (CSD) MISSING

//bdscd (SVD)
int sbdsdc_(char*, char*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dbdsdc_(char*, char*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//bdsqr (SCD)
int sbdsqr_(char*, int*, int*, int*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int dbdsqr_(char*, int*, int*, int*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);
int cbdsqr_(char*, int*, int*, int*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int zbdsqr_(char*, int*, int*, int*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);

//gbtrf (LU)
int sgbtrf_(int*, int*, int*, int*, float*, int*, int*, int*);
int dgbtrf_(int*, int*, int*, int*, double*, int*, int*, int*);
int cgbtrf_(int*, int*, int*, int*, float*, int*, int*, int*);
int zgbtrf_(int*, int*, int*, int*, double*, int*, int*, int*);

//gejsv (SVD)
int sgejsv_(char*, char*, char*, char*, char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*, int*);
int dgejsv_(char*, char*, char*, char*, char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*, int*);

//gelqf (LQ)
int sgelqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgelqf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgelqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgelqf_(int*, int*, double*, int*, double*, double*, int*, int*);

//geqlf (QL)
int sgeqlf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgeqlf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqlf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgeqlf_(int*, int*, double*, int*, double*, double*, int*, int*);

//geqp3 (QR)
int sgeqp3_(int*, int*, float*, int*, int*, float*, float*, int*, int*);
int dgeqp3_(int*, int*, double*, int*, int*, double*, double*, int*, int*);
int cgeqp3_(int*, int*, float*, int*, int*, float*, float*, int*, float*, int*);
int zgeqp3_(int*, int*, double*, int*, int*, double*, double*, int*, double*, int*);

//geqpf (QR)
int cgeqpf_(int*, int*, float*, int*, int*, float*, float*, float*, int*);
int dgeqpf_(int*, int*, double*, int*, int*, double*, double*, int*);
int sgeqpf_(int*, int*, float*, int*, int*, float*, float*, int*);
int zgeqpf_(int*, int*, double*, int*, int*, double*, double*, double*, int*);

//geqrf (QR)
int sgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgeqrf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgeqrf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);

//geqrt  (QR by WY repr.) MISSING
//geqrt2 (QR by WY repr.) MISSING
//geqrt3 (QR by WY repr.) MISSING

//gerqf (RQ)
int sgerqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgerqf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgerqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgerqf_(int*, int*, double*, int*, double*, double*, int*, int*);

//gesvj (SVD)
int sgesvj_(char*, char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dgesvj_(char*, char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//getrf (LU)
int sgetrf_(int*, int*, float*, int*, int*, int*);
int dgetrf_(int*, int*, double*, int*, int*, int*);
int cgetrf_(int*, int*, float*, int*, int*, int*);
int zgetrf_(int*, int*, double*, int*, int*, int*);

//ggqrf (gen. QR)
int sggqrf_(int*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int dggqrf_(int*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*);
int cggqrf_(int*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int zggqrf_(int*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*);

//ggrqf (gen. RQ)
int sggrqf_(int*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int dggrqf_(int*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*);
int cggrqf_(int*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int zggrqf_(int*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*);

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

//gttrf (tridiag LU)
int sgttrf_(int*, float*, float*, float*, float*, int*, int*);
int dgttrf_(int*, double*, double*, double*, double*, int*, int*);
int cgttrf_(int*, float*, float*, float*, float*, int*, int*);
int zgttrf_(int*, double*, double*, double*, double*, int*, int*);

//hetrf (LDL)
int chetrf_(char*, int*, float*, int*, int*, float*, int*, int*);
int zhetrf_(char*, int*, double*, int*, int*, double*, int*, int*);

//hptrf (packed LDL)
int chptrf_(char*, int*, float*, int*, int*);
int zhptrf_(char*, int*, double*, int*, int*);

//pbstf (banded split chol)
int cpbstf_(char*, int*, int*, float*, int*, int*);
int dpbstf_(char*, int*, int*, double*, int*, int*);
int spbstf_(char*, int*, int*, float*, int*, int*);
int zpbstf_(char*, int*, int*, double*, int*, int*);

//pbtrf (banded chol)
int spbtrf_(char*, int*, int*, float*, int*, int*);
int dpbtrf_(char*, int*, int*, double*, int*, int*);
int cpbtrf_(char*, int*, int*, float*, int*, int*);
int zpbtrf_(char*, int*, int*, double*, int*, int*);

//pftrf (chol)
int spftrf_(char*, char*, int*, float*, int*);
int dpftrf_(char*, char*, int*, double*, int*);
int cpftrf_(char*, char*, int*, float*, int*);
int zpftrf_(char*, char*, int*, double*, int*);

//potrf (chol)
int spotrf_(char*, int*, float*, int*, int*);
int dpotrf_(char*, int*, double*, int*, int*);
int cpotrf_(char*, int*, float*, int*, int*);
int zpotrf_(char*, int*, double*, int*, int*);

//pptrf (packed chol)
int spptrf_(char*, int*, float*, int*);
int dpptrf_(char*, int*, double*, int*);
int cpptrf_(char*, int*, float*, int*);
int zpptrf_(char*, int*, double*, int*);

//pstf2 (pivoting chol) UNBLOCKED?
int spstf2_(char*, int*, float*, int*, int*, int*, float*, float*, int*);
int dpstf2_(char*, int*, double*, int*, int*, int*, double*, double*, int*);
int cpstf2_(char*, int*, float*, int*, int*, int*, float*, float*, int*);
int zpstf2_(char*, int*, double*, int*, int*, int*, double*, double*, int*);

//pstrf (pivoting chol)
int spstrf_(char*, int*, float*, int*, int*, int*, float*, float*, int*);
int dpstrf_(char*, int*, double*, int*, int*, int*, double*, double*, int*);
int cpstrf_(char*, int*, float*, int*, int*, int*, float*, float*, int*);
int zpstrf_(char*, int*, double*, int*, int*, int*, double*, double*, int*);

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

//tgsja (GSVD)
int stgsja_(char*, char*, char*, int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dtgsja_(char*, char*, char*, int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);
int ctgsja_(char*, char*, char*, int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int ztgsja_(char*, char*, char*, int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

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

#endif /* LAPACK_FACTORIZATION_H */
