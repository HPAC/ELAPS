#ifndef LAPACK_EXPERT_LS_H
#define LAPACK_EXPERT_LS_H

////////////////////////////////////////////////////////////////////////////////
// Divide and Conquer and Exp ert Driver Routines for Linear Least Squares Problems
////////////////////////////////////////////////////////////////////////////////

//gelsy
int sgelsy_(int*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, int*);
int dgelsy_(int*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, int*);
int zgelsy_(int*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, int*);
int cgelsy_(int*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, int*);

//gelss
int sgelss_(int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int dgelss_(int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*, int*);
int cgelss_(int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*);
int zgelss_(int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*);

//gelsd
int sgelsd_(int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*);
int dgelsd_(int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*);
int cgelsd_(int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*);
int zgelsd_(int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*);

#endif /* LAPACK_EXPERT_LS_H */
