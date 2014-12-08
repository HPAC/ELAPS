#ifndef LAPACK_INV_H
#define LAPACK_INV_H

////////////////////////////////////////////////////////////////////////////////
// inversion
////////////////////////////////////////////////////////////////////////////////

//getri (inv by LU)
int sgetri_(int*, float*, int*, int*, float*, int*, int*);
int dgetri_(int*, double*, int*, int*, double*, int*, int*);
int cgetri_(int*, float*, int*, int*, float*, int*, int*);
int zgetri_(int*, double*, int*, int*, double*, int*, int*);

//hetri (inv by LDL)
int chetri_(char*, int*, float*, int*, int*, float*, int*);
int zhetri_(char*, int*, double*, int*, int*, double*, int*);

//hptri (packed inv by LDL)
int chptri_(char*, int*, float*, int*, float*, int*);
int zhptri_(char*, int*, double*, int*, double*, int*);

//pftri (inv by chol)
int spftri_(char*, char*, int*, float*, int*);
int dpftri_(char*, char*, int*, double*, int*);
int cpftri_(char*, char*, int*, float*, int*);
int zpftri_(char*, char*, int*, double*, int*);

//potri (inv by chol)
int spotri_(char*, int*, float*, int*, int*);
int dpotri_(char*, int*, double*, int*, int*);
int cpotri_(char*, int*, float*, int*, int*);
int zpotri_(char*, int*, double*, int*, int*);

//pptri (packed inv by chol)
int spptri_(char*, int*, float*, int*);
int dpptri_(char*, int*, double*, int*);
int cpptri_(char*, int*, float*, int*);
int zpptri_(char*, int*, double*, int*);

//sptri (packed inv b LDL)
int ssptri_(char*, int*, float*, int*, float*, int*);
int dsptri_(char*, int*, double*, int*, double*, int*);
int csptri_(char*, int*, float*, int*, float*, int*);
int zsptri_(char*, int*, double*, int*, double*, int*);

//sytri (inv by LDL)
int ssytri_(char*, int*, float*, int*, int*, float*, int*);
int dsytri_(char*, int*, double*, int*, int*, double*, int*);
int csytri_(char*, int*, float*, int*, int*, float*, int*);
int zsytri_(char*, int*, double*, int*, int*, double*, int*);

//tftri (inv in RFP)
int stftri_(char*, char*, char*, int*, float*, int*);
int dtftri_(char*, char*, char*, int*, double*, int*);
int ctftri_(char*, char*, char*, int*, float*, int*);
int ztftri_(char*, char*, char*, int*, double*, int*);

//tptri (packed inv)
int ctptri_(char*, char*, int*, float*, int*);
int dtptri_(char*, char*, int*, double*, int*);
int stptri_(char*, char*, int*, float*, int*);
int ztptri_(char*, char*, int*, double*, int*);

//trtri (inv)
int strtri_(char*, char*, int*, float*, int*, int*);
int dtrtri_(char*, char*, int*, double*, int*, int*);
int ctrtri_(char*, char*, int*, float*, int*, int*);
int ztrtri_(char*, char*, int*, double*, int*, int*);

#endif /* LAPACK_INV_H */
