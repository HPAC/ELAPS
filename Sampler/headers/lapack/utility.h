#ifndef LAPACK_SCALCPY_H
#define LAPACK_SCALCPY_H

////////////////////////////////////////////////////////////////////////////////
// copy, scale for matrices
////////////////////////////////////////////////////////////////////////////////


//lacpy
int slacpy_(char*, int*, int*, float*, int*, float*, int*);
int dlacpy_(char*, int*, int*, double*, int*, double*, int*);
int clacpy_(char*, int*, int*, float*, int*, float*, int*);
int zlacpy_(char*, int*, int*, double*, int*, double*, int*);

//lascl
int slascl_(char*, int*, int*, float*, float*, int*, int*, float*, int*, int*);
int dlascl_(char*, int*, int*, double*, double*, int*, int*, double*, int*, int*);
int clascl_(char*, int*, int*, float*, float*, int*, int*, float*, int*, int*);
int zlascl_(char*, int*, int*, double*, double*, int*, int*, double*, int*, int*);


//laswp
int slaswp_(int*, float*, int*, int*, int*, int*, int*);
int dlaswp_(int*, double*, int*, int*, int*, int*, int*);
int claswp_(int*, float*, int*, int*, int*, int*, int*);
int zlaswp_(int*, double*, int*, int*, int*, int*, int*);

// BUG
//lascl2
//int clascl2_(int*, int*, float*, float*, int*);
//int dlascl2_(int*, int*, double*, double*, int*);
//int slascl2_(int*, int*, float*, float*, int*);
//int zlascl2_(int*, int*, double*, double*, int*);

#endif /* LAPACK_SCALCPY_H */
