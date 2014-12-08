#ifndef LAPACK_EXPERT_EQ_H
#define LAPACK_EXPERT_EQ_H

////////////////////////////////////////////////////////////////////////////////
// Expert Driver Routines for Linear Equations
////////////////////////////////////////////////////////////////////////////////

//gesvx
int sgesvx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, char*, float*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dgesvx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, char*, double*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);
int cgesvx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, char*, float*, float*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zgesvx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, char*, double*, double*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//gbsvx
int sgbsvx_(char*, char*, int*, int*, int*, int*, float*, int*, float*, int*, int*, char*, float*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dgbsvx_(char*, char*, int*, int*, int*, int*, double*, int*, double*, int*, int*, char*, double*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);
int cgbsvx_(char*, char*, int*, int*, int*, int*, float*, int*, float*, int*, int*, char*, float*, float*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zgbsvx_(char*, char*, int*, int*, int*, int*, double*, int*, double*, int*, int*, char*, double*, double*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//gtsvx
int sgtsvx_(char*, char*, int*, int*, float*, float*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dgtsvx_(char*, char*, int*, int*, double*, double*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);
int cgtsvx_(char*, char*, int*, int*, float*, float*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zgtsvx_(char*, char*, int*, int*, double*, double*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//posvx
int sposvx_(char*, char*, int*, int*, float*, int*, float*, int*, char*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dposvx_(char*, char*, int*, int*, double*, int*, double*, int*, char*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);
int cposvx_(char*, char*, int*, int*, float*, int*, float*, int*, char*, float*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zposvx_(char*, char*, int*, int*, double*, int*, double*, int*, char*, double*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//ppsvx
int sppsvx_(char*, char*, int*, int*, float*, float*, char*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dppsvx_(char*, char*, int*, int*, double*, double*, char*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);
int cppsvx_(char*, char*, int*, int*, float*, float*, char*, float*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zppsvx_(char*, char*, int*, int*, double*, double*, char*, double*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//pbsvx
int spbsvx_(char*, char*, int*, int*, int*, float*, int*, float*, int*, char*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dpbsvx_(char*, char*, int*, int*, int*, double*, int*, double*, int*, char*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);
int cpbsvx_(char*, char*, int*, int*, int*, float*, int*, float*, int*, char*, float*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zpbsvx_(char*, char*, int*, int*, int*, double*, int*, double*, int*, char*, double*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//ptsvx
int sptsvx_(char*, int*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int dptsvx_(char*, int*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*);
int cptsvx_(char*, int*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zptsvx_(char*, int*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//sysvx
int ssysvx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*, int*);
int dsysvx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*, int*);
int csysvx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, float*, int*);
int zsysvx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, double*, int*);

//hesvx
int chesvx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, float*, int*);
int zhesvx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, double*, int*);

//spsvx
int sspsvx_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dspsvx_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);
int cspsvx_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zspsvx_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//hpsvx
int chpsvx_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zhpsvx_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

#endif /* LAPACK_EXPERT_EQ_H */
