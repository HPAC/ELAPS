#ifndef BLAS_H
#define BLAS_H

#ifndef BLAS_UNDERSCORE
#define BLAS_UNDERSCORE 1
#endif

#ifndef BLAS
#if BLAS_UNDERSCORE
#define BLAS(name) name ## _
#else
#define BLAS(name) name
#endif
#endif

#ifndef BLAS_COMPLEX_FUNCTIONS_AS_ROUTINES
#define BLAS_COMPLEX_FUNCTIONS_AS_ROUTINES 0
#endif

#if BLAS_COMPLEX_FUNCTIONS_AS_ROUTINES
void BLAS(cdotc)(float *, const int *, const float *, const int *, const float *, const int *);
void BLAS(cdotu)(float *, const int *, const float *, const int *, const float *, const int *);
void BLAS(zdotc)(double *, const int *, const double *, const int *, const double *, const int *);
void BLAS(zdotu)(double *, const int *, const double *, const int *, const double *, const int *);
#else
#include "complex_types.h"
floatc_t BLAS(cdotc)(const int *, const float *, const int *, const float *, const int *);
floatc_t BLAS(cdotu)(const int *, const float *, const int *, const float *, const int *);
doublec_t BLAS(zdotc)(const int *, const double *, const int *, const double *, const int *);
doublec_t BLAS(zdotu)(const int *, const double *, const int *, const double *, const int *);
#endif

void BLAS(caxpy)(const int *, const float *, const float *, const int *, float *, const int *);
void BLAS(ccopy)(const int *, const float *, const int *, float *, const int *);
void BLAS(cgbmv)(const char *, const int *, const int *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(cgemm)(const char *, const char *, const int *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(cgemv)(const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(cgerc)(const int *, const int *, const float *, const float *, const int *, const float *, const int *, float *, const int *);
void BLAS(cgeru)(const int *, const int *, const float *, const float *, const int *, const float *, const int *, float *, const int *);
void BLAS(chbmv)(const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(chemm)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(chemv)(const char *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(cher)(const char *, const int *, const float *, const float *, const int *, float *, const int *);
void BLAS(cher2)(const char *, const int *, const float *, const float *, const int *, const float *, const int *, float *, const int *);
void BLAS(cher2k)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(cherk)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, float *, const int *);
void BLAS(chpmv)(const char *, const int *, const float *, const float *, const float *, const int *, const float *, float *, const int *);
void BLAS(chpr)(const char *, const int *, const float *, const float *, const int *, float *);
void BLAS(chpr2)(const char *, const int *, const float *, const float *, const int *, const float *, const int *, float *);
void BLAS(cscal)(const int *, const float *, float *, const int *);
void BLAS(csscal)(const int *, const float *, float *, const int *);
void BLAS(cswap)(const int *, float *, const int *, float *, const int *);
void BLAS(csymm)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(csyr2k)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(csyrk)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, float *, const int *);
void BLAS(ctbmv)(const char *, const char *, const char *, const int *, const int *, const float *, const int *, float *, const int *);
void BLAS(ctbsv)(const char *, const char *, const char *, const int *, const int *, const float *, const int *, float *, const int *);
void BLAS(ctpmv)(const char *, const char *, const char *, const int *, const float *, float *, const int *);
void BLAS(ctpsv)(const char *, const char *, const char *, const int *, const float *, float *, const int *);
void BLAS(ctrmm)(const char *, const char *, const char *, const char *, const int *, const int *, const float *, const float *, const int *, float *, const int *);
void BLAS(ctrmv)(const char *, const char *, const char *, const int *, const float *, const int *, float *, const int *);
void BLAS(ctrsm)(const char *, const char *, const char *, const char *, const int *, const int *, const float *, const float *, const int *, float *, const int *);
void BLAS(ctrsv)(const char *, const char *, const char *, const int *, const float *, const int *, float *, const int *);
double BLAS(dasum)(const int *, const double *, const int *);
void BLAS(daxpy)(const int *, const double *, const double *, const int *, double *, const int *);
void BLAS(dcopy)(const int *, const double *, const int *, double *, const int *);
double BLAS(ddot)(const int *, const double *, const int *, const double *, const int *);
void BLAS(dgbmv)(const char *, const int *, const int *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(dgemm)(const char *, const char *, const int *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(dgemv)(const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(dger)(const int *, const int *, const double *, const double *, const int *, const double *, const int *, double *, const int *);
double BLAS(dnrm2)(const int *, const double *, const int *);
void BLAS(drot)(const int *, double *, const int *, double *, const int *, const double *, const double *);
void BLAS(drotg)(double *, double *, double *, double *);
void BLAS(drotm)(const int *, double *, const int *, double *, const int *, const double *);
void BLAS(drotmg)(double *, double *, double *, const double *, double *);
void BLAS(dsbmv)(const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(dscal)(const int *, const double *, double *, const int *);
double BLAS(dsdot)(const int *, const float *, const int *, const float *, const int *);
void BLAS(dspmv)(const char *, const int *, const double *, const double *, const double *, const int *, const double *, double *, const int *);
void BLAS(dspr)(const char *, const int *, const double *, const double *, const int *, double *);
void BLAS(dspr2)(const char *, const int *, const double *, const double *, const int *, const double *, const int *, double *);
void BLAS(dswap)(const int *, double *, const int *, double *, const int *);
void BLAS(dsymm)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(dsymv)(const char *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(dsyr)(const char *, const int *, const double *, const double *, const int *, double *, const int *);
void BLAS(dsyr2)(const char *, const int *, const double *, const double *, const int *, const double *, const int *, double *, const int *);
void BLAS(dsyr2k)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(dsyrk)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, double *, const int *);
void BLAS(dtbmv)(const char *, const char *, const char *, const int *, const int *, const double *, const int *, double *, const int *);
void BLAS(dtbsv)(const char *, const char *, const char *, const int *, const int *, const double *, const int *, double *, const int *);
void BLAS(dtpmv)(const char *, const char *, const char *, const int *, const double *, double *, const int *);
void BLAS(dtpsv)(const char *, const char *, const char *, const int *, const double *, double *, const int *);
void BLAS(dtrmm)(const char *, const char *, const char *, const char *, const int *, const int *, const double *, const double *, const int *, double *, const int *);
void BLAS(dtrmv)(const char *, const char *, const char *, const int *, const double *, const int *, double *, const int *);
void BLAS(dtrsm)(const char *, const char *, const char *, const char *, const int *, const int *, const double *, const double *, const int *, double *, const int *);
void BLAS(dtrsv)(const char *, const char *, const char *, const int *, const double *, const int *, double *, const int *);
double BLAS(dzasum)(const int *, const double *, const int *);
double BLAS(dznrm2)(const int *, const double *, const int *);
int BLAS(icamax)(const int *, const float *, const int *);
int BLAS(idamax)(const int *, const double *, const int *);
int BLAS(isamax)(const int *, const float *, const int *);
int BLAS(izamax)(const int *, const double *, const int *);
float BLAS(sasum)(const int *, const float *, const int *);
void BLAS(saxpy)(const int *, const float *, const float *, const int *, float *, const int *);
float BLAS(scasum)(const int *, const float *, const int *);
float BLAS(scnrm2)(const int *, const float *, const int *);
void BLAS(scopy)(const int *, const float *, const int *, float *, const int *);
float BLAS(sdot)(const int *, const float *, const int *, const float *, const int *);
float BLAS(sdsdot)(const int *, const float *, const float *, const int *, const float *, const int *);
void BLAS(sgbmv)(const char *, const int *, const int *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(sgemm)(const char *, const char *, const int *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(sgemv)(const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(sger)(const int *, const int *, const float *, const float *, const int *, const float *, const int *, float *, const int *);
float BLAS(snrm2)(const int *, const float *, const int *);
void BLAS(srot)(const int *, float *, const int *, float *, const int *, const float *, const float *);
void BLAS(srotg)(float *,float *,float *,float *);
void BLAS(srotm)(const int *, float *, const int *, float *, const int *, const float *);
void BLAS(srotmg)(float *, float *, float *, const float *, float *);
void BLAS(ssbmv)(const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(sscal)(const int *, const float *, float *, const int *);
void BLAS(sspmv)(const char *, const int *, const float *, const float *, const float *, const int *, const float *, float *, const int *);
void BLAS(sspr)(const char *, const int *, const float *, const float *, const int *, float *);
void BLAS(sspr2)(const char *, const int *, const float *, const float *, const int *, const float *, const int *, float *);
void BLAS(sswap)(const int *, float *, const int *, float *, const int *);
void BLAS(ssymm)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(ssymv)(const char *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(ssyr)(const char *, const int *, const float *, const float *, const int *, float *, const int *);
void BLAS(ssyr2)(const char *, const int *, const float *, const float *, const int *, const float *, const int *, float *, const int *);
void BLAS(ssyr2k)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, const int *, const float *, float *, const int *);
void BLAS(ssyrk)(const char *, const char *, const int *, const int *, const float *, const float *, const int *, const float *, float *, const int *);
void BLAS(stbmv)(const char *, const char *, const char *, const int *, const int *, const float *, const int *, float *, const int *);
void BLAS(stbsv)(const char *, const char *, const char *, const int *, const int *, const float *, const int *, float *, const int *);
void BLAS(stpmv)(const char *, const char *, const char *, const int *, const float *, float *, const int *);
void BLAS(stpsv)(const char *, const char *, const char *, const int *, const float *, float *, const int *);
void BLAS(strmm)(const char *, const char *, const char *, const char *, const int *, const int *, const float *, const float *, const int *, float *, const int *);
void BLAS(strmv)(const char *, const char *, const char *, const int *, const float *, const int *, float *, const int *);
void BLAS(strsm)(const char *, const char *, const char *, const char *, const int *, const int *, const float *, const float *, const int *, float *, const int *);
void BLAS(strsv)(const char *, const char *, const char *, const int *, const float *, const int *, float *, const int *);
void BLAS(zaxpy)(const int *, const double *, const double *, const int *, double *, const int *);
void BLAS(zcopy)(const int *, const double *, const int *, double *, const int *);
void BLAS(zdscal)(const int *, const double *, double *, const int *);
void BLAS(zgbmv)(const char *, const int *, const int *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zgemm)(const char *, const char *, const int *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zgemv)(const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zgerc)(const int *, const int *, const double *, const double *, const int *, const double *, const int *, double *, const int *);
void BLAS(zgeru)(const int *, const int *, const double *, const double *, const int *, const double *, const int *, double *, const int *);
void BLAS(zhbmv)(const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zhemm)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zhemv)(const char *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zher)(const char *, const int *, const double *, const double *, const int *, double *, const int *);
void BLAS(zher2)(const char *, const int *, const double *, const double *, const int *, const double *, const int *, double *, const int *);
void BLAS(zher2k)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zherk)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, double *, const int *);
void BLAS(zhpmv)(const char *, const int *, const double *, const double *, const double *, const int *, const double *, double *, const int *);
void BLAS(zhpr)(const char *, const int *, const double *, const double *, const int *, double *);
void BLAS(zhpr2)(const char *, const int *, const double *, const double *, const int *, const double *, const int *, double *);
void BLAS(zscal)(const int *, const double *, double *, const int *);
void BLAS(zswap)(const int *, double *, const int *, double *, const int *);
void BLAS(zsymm)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zsyr2k)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, const int *, const double *, double *, const int *);
void BLAS(zsyrk)(const char *, const char *, const int *, const int *, const double *, const double *, const int *, const double *, double *, const int *);
void BLAS(ztbmv)(const char *, const char *, const char *, const int *, const int *, const double *, const int *, double *, const int *);
void BLAS(ztbsv)(const char *, const char *, const char *, const int *, const int *, const double *, const int *, double *, const int *);
void BLAS(ztpmv)(const char *, const char *, const char *, const int *, const double *, double *, const int *);
void BLAS(ztpsv)(const char *, const char *, const char *, const int *, const double *, double *, const int *);
void BLAS(ztrmm)(const char *, const char *, const char *, const char *, const int *, const int *, const double *, const double *, const int *, double *, const int *);
void BLAS(ztrmv)(const char *, const char *, const char *, const int *, const double *, const int *, double *, const int *);
void BLAS(ztrsm)(const char *, const char *, const char *, const char *, const int *, const int *, const double *, const double *, const int *, double *, const int *);
void BLAS(ztrsv)(const char *, const char *, const char *, const int *, const double *, const int *, double *, const int *);

#endif /* BLAS_H */
