#ifndef LAPACK_UNBLOCKED_H
#define LAPACK_UNBLOCKED_H

////////////////////////////////////////////////////////////////////////////////
// Unblocked routines (found by hand)
////////////////////////////////////////////////////////////////////////////////

//getf2
void sgetf2_(int*, int*, float*, int*, int*, int*);
void dgetf2_(int*, int*, double*, int*, int*, int*);
void cgetf2_(int*, int*, float*, int*, int*, int*);
void zgetf2_(int*, int*, double*, int*, int*, int*);

//hegs2
void chegs2_(int*, char*, int*, float*, int*, float*, int*, int*);
void zhegs2_(int*, char*, int*, double*, int*, double*, int*, int*);

//hetd2
void chetd2_(char*, int*, float*, int*, float*, float*, float*, int*);
void zhetd2_(char*, int*, double*, int*, double*, double*, double*, int*);

//hetf2
void chetf2_(char*, int*, float*, int*, int*, int*);
void zhetf2_(char*, int*, double*, int*, int*, int*);

//lauu2
void slauu2_(char*, int*, float*, int*, int*);
void dlauu2_(char*, int*, double*, int*, int*);
void clauu2_(char*, int*, float*, int*, int*);
void zlauu2_(char*, int*, double*, int*, int*);

//pbtf2
void spbtf2_(char*, int*, int*, float*, int*, int*);
void dpbtf2_(char*, int*, int*, double*, int*, int*);
void cpbtf2_(char*, int*, int*, float*, int*, int*);
void zpbtf2_(char*, int*, int*, double*, int*, int*);

//potf2
void spotf2_(char*, int*, float*, int*, int*);
void dpotf2_(char*, int*, double*, int*, int*);
void cpotf2_(char*, int*, float*, int*, int*);
void zpotf2_(char*, int*, double*, int*, int*);

//sytf2
void ssytf2_(char*, int*, float*, int*, int*, int*);
void dsytf2_(char*, int*, double*, int*, int*, int*);
void csytf2_(char*, int*, float*, int*, int*, int*);
void zsytf2_(char*, int*, double*, int*, int*, int*);

//tgsy2
void stgsy2_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*, int*);
void dtgsy2_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*, int*);
void ctgsy2_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*);
void ztgsy2_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*);

//trti2
void strti2_(char*, char*, int*, float*, int*, int*);
void dtrti2_(char*, char*, int*, double*, int*, int*);
void ctrti2_(char*, char*, int*, float*, int*, int*);
void ztrti2_(char*, char*, int*, double*, int*, int*);

//ung2l
void cung2l_(int*, int*, int*, float*, int*, float*, float*, int*);
void zung2l_(int*, int*, int*, double*, int*, double*, double*, int*);

//ungl2
void cungl2_(int*, int*, int*, float*, int*, float*, float*, int*);
void zungl2_(int*, int*, int*, double*, int*, double*, double*, int*);

//ungr2
void cungr2_(int*, int*, int*, float*, int*, float*, float*, int*);
void zungr2_(int*, int*, int*, double*, int*, double*, double*, int*);

//unm2l
void cunm2l_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void zunm2l_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//unm2r
void cunm2r_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void zunm2r_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//unml2
void cunml2_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void zunml2_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//unmr2
void cunmr2_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void zunmr2_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//unmr3
void cunmr3_(char*, char*, int*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void zunmr3_(char*, char*, int*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//org2l
void sorg2l_(int*, int*, int*, float*, int*, float*, float*, int*);
void dorg2l_(int*, int*, int*, double*, int*, double*, double*, int*);

//org2r
void sorg2r_(int*, int*, int*, float*, int*, float*, float*, int*);
void dorg2r_(int*, int*, int*, double*, int*, double*, double*, int*);

//orgr2
void sorgr2_(int*, int*, int*, float*, int*, float*, float*, int*);
void dorgr2_(int*, int*, int*, double*, int*, double*, double*, int*);

//orm2l
void sorm2l_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void dorm2l_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//orm2r
void sorm2r_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void dorm2r_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//orml2
void sorml2_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void dorml2_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//ormr2
void sormr2_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void dormr2_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//ormr3
void sormr3_(char*, char*, int*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
void dormr3_(char*, char*, int*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//sygs2
void ssygs2_(int*, char*, int*, float*, int*, float*, int*, int*);
void dsygs2_(int*, char*, int*, double*, int*, double*, int*, int*);

//sytd2
void ssytd2_(char*, int*, float*, int*, float*, float*, float*, int*);
void dsytd2_(char*, int*, double*, int*, double*, double*, double*, int*);

//gbtf2
void sgbtf2_(int*, int*, int*, int*, float*, int*, int*, int*);
void dgbtf2_(int*, int*, int*, int*, double*, int*, int*, int*);
void cgbtf2_(int*, int*, int*, int*, float*, int*, int*, int*);
void zgbtf2_(int*, int*, int*, int*, double*, int*, int*, int*);

//gebd2
void sgebd2_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
void dgebd2_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*);
void cgebd2_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
void zgebd2_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//gehd2
void sgehd2_(int*, int*, int*, float*, int*, float*, float*, int*);
void dgehd2_(int*, int*, int*, double*, int*, double*, double*, int*);
void cgehd2_(int*, int*, int*, float*, int*, float*, float*, int*);
void zgehd2_(int*, int*, int*, double*, int*, double*, double*, int*);

//gelq2
void sgelq2_(int*, int*, float*, int*, float*, float*, int*);
void dgelq2_(int*, int*, double*, int*, double*, double*, int*);
void cgelq2_(int*, int*, float*, int*, float*, float*, int*);
void zgelq2_(int*, int*, double*, int*, double*, double*, int*);

//geql2
void sgeql2_(int*, int*, float*, int*, float*, float*, int*);
void dgeql2_(int*, int*, double*, int*, double*, double*, int*);
void cgeql2_(int*, int*, float*, int*, float*, float*, int*);
void zgeql2_(int*, int*, double*, int*, double*, double*, int*);

//geqr2
void sgeqr2_(int*, int*, float*, int*, float*, float*, int*);
void dgeqr2_(int*, int*, double*, int*, double*, double*, int*);
void cgeqr2_(int*, int*, float*, int*, float*, float*, int*);
void zgeqr2_(int*, int*, double*, int*, double*, double*, int*);

//gerq2
void sgerq2_(int*, int*, float*, int*, float*, float*, int*);
void dgerq2_(int*, int*, double*, int*, double*, double*, int*);
void cgerq2_(int*, int*, float*, int*, float*, float*, int*);
void zgerq2_(int*, int*, double*, int*, double*, double*, int*);

//latrd
void clatrd_(char*, int*, int*, float*, int*, float*, float*, float*, int*);
void dlatrd_(char*, int*, int*, double*, int*, double*, double*, double*, int*);
void slatrd_(char*, int*, int*, float*, int*, float*, float*, float*, int*);
void zlatrd_(char*, int*, int*, double*, int*, double*, double*, double*, int*);

//larft
void slarft_(char*, char*, int*, int*, float*, int*, float*, float*, int*);
void dlarft_(char*, char*, int*, int*, double*, int*, double*, double*, int*);
void clarft_(char*, char*, int*, int*, float*, int*, float*, float*, int*);
void zlarft_(char*, char*, int*, int*, double*, int*, double*, double*, int*);

#endif /* LAPACK_UNBLOCKED_H */
