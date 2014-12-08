#ifndef LAPACK_FACTORIZATION_CHOL_H
#define LAPACK_FACTORIZATION_CHOL_H

////////////////////////////////////////////////////////////////////////////////
// Cholesky
////////////////////////////////////////////////////////////////////////////////

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

#endif /* LAPACK_FACTORIZATION_CHOL_H */
