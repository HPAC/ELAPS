#ifndef LAPACK_LINSYS_H
#define LAPACK_LINSYS_H

////////////////////////////////////////////////////////////////////////////////
// linear system solvers
////////////////////////////////////////////////////////////////////////////////

//getrs (lin sys by LU)
int sgetrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int dgetrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);
int cgetrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int zgetrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);

//gtrfs (tridiag lin sys)
int sgtrfs_(char*, int*, int*, float*, float*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dgtrfs_(char*, int*, int*, double*, double*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int cgtrfs_(char*, int*, int*, float*, float*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zgtrfs_(char*, int*, int*, double*, double*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//gttrs (tridiag lin sys)
int sgttrs_(char*, int*, int*, float*, float*, float*, float*, int*, float*, int*, int*);
int dgttrs_(char*, int*, int*, double*, double*, double*, double*, int*, double*, int*, int*);
int cgttrs_(char*, int*, int*, float*, float*, float*, float*, int*, float*, int*, int*);
int zgttrs_(char*, int*, int*, double*, double*, double*, double*, int*, double*, int*, int*);

//gtts2 (tridiag lin sys) UNBLOCKED?
int sgtts2_(int*, int*, int*, float*, float*, float*, float*, int*, float*, int*);
int dgtts2_(int*, int*, int*, double*, double*, double*, double*, int*, double*, int*);
int cgtts2_(int*, int*, int*, float*, float*, float*, float*, int*, float*, int*);
int zgtts2_(int*, int*, int*, double*, double*, double*, double*, int*, double*, int*);

//hetrs (lin sys by LDL)
int chetrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int zhetrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);

//hptrs (packed lin sys by LDL)
int chptrs_(char*, int*, int*, float*, int*, float*, int*, int*);
int zhptrs_(char*, int*, int*, double*, int*, double*, int*, int*);

//pbtrs (banded lin sys by chol)
int spbtrs_(char*, int*, int*, int*, float*, int*, float*, int*, int*);
int dpbtrs_(char*, int*, int*, int*, double*, int*, double*, int*, int*);
int cpbtrs_(char*, int*, int*, int*, float*, int*, float*, int*, int*);
int zpbtrs_(char*, int*, int*, int*, double*, int*, double*, int*, int*);

//pftrs (lin sys by chol)
int spftrs_(char*, char*, int*, int*, float*, float*, int*, int*);
int dpftrs_(char*, char*, int*, int*, double*, double*, int*, int*);
int cpftrs_(char*, char*, int*, int*, float*, float*, int*, int*);
int zpftrs_(char*, char*, int*, int*, double*, double*, int*, int*);

//potrs (lin sys by chol)
int spotrs_(char*, int*, int*, float*, int*, float*, int*, int*);
int dpotrs_(char*, int*, int*, double*, int*, double*, int*, int*);
int cpotrs_(char*, int*, int*, float*, int*, float*, int*, int*);
int zpotrs_(char*, int*, int*, double*, int*, double*, int*, int*);

//pptrs (packed lin sys by chol)
int spptrs_(char*, int*, int*, float*, float*, int*, int*);
int dpptrs_(char*, int*, int*, double*, double*, int*, int*);
int cpptrs_(char*, int*, int*, float*, float*, int*, int*);
int zpptrs_(char*, int*, int*, double*, double*, int*, int*);

//pttrs (tridiag lin sys by LDL)
int spttrs_(int*, int*, float*, float*, float*, int*, int*);
int dpttrs_(int*, int*, double*, double*, double*, int*, int*);
int cpttrs_(char*, int*, int*, float*, float*, float*, int*, int*);
int zpttrs_(char*, int*, int*, double*, double*, double*, int*, int*);

//ptts2 (tridiag lin sys by LDL) UNBLOCKED?
int sptts2_(int*, int*, float*, float*, float*, int*);
int dptts2_(int*, int*, double*, double*, double*, int*);
int cptts2_(int*, int*, int*, float*, float*, float*, int*);
int zptts2_(int*, int*, int*, double*, double*, double*, int*);

//ptts2 (tridiag lin sys by LDL) UNBLOCKED?
int sptts2_(int*, int*, float*, float*, float*, int*);
int dptts2_(int*, int*, double*, double*, double*, int*);
int cptts2_(int*, int*, int*, float*, float*, float*, int*);
int zptts2_(int*, int*, int*, double*, double*, double*, int*);

//sytrs (lin sys by LDL)
int ssytrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int dsytrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);
int csytrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int zsytrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);

//tbtrs (banded lin sys)
int stbtrs_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, int*);
int dtbtrs_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, int*);
int ctbtrs_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, int*);
int ztbtrs_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, int*);

//tptrs (packed lin sys)
int stptrs_(char*, char*, char*, int*, int*, float*, float*, int*, int*);
int dtptrs_(char*, char*, char*, int*, int*, double*, double*, int*, int*);
int ctptrs_(char*, char*, char*, int*, int*, float*, float*, int*, int*);
int ztptrs_(char*, char*, char*, int*, int*, double*, double*, int*, int*);

//trtrs (lin sys)
int strtrs_(char*, char*, char*, int*, int*, float*, int*, float*, int*, int*);
int dtrtrs_(char*, char*, char*, int*, int*, double*, int*, double*, int*, int*);
int ctrtrs_(char*, char*, char*, int*, int*, float*, int*, float*, int*, int*);
int ztrtrs_(char*, char*, char*, int*, int*, double*, int*, double*, int*, int*);

#endif /* LAPACK_LINSYS_H */
