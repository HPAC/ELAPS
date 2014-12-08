#ifndef LAPACK_EIGKERNEL_H
#define LAPACK_EIGKERNEL_H

////////////////////////////////////////////////////////////////////////////////
// EIG kernels
////////////////////////////////////////////////////////////////////////////////

//hsein (II for EIG)
int shsein_(char*, char*, char*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*, int*, float*, int*, int*, int*);
int dhsein_(char*, char*, char*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*, int*, double*, int*, int*, int*);
int chsein_(char*, char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*, float*, float*, int*, int*, int*);
int zhsein_(char*, char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*, double*, double*, int*, int*, int*);

//hseqr (EVs + Schur)
int shseqr_(char*, char*, int*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*);
int dhseqr_(char*, char*, int*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*);
int chseqr_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zhseqr_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//pteqr (tridiag EIG)
int spteqr_(char*, int*, float*, float*, float*, int*, float*, int*);
int dpteqr_(char*, int*, double*, double*, double*, int*, double*, int*);
int cpteqr_(char*, int*, float*, float*, float*, int*, float*, int*);
int zpteqr_(char*, int*, double*, double*, double*, int*, double*, int*);

//stebz (tridiag EIG)
int sstebz_(char*, char*, int*, float*, float*, int*, int*, float*, float*, float*, int*, int*, float*, int*, int*, float*, int*, int*);
int dstebz_(char*, char*, int*, double*, double*, int*, int*, double*, double*, double*, int*, int*, double*, int*, int*, double*, int*, int*);

//stedc (tridiag EIG by DC)
int sstedc_(char*, int*, float*, float*, float*, int*, float*, int*, int*, int*, int*);
int dstedc_(char*, int*, double*, double*, double*, int*, double*, int*, int*, int*, int*);
int cstedc_(char*, int*, float*, float*, float*, int*, float*, int*, float*, int*, int*, int*, int*);
int zstedc_(char*, int*, double*, double*, double*, int*, double*, int*, double*, int*, int*, int*, int*);

//stegr (tridiag EIG)
int sstegr_(char*, char*, int*, float*, float*, float*, float*, int*, int*, float*, int*, float*, float*, int*, int*, float*, int*, int*, int*, int*);
int dstegr_(char*, char*, int*, double*, double*, double*, double*, int*, int*, double*, int*, double*, double*, int*, int*, double*, int*, int*, int*, int*);
int cstegr_(char*, char*, int*, float*, float*, float*, float*, int*, int*, float*, int*, float*, float*, int*, int*, float*, int*, int*, int*, int*);
int zstegr_(char*, char*, int*, double*, double*, double*, double*, int*, int*, double*, int*, double*, double*, int*, int*, double*, int*, int*, int*, int*);

//stein (tridag EIG by II)
int sstein_(int*, float*, float*, int*, float*, int*, int*, float*, int*, float*, int*, int*, int*);
int dstein_(int*, double*, double*, int*, double*, int*, int*, double*, int*, double*, int*, int*, int*);
int cstein_(int*, float*, float*, int*, float*, int*, int*, float*, int*, float*, int*, int*, int*);
int zstein_(int*, double*, double*, int*, double*, int*, int*, double*, int*, double*, int*, int*, int*);

//stemr (tridag EIG by MRRR)
int sstemr_(char*, char*, int*, float*, float*, float*, float*, int*, int*, int*, float*, float*, int*, int*, int*, int*, float*, int*, int*, int*, int*);
int dstemr_(char*, char*, int*, double*, double*, double*, double*, int*, int*, int*, double*, double*, int*, int*, int*, int*, double*, int*, int*, int*, int*);
int cstemr_(char*, char*, int*, float*, float*, float*, float*, int*, int*, int*, float*, float*, int*, int*, int*, int*, float*, int*, int*, int*, int*);
int zstemr_(char*, char*, int*, double*, double*, double*, double*, int*, int*, int*, double*, double*, int*, int*, int*, int*, double*, int*, int*, int*, int*);

//steqr (tridiag EIG by QR)
int ssteqr_(char*, int*, float*, float*, float*, int*, float*, int*);
int dsteqr_(char*, int*, double*, double*, double*, int*, double*, int*);
int csteqr_(char*, int*, float*, float*, float*, int*, float*, int*);
int zsteqr_(char*, int*, double*, double*, double*, int*, double*, int*);

//sterf (tridiag EIG by QR variant)
int ssterf_(int*, float*, float*, int*);
int dsterf_(int*, double*, double*, int*);

#endif /* LAPACK_EIGKERNEL_H */
