#ifndef LAPACK_SIMPLE_LS_H
#define LAPACK_SIMPLE_LS_H

////////////////////////////////////////////////////////////////////////////////
// Simple Driver Routines for Standard and Generalized Linear Least Squares Problems
////////////////////////////////////////////////////////////////////////////////

//gels
int sgels_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, int*);
int dgels_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, int*);
int cgels_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, int*);
int zgels_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, int*);

//gglse
int sgglse_(int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dgglse_(int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);
int cgglse_(int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int zgglse_(int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, int*);

//ggglh MISSING

#endif /* LAPACK_SIMPLE_LS_H */
