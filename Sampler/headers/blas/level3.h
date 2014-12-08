#ifndef BLAS_LEVEL3_H
#define BLAS_LEVEL3_H

//gemm
void	sgemm_(char*, char*, int*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	dgemm_(char*, char*, int*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);
void	cgemm_(char*, char*, int*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zgemm_(char*, char*, int*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//symm
void	ssymm_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	dsymm_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);
void	csymm_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zsymm_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//hemm
void	chemm_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zhemm_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//syrk
void	ssyrk_(char*, char*, int*, int*, float*, float*, int*, float*, float*, int*);
void	dsyrk_(char*, char*, int*, int*, double*, double*, int*, double*, double*, int*);
void	csyrk_(char*, char*, int*, int*, float*, float*, int*, float*, float*, int*);
void	zsyrk_(char*, char*, int*, int*, double*, double*, int*, double*, double*, int*);

//herk
void	cherk_(char*, char*, int*, int*, float*, float*, int*, float*, float*, int*);
void	zherk_(char*, char*, int*, int*, double*, double*, int*, double*, double*, int*);

//syr2k
void	ssyr2k_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	dsyr2k_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);
void	csyr2k_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zsyr2k_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//her2k
void	cher2k_(char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*);
void	zher2k_(char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*);

//trmm
void	strmm_(char*, char*, char*, char*, int*, int*, float*, float*, int*, float*, int*);
void	dtrmm_(char*, char*, char*, char*, int*, int*, double*, double*, int*, double*, int*);
void	ctrmm_(char*, char*, char*, char*, int*, int*, float*, float*, int*, float*, int*);
void	ztrmm_(char*, char*, char*, char*, int*, int*, double*, double*, int*, double*, int*);

//trsm
void	strsm_(char*, char*, char*, char*, int*, int*, float*, float*, int*, float*, int*);
void	dtrsm_(char*, char*, char*, char*, int*, int*, double*, double*, int*, double*, int*);
void	ctrsm_(char*, char*, char*, char*, int*, int*, float*, float*, int*, float*, int*);
void	ztrsm_(char*, char*, char*, char*, int*, int*, double*, double*, int*, double*, int*);

#endif /* BLAS_LEVEL3_H */
