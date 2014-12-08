#ifndef BLAS_NONSTANDARD_H
#define BLAS_NONSTANDARD_H

//rot
int     csrot_(int*, float*, int*, float*, int*, float*, float*);
int     zdrot_(int*, double*, int*, double*, int*, double*, double*);

//symv
void	csymv_(char*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zsymv_(char*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//syr
void	csyr_(char*, int*, float *, float*, int*, float*, int*);
void	zsyr_(char*, int*, double*, double*, int*, double*, int*);

#endif /* BLAS_NONSTANDARD_H */
