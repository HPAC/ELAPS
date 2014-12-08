#ifndef LAPACK_EXPERT_SYEV_H
#define LAPACK_EXPERT_SYEV_H

////////////////////////////////////////////////////////////////////////////////
// Expert and RRR Driver Routines for Standard and Generalized Symmetric Eigenvalue Problems
////////////////////////////////////////////////////////////////////////////////

//syevx
int ssyevx_(char*, char*, char*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*, int*);
int dsyevx_(char*, char*, char*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*, int*);

//heevx
int cheevx_(char*, char*, char*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*, int*);
int zheevx_(char*, char*, char*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*, int*);

//syevr
int ssyevr_(char*, char*, char*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, int*, float*, int*, int*, int*, int*);
int dsyevr_(char*, char*, char*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, int*, double*, int*, int*, int*, int*);

//heevr
int cheevr_(char*, char*, char*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, int*, int*, int*, int*);
int zheevr_(char*, char*, char*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, int*, int*, int*, int*);

//sygvx
int ssygvx_(int*, char*, char*, char*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*, int*);
int dsygvx_(int*, char*, char*, char*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*, int*);

//hegvx
int chegvx_(int*, char*, char*, char*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*, int*);
int zhegvx_(int*, char*, char*, char*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*, int*);

//spevx
int sspevx_(char*, char*, char*, int*, float*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*);
int dspevx_(char*, char*, char*, int*, double*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*);

//hpevx
int chpevx_(char*, char*, char*, int*, float*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*, int*);
int zhpevx_(char*, char*, char*, int*, double*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*, int*);

//spgvx
int sspgvx_(int*, char*, char*, char*, int*, float*, float*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*);
int dspgvx_(int*, char*, char*, char*, int*, double*, double*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*);

//hpgvx
int chpgvx_(int*, char*, char*, char*, int*, float*, float*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*, int*);
int zhpgvx_(int*, char*, char*, char*, int*, double*, double*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*, int*);

//sbevx
int ssbevx_(char*, char*, char*, int*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*);
int dsbevx_(char*, char*, char*, int*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*);

//hbevx
int chbevx_(char*, char*, char*, int*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*, int*);
int zhbevx_(char*, char*, char*, int*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*, int*);

//sbgvx
int ssbgvx_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*);
int dsbgvx_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*);

//hbgvx
int chbgvx_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*, int*);
int zhbgvx_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*, int*);

//stevx
int sstevx_(char*, char*, int*, float*, float*, float*, float*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*, int*);
int dstevx_(char*, char*, int*, double*, double*, double*, double*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*, int*);

//stevr
int sstevr_(char*, char*, int*, float*, float*, float*, float*, int*, int*, float*, int*, float*, float*, int*, int*, float*, int*, int*, int*, int*);
int dstevr_(char*, char*, int*, double*, double*, double*, double*, int*, int*, double*, int*, double*, double*, int*, int*, double*, int*, int*, int*, int*);

#endif /* LAPACK_EXPERT_SYEV_H */
