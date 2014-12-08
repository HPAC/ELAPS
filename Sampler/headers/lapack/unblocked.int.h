#ifndef LAPACK_UNBLOCKED_H
#define LAPACK_UNBLOCKED_H

////////////////////////////////////////////////////////////////////////////////
// Unblocked routines (found by hand)
////////////////////////////////////////////////////////////////////////////////

//getf2
int sgetf2_(int*, int*, float*, int*, int*, int*);
int dgetf2_(int*, int*, double*, int*, int*, int*);
int cgetf2_(int*, int*, float*, int*, int*, int*);
int zgetf2_(int*, int*, double*, int*, int*, int*);

//hegs2
int chegs2_(int*, char*, int*, float*, int*, float*, int*, int*);
int zhegs2_(int*, char*, int*, double*, int*, double*, int*, int*);

//hetd2
int chetd2_(char*, int*, float*, int*, float*, float*, float*, int*);
int zhetd2_(char*, int*, double*, int*, double*, double*, double*, int*);

//hetf2
int chetf2_(char*, int*, float*, int*, int*, int*);
int zhetf2_(char*, int*, double*, int*, int*, int*);

//lauu2
int slauu2_(char*, int*, float*, int*, int*);
int dlauu2_(char*, int*, double*, int*, int*);
int clauu2_(char*, int*, float*, int*, int*);
int zlauu2_(char*, int*, double*, int*, int*);

//pbtf2
int spbtf2_(char*, int*, int*, float*, int*, int*);
int dpbtf2_(char*, int*, int*, double*, int*, int*);
int cpbtf2_(char*, int*, int*, float*, int*, int*);
int zpbtf2_(char*, int*, int*, double*, int*, int*);

//potf2
int spotf2_(char*, int*, float*, int*, int*);
int dpotf2_(char*, int*, double*, int*, int*);
int cpotf2_(char*, int*, float*, int*, int*);
int zpotf2_(char*, int*, double*, int*, int*);

//sytf2
int ssytf2_(char*, int*, float*, int*, int*, int*);
int dsytf2_(char*, int*, double*, int*, int*, int*);
int csytf2_(char*, int*, float*, int*, int*, int*);
int zsytf2_(char*, int*, double*, int*, int*, int*);

//tgsy2
int stgsy2_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*, int*);
int dtgsy2_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*, int*);
int ctgsy2_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*);
int ztgsy2_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*);

//trti2
int strti2_(char*, char*, int*, float*, int*, int*);
int dtrti2_(char*, char*, int*, double*, int*, int*);
int ctrti2_(char*, char*, int*, float*, int*, int*);
int ztrti2_(char*, char*, int*, double*, int*, int*);

//ung2l
int cung2l_(int*, int*, int*, float*, int*, float*, float*, int*);
int zung2l_(int*, int*, int*, double*, int*, double*, double*, int*);

//ungl2
int cungl2_(int*, int*, int*, float*, int*, float*, float*, int*);
int zungl2_(int*, int*, int*, double*, int*, double*, double*, int*);

//ungr2
int cungr2_(int*, int*, int*, float*, int*, float*, float*, int*);
int zungr2_(int*, int*, int*, double*, int*, double*, double*, int*);

//unm2l
int cunm2l_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int zunm2l_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//unm2r
int cunm2r_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int zunm2r_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//unml2
int cunml2_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int zunml2_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//unmr2
int cunmr2_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int zunmr2_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//unmr3
int cunmr3_(char*, char*, int*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int zunmr3_(char*, char*, int*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//org2l
int sorg2l_(int*, int*, int*, float*, int*, float*, float*, int*);
int dorg2l_(int*, int*, int*, double*, int*, double*, double*, int*);

//org2r
int sorg2r_(int*, int*, int*, float*, int*, float*, float*, int*);
int dorg2r_(int*, int*, int*, double*, int*, double*, double*, int*);

//orgr2
int sorgr2_(int*, int*, int*, float*, int*, float*, float*, int*);
int dorgr2_(int*, int*, int*, double*, int*, double*, double*, int*);

//orm2l
int sorm2l_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int dorm2l_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//orm2r
int sorm2r_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int dorm2r_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//orml2
int sorml2_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int dorml2_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//ormr2
int sormr2_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int dormr2_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//ormr3
int sormr3_(char*, char*, int*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*);
int dormr3_(char*, char*, int*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*);

//sygs2
int ssygs2_(int*, char*, int*, float*, int*, float*, int*, int*);
int dsygs2_(int*, char*, int*, double*, int*, double*, int*, int*);

//sytd2
int ssytd2_(char*, int*, float*, int*, float*, float*, float*, int*);
int dsytd2_(char*, int*, double*, int*, double*, double*, double*, int*);

//gbtf2
int sgbtf2_(int*, int*, int*, int*, float*, int*, int*, int*);
int dgbtf2_(int*, int*, int*, int*, double*, int*, int*, int*);
int cgbtf2_(int*, int*, int*, int*, float*, int*, int*, int*);
int zgbtf2_(int*, int*, int*, int*, double*, int*, int*, int*);

//gebd2
int sgebd2_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int dgebd2_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*);
int cgebd2_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zgebd2_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//gehd2
int sgehd2_(int*, int*, int*, float*, int*, float*, float*, int*);
int dgehd2_(int*, int*, int*, double*, int*, double*, double*, int*);
int cgehd2_(int*, int*, int*, float*, int*, float*, float*, int*);
int zgehd2_(int*, int*, int*, double*, int*, double*, double*, int*);

//gelq2
int sgelq2_(int*, int*, float*, int*, float*, float*, int*);
int dgelq2_(int*, int*, double*, int*, double*, double*, int*);
int cgelq2_(int*, int*, float*, int*, float*, float*, int*);
int zgelq2_(int*, int*, double*, int*, double*, double*, int*);

//geql2
int sgeql2_(int*, int*, float*, int*, float*, float*, int*);
int dgeql2_(int*, int*, double*, int*, double*, double*, int*);
int cgeql2_(int*, int*, float*, int*, float*, float*, int*);
int zgeql2_(int*, int*, double*, int*, double*, double*, int*);

//geqr2
int sgeqr2_(int*, int*, float*, int*, float*, float*, int*);
int dgeqr2_(int*, int*, double*, int*, double*, double*, int*);
int cgeqr2_(int*, int*, float*, int*, float*, float*, int*);
int zgeqr2_(int*, int*, double*, int*, double*, double*, int*);

//gerq2
int sgerq2_(int*, int*, float*, int*, float*, float*, int*);
int dgerq2_(int*, int*, double*, int*, double*, double*, int*);
int cgerq2_(int*, int*, float*, int*, float*, float*, int*);
int zgerq2_(int*, int*, double*, int*, double*, double*, int*);

//latrd
int clatrd_(char*, int*, int*, float*, int*, float*, float*, float*, int*);
int dlatrd_(char*, int*, int*, double*, int*, double*, double*, double*, int*);
int slatrd_(char*, int*, int*, float*, int*, float*, float*, float*, int*);
int zlatrd_(char*, int*, int*, double*, int*, double*, double*, double*, int*);

#endif /* LAPACK_UNBLOCKED_H */
