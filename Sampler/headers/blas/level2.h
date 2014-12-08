#ifndef BLAS_LEVEL2_H
#define BLAS_LEVEL2_H

//gemv
void	sgemv_(char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	dgemv_(char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);
void	cgemv_(char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zgemv_(char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//gbmv
void	sgbmv_(char*, int*, int*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	dgbmv_(char*, int*, int*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);
void	cgbmv_(char*, int*, int*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zgbmv_(char*, int*, int*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//hemv
void	chemv_(char*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zhemv_(char*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//hbmv
void	chbmv_(char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zhbmv_(char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//hpmv
void	chpmv_(char*, int*, float*, float*, float*, int*, float*, float*, int*);
void	zhpmv_(char*, int*, double*, double*, double*, int*, double*, double*, int*);

//symv
void	ssymv_(char*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	dsymv_(char*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//sbmv
void	ssbmv_(char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	dsbmv_(char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//spmv
void	sspmv_(char*, int*, float*, float*, float*, int*, float*, float*, int*);
void	dspmv_(char*, int*, double*, double*, double*, int*, double*, double*, int*);

//trmv
void	strmv_(char*, char*, char*, int*, float*, int*, float*, int*);
void	dtrmv_(char*, char*, char*, int*, double*, int*, double*, int*);
void	ctrmv_(char*, char*, char*, int*, float*, int*, float*, int*);
void	ztrmv_(char*, char*, char*, int*, double*, int*, double*, int*);

//tbmv
void	stbmv_(char*, char*, char*, int*, int*, float*, int*, float*, int*);
void	dtbmv_(char*, char*, char*, int*, int*, double*, int*, double*, int*);
void	ctbmv_(char*, char*, char*, int*, int*, float*, int*, float*, int*);
void	ztbmv_(char*, char*, char*, int*, int*, double*, int*, double*, int*);

//tpmv
void	stpmv_(char*, char*, char*, int*, float*, float*, int*);
void	dtpmv_(char*, char*, char*, int*, double*, double*, int*);
void	ctpmv_(char*, char*, char*, int*, float*, float*, int*);
void	ztpmv_(char*, char*, char*, int*, double*, double*, int*);

//trsv
void	strsv_(char*, char*, char*, int*, float*, int*, float*, int*);
void	dtrsv_(char*, char*, char*, int*, double*, int*, double*, int*);
void	ctrsv_(char*, char*, char*, int*, float*, int*, float*, int*);
void	ztrsv_(char*, char*, char*, int*, double*, int*, double*, int*);

//tbsv
void	stbsv_(char*, char*, char*, int*, int*, float*, int*, float*, int*);
void	dtbsv_(char*, char*, char*, int*, int*, double*, int*, double*, int*);
void	ctbsv_(char*, char*, char*, int*, int*, float*, int*, float*, int*);
void	ztbsv_(char*, char*, char*, int*, int*, double*, int*, double*, int*);

//tpsv
void	stpsv_(char*, char*, char*, int*, float*, float*, int*);
void	dtpsv_(char*, char*, char*, int*, double*, double*, int*);
void	ctpsv_(char*, char*, char*, int*, float*, float*, int*);
void	ztpsv_(char*, char*, char*, int*, double*, double*, int*);

//ger
void	sger_(int*, int*, float*, float*, int*, float*, int*, float*, int*);
void	dger_(int*, int*, double*, double*, int*, double*, int*, double*, int*);

//geru
void	cgeru_(int*, int*, float*, float*, int*, float*, int*, float*, int*);
void	zgeru_(int*, int*, double*, double*, int*, double*, int*, double*, int*);

//gerc
void	cgerc_(int*, int*, float*, float*, int*, float*, int*, float*, int*);
void	zgerc_(int*, int*, double*, double*, int*, double*, int*, double*, int*);

//her
void	cher_(char*, int*, float *, float*, int*, float*, int*);
void	zher_(char*, int*, double*, double*, int*, double*, int*);

//hpr
void	chpr_(char*, int*, float *, float*, int*, float*);
void	zhpr_(char*, int*, double*, double*, int*, double*);

//her2
void	cher2_(char*, int*, float *, float*, int*, float*, int*, float*, int*);
void	zher2_(char*, int*, double*, double*, int*, double*, int*, double*, int*);

//hpr2
void	chpr2_(char*, int*, float *, float*, int*, float*, int*, float*);
void	zhpr2_(char*, int*, double*, double*, int*, double*, int*, double*);

//syr
void	ssyr_(char*, int*, float *, float*, int*, float*, int*);
void	dsyr_(char*, int*, double*, double*, int*, double*, int*);

//spr
void	sspr_(char*, int*, float *, float*, int*, float*);
void	dspr_(char*, int*, double*, double*, int*, double*);

//syr2
void	ssyr2_(char*, int*, float *, float*, int*, float*, int*, float*, int*);
void	dsyr2_(char*, int*, double*, double*, int*, double*, int*, double*, int*);

//spr2
void	sspr2_(char*, int*, float *, float*, int*, float*, int*, float*);
void	dspr2_(char*, int*, double*, double*, int*, double*, int*, double*);

#endif /* BLAS_LEVEL2_H */
