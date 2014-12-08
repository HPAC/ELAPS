#ifndef LAPACK_SIMPLE_EQ_H
#define LAPACK_SIMPLE_EQ_H

////////////////////////////////////////////////////////////////////////////////
// Simple Driver Routines for Linear Equations
////////////////////////////////////////////////////////////////////////////////

//gesv
int sgesv_(int*, int*, float*, int*, int*, float*, int*, int*);
int dgesv_(int*, int*, double*, int*, int*, double*, int*, int*);
int cgesv_(int*, int*, float*, int*, int*, float*, int*, int*);
int zgesv_(int*, int*, double*, int*, int*, double*, int*, int*);

//gbsv
int sgbsv_(int*, int*, int*, int*, float*, int*, int*, float*, int*, int*);
int dgbsv_(int*, int*, int*, int*, double*, int*, int*, double*, int*, int*);
int cgbsv_(int*, int*, int*, int*, float*, int*, int*, float*, int*, int*);
int zgbsv_(int*, int*, int*, int*, double*, int*, int*, double*, int*, int*);

//gtsv
int sgtsv_(int*, int*, float*, float*, float*, float*, int*, int*);
int dgtsv_(int*, int*, double*, double*, double*, double*, int*, int*);
int cgtsv_(int*, int*, float*, float*, float*, float*, int*, int*);
int zgtsv_(int*, int*, double*, double*, double*, double*, int*, int*);

//posv
int sposv_(char*, int*, int*, float*, int*, float*, int*, int*);
int dposv_(char*, int*, int*, double*, int*, double*, int*, int*);
int cposv_(char*, int*, int*, float*, int*, float*, int*, int*);
int zposv_(char*, int*, int*, double*, int*, double*, int*, int*);

//ppsv
int dppsv_(char*, int*, int*, double*, double*, int*, int*);
int sppsv_(char*, int*, int*, float*, float*, int*, int*);
int cppsv_(char*, int*, int*, float*, float*, int*, int*);
int zppsv_(char*, int*, int*, double*, double*, int*, int*);

//pbsv
int spbsv_(char*, int*, int*, int*, float*, int*, float*, int*, int*);
int dpbsv_(char*, int*, int*, int*, double*, int*, double*, int*, int*);
int cpbsv_(char*, int*, int*, int*, float*, int*, float*, int*, int*);
int zpbsv_(char*, int*, int*, int*, double*, int*, double*, int*, int*);

//ptsv
int sptsv_(int*, int*, float*, float*, float*, int*, int*);
int dptsv_(int*, int*, double*, double*, double*, int*, int*);
int cptsv_(int*, int*, float*, float*, float*, int*, int*);
int zptsv_(int*, int*, double*, double*, double*, int*, int*);

//sysv
int ssysv_(char*, int*, int*, float*, int*, int*, float*, int*, float*, int*, int*);
int dsysv_(char*, int*, int*, double*, int*, int*, double*, int*, double*, int*, int*);
int csysv_(char*, int*, int*, float*, int*, int*, float*, int*, float*, int*, int*);
int zsysv_(char*, int*, int*, double*, int*, int*, double*, int*, double*, int*, int*);

//hesv
int chesv_(char*, int*, int*, float*, int*, int*, float*, int*, float*, int*, int*);
int zhesv_(char*, int*, int*, double*, int*, int*, double*, int*, double*, int*, int*);

//spsv
int sspsv_(char*, int*, int*, float*, int*, float*, int*, int*);
int dspsv_(char*, int*, int*, double*, int*, double*, int*, int*);
int cspsv_(char*, int*, int*, float*, int*, float*, int*, int*);
int zspsv_(char*, int*, int*, double*, int*, double*, int*, int*);

//hpsv
int chpsv_(char*, int*, int*, float*, int*, float*, int*, int*);
int zhpsv_(char*, int*, int*, double*, int*, double*, int*, int*);

#endif /* LAPACK_SIMPLE_EQ_H */
