#ifndef BLAS_LEVEL1_H
#define BLAS_LEVEL1_H

#include "../types.h"

//rotg
void	srotg_(float*, float*, float*, float*);
void	drotg_(double*, double*, double*, double*);

//rotmg
void	srotmg_(float*, float*, float*, float*, float*);
void	drotmg_(double*, double*, double*, double*, double*);

//rot
void	srot_(int*, float*, int*, float*, int*, float*, float*);
void	drot_(int*, double*, int*, double*, int*, double*, double*);

//rotm
void	srotm_(int*, float*, int*, float*, int*, float*);
void	drotm_(int*, double*, int*, double*, int*, double*);

//swap
void	sswap_(int*, float*, int*, float*, int*);
void	dswap_(int*, double*, int*, double*, int*);
void	cswap_(int*, float*, int*, float*, int*);
void	zswap_(int*, double*, int*, double*, int*);

//scal
void	sscal_(int*, float*, float*, int*);
void	dscal_(int*, double*, double*, int*);
void	cscal_(int*, float*, float*, int*);
void	zscal_(int*, double*, double*, int*);
void	csscal_(int*, float*, float*, int*);
void	zdscal_(int*, double*, double*, int*);

//copy
void	scopy_(int*, float*, int*, float*, int*);
void	dcopy_(int*, double*, int*, double*, int*);
void	ccopy_(int*, float*, int*, float*, int*);
void	zcopy_(int*, double*, int*, double*, int*);

//axpy
void	saxpy_(int*, float*, float*, int*, float*, int*);
void	daxpy_(int*, double*, double*, int*, double*, int*);
void	caxpy_(int*, float*, float*, int*, float*, int*);
void	zaxpy_(int*, double*, double*, int*, double*, int*);

//dot
float	sdot_(int*, float*, int*, float*, int*);
double	ddot_(int*, double*, int*, double*, int*);
double	dsdot_(int*, float*, int*, float*, int*);

//dotu
floatc_t    cdotu_(int*, float*, int*, float*, int*);
doublec_t   zdotu_(int*, double*, int*, double*, int*);

//dotc
floatc_t cdotc_(int*, float*, int*, float*, int*);
doublec_t zdotc_(int*, double*, int*, double*, int*);

//dot
float   sdsdot_(int*, float*, float*, int*, float*, int*);

//nrm2
float	snrm2_(int*, float*, int*);
double	dnrm2_(int*, double*, int*);
float	scnrm2_(int*, float*, int*);
double	dznrm2_(int*, double*, int*);

//asum
float	sasum_(int*, float*, int*);
double	dasum_(int*, double*, int*);
float	scasum_(int*, float*, int*);
double	dzasum_(int*, double*, int*);

//i~amax
int	isamax_(int*, float*, int*);
int	idamax_(int*, double*, int*);
int	icamax_(int*, float*, int*);
int	izamax_(int*, double*, int*);

#endif /* BLAS_LEVEL1_H */
