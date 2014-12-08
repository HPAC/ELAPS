#ifndef LAPACK_COMPUTATIONAL_H
#define LAPACK_COMPUTATIONAL_H

////////////////////////////////////////////////////////////////////////////////
// Computational routines (found by hand)
////////////////////////////////////////////////////////////////////////////////

//bbcsd (CSD) MISSING

//bdscd (SVD)
int sbdsdc_(char*, char*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dbdsdc_(char*, char*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//bdsqr (SCD)
int sbdsqr_(char*, int*, int*, int*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int dbdsqr_(char*, int*, int*, int*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);
int cbdsqr_(char*, int*, int*, int*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int zbdsqr_(char*, int*, int*, int*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);

//disna (reciprocal condition number)
int sdisna_(char*, int*, int*, float*, float*, int*);
int ddisna_(char*, int*, int*, double*, double*, int*);

//gbbrd (banded red. to bidiagonal, orthogonal trans.)
int sgbbrd_(char*, int*, int*, int*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int dgbbrd_(char*, int*, int*, int*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);
int cgbbrd_(char*, int*, int*, int*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, int*);
int zgbbrd_(char*, int*, int*, int*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, int*);

//gbcon (banded reciprocal condition number by LU)
int sgbcon_(char*, int*, int*, int*, float*, int*, int*, float*, float*, float*, int*, int*);
int dgbcon_(char*, int*, int*, int*, double*, int*, int*, double*, double*, double*, int*, int*);
int cgbcon_(char*, int*, int*, int*, float*, int*, int*, float*, float*, float*, float*, int*);
int zgbcon_(char*, int*, int*, int*, double*, int*, int*, double*, double*, double*, double*, int*);

//gbequ (banded equilibration scaling)
int sgbequ_(int*, int*, int*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int dgbequ_(int*, int*, int*, int*, double*, int*, double*, double*, double*, double*, double*, int*);
int cgbequ_(int*, int*, int*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zgbequ_(int*, int*, int*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//gbrfs (banded linear systems)
int sgbrfs_(char*, int*, int*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dgbrfs_(char*, int*, int*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int cgbrfs_(char*, int*, int*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zgbrfs_(char*, int*, int*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//gbrfsx (banded linear systems)
//int sgbrfsx_(char*, char*, int*, int*, int*, int*, float*, int*, float*, int*, int*, float*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
//int dgbrfsx_(char*, char*, int*, int*, int*, int*, double*, int*, double*, int*, int*, double*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, int*, int*);
//int cgbrfsx_(char*, char*, int*, int*, int*, int*, float*, int*, float*, int*, int*, float*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, float*, int*);
//int zgbrfsx_(char*, char*, int*, int*, int*, int*, double*, int*, double*, int*, int*, double*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, double*, int*);

//gbtrf (LU)
int sgbtrf_(int*, int*, int*, int*, float*, int*, int*, int*);
int dgbtrf_(int*, int*, int*, int*, double*, int*, int*, int*);
int cgbtrf_(int*, int*, int*, int*, float*, int*, int*, int*);
int zgbtrf_(int*, int*, int*, int*, double*, int*, int*, int*);

//gbtrs (Linear system by LU)
int cgbtrs_(char*, int*, int*, int*, int*, float*, int*, int*, float*, int*, int*);
int dgbtrs_(char*, int*, int*, int*, int*, double*, int*, int*, double*, int*, int*);
int sgbtrs_(char*, int*, int*, int*, int*, float*, int*, int*, float*, int*, int*);
int zgbtrs_(char*, int*, int*, int*, int*, double*, int*, int*, double*, int*, int*);

//gebak (EVD backtrans)
int sgebak_(char*, char*, int*, int*, int*, float*, int*, float*, int*, int*);
int dgebak_(char*, char*, int*, int*, int*, double*, int*, double*, int*, int*);
int cgebak_(char*, char*, int*, int*, int*, float*, int*, float*, int*, int*);
int zgebak_(char*, char*, int*, int*, int*, double*, int*, double*, int*, int*);

//gebal (EVD prebalancing)
int sgebal_(char*, int*, float*, int*, int*, int*, float*, int*);
int dgebal_(char*, int*, double*, int*, int*, int*, double*, int*);
int cgebal_(char*, int*, float*, int*, int*, int*, float*, int*);
int zgebal_(char*, int*, double*, int*, int*, int*, double*, int*);

//gebrd (red. to bidiagonal, orthogonal trans.)
int sgebrd_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*, int*);
int dgebrd_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*, int*);
int cgebrd_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*, int*);
int zgebrd_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*, int*);

//gecon (reciprocal condition number by LU)
int sgecon_(char*, int*, float*, int*, float*, float*, float*, int*, int*);
int dgecon_(char*, int*, double*, int*, double*, double*, double*, int*, int*);
int cgecon_(char*, int*, float*, int*, float*, float*, float*, float*, int*);
int zgecon_(char*, int*, double*, int*, double*, double*, double*, double*, int*);

//geequ (equilibration scaling)
int sgeequ_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int dgeequ_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*);
int cgeequ_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*);
int zgeequ_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*);

//gehrd (red. to Hessenberg)
int sgehrd_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int dgehrd_(int*, int*, int*, double*, int*, double*, double*, int*, int*);
int cgehrd_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int zgehrd_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//gejsv (SVD)
int sgejsv_(char*, char*, char*, char*, char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, int*, int*, int*);
int dgejsv_(char*, char*, char*, char*, char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, int*, int*, int*);

//gelqf (LQ factorization)
int sgelqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgelqf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgelqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgelqf_(int*, int*, double*, int*, double*, double*, int*, int*);

//geqlf (QL factorization)
int sgeqlf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgeqlf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqlf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgeqlf_(int*, int*, double*, int*, double*, double*, int*, int*);

//geqp3 (QR factorization, BLAS3)
int sgeqp3_(int*, int*, float*, int*, int*, float*, float*, int*, int*);
int dgeqp3_(int*, int*, double*, int*, int*, double*, double*, int*, int*);
int cgeqp3_(int*, int*, float*, int*, int*, float*, float*, int*, float*, int*);
int zgeqp3_(int*, int*, double*, int*, int*, double*, double*, int*, double*, int*);

//geqpf (QR factorization)
int cgeqpf_(int*, int*, float*, int*, int*, float*, float*, float*, int*);
int dgeqpf_(int*, int*, double*, int*, int*, double*, double*, int*);
int sgeqpf_(int*, int*, float*, int*, int*, float*, float*, int*);
int zgeqpf_(int*, int*, double*, int*, int*, double*, double*, double*, int*);

//geqrf (QR factorization)
int sgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgeqrf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgeqrf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);

//geqrt  (QR factorization by WY repr.) MISSING
//geqrt2 (QR factorization by WY repr.) MISSING
//geqrt3 (QR factorization by WY repr.) MISSING

//gerfs (improve lin sys sol)
int sgerfs_(char*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dgerfs_(char*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int cgerfs_(char*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zgerfs_(char*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//gerfsx (improve lin sys sol)
int sgerfsx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, float*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int dgerfsx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, double*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, int*, int*);
int cgerfsx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, float*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, float*, int*);
int zgerfsx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, double*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, double*, int*);

//gerqf (RQ factorization)
int sgerqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgerqf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgerqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgerqf_(int*, int*, double*, int*, double*, double*, int*, int*);

//gesvj (SVD)
int sgesvj_(char*, char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dgesvj_(char*, char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//getrf (LU)
int sgetrf_(int*, int*, float*, int*, int*, int*);
int dgetrf_(int*, int*, double*, int*, int*, int*);
int cgetrf_(int*, int*, float*, int*, int*, int*);
int zgetrf_(int*, int*, double*, int*, int*, int*);

//getri (inverse by LU)
int sgetri_(int*, float*, int*, int*, float*, int*, int*);
int dgetri_(int*, double*, int*, int*, double*, int*, int*);
int cgetri_(int*, float*, int*, int*, float*, int*, int*);
int zgetri_(int*, double*, int*, int*, double*, int*, int*);

//getrs (lin sys by LU)
int sgetrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int dgetrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);
int cgetrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int zgetrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);

//ggbak (back transformation gen EV)
int sggbak_(char*, char*, int*, int*, int*, float*, float*, int*, float*, int*, int*);
int dggbak_(char*, char*, int*, int*, int*, double*, double*, int*, double*, int*, int*);
int cggbak_(char*, char*, int*, int*, int*, float*, float*, int*, float*, int*, int*);
int zggbak_(char*, char*, int*, int*, int*, double*, double*, int*, double*, int*, int*);

//ggbal (gen. EV prebalancing)
int sggbal_(char*, int*, float*, int*, float*, int*, int*, int*, float*, float*, float*, int*);
int dggbal_(char*, int*, double*, int*, double*, int*, int*, int*, double*, double*, double*, int*);
int cggbal_(char*, int*, float*, int*, float*, int*, int*, int*, float*, float*, float*, int*);
int zggbal_(char*, int*, double*, int*, double*, int*, int*, int*, double*, double*, double*, int*);

//gghrd (red. to U Hessenberg, orthogonal trans.)
int sgghrd_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dgghrd_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*);
int cgghrd_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int zgghrd_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//ggqrf (gen. QR)
int sggqrf_(int*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int dggqrf_(int*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*);
int cggqrf_(int*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int zggqrf_(int*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*);

//ggrqf (gen. RQ)
int sggrqf_(int*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int dggrqf_(int*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*);
int cggrqf_(int*, int*, int*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int zggrqf_(int*, int*, int*, double*, int*, double*, double*, int*, double*, double*, int*, int*);

//ggsvp (gen. SVD preprocessing)
int sggsvp_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, int*, float*, int*, int*, float*, float*, int*);
int dggsvp_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, int*, double*, int*, int*, double*, double*, int*);
int cggsvp_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, int*, float*, int*, int*, float*, float*, float*, int*);
int zggsvp_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, int*, double*, int*, int*, double*, double*, double*, int*);

//gsvj0 (SVD preprocessing)
int sgsvj0_(char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*);
int dgsvj0_(char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*);

//gsvj1 (SVD preprocessing)
int sgsvj1_(char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*);
int dgsvj1_(char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*);

//gtcon (reciprocal condidion number tridiag.)
int sgtcon_(char*, int*, float*, float*, float*, float*, int*, float*, float*, float*, int*, int*);
int dgtcon_(char*, int*, double*, double*, double*, double*, int*, double*, double*, double*, int*, int*);
int cgtcon_(char*, int*, float*, float*, float*, float*, int*, float*, float*, float*, int*);
int zgtcon_(char*, int*, double*, double*, double*, double*, int*, double*, double*, double*, int*);

//gtrfs (tridiag lin sys)
int sgtrfs_(char*, int*, int*, float*, float*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dgtrfs_(char*, int*, int*, double*, double*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int cgtrfs_(char*, int*, int*, float*, float*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zgtrfs_(char*, int*, int*, double*, double*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//gttrf (tridiag LU)
int sgttrf_(int*, float*, float*, float*, float*, int*, int*);
int dgttrf_(int*, double*, double*, double*, double*, int*, int*);
int cgttrf_(int*, float*, float*, float*, float*, int*, int*);
int zgttrf_(int*, double*, double*, double*, double*, int*, int*);

//gttrs (tridiag lin sys)
int sgttrs_(char*, int*, int*, float*, float*, float*, float*, int*, float*, int*, int*);
int dgttrs_(char*, int*, int*, double*, double*, double*, double*, int*, double*, int*, int*);
int cgttrs_(char*, int*, int*, float*, float*, float*, float*, int*, float*, int*, int*);
int zgttrs_(char*, int*, int*, double*, double*, double*, double*, int*, double*, int*, int*);

//gtts2 (tridiag lin sys) UNBLOCKED?
int sgtts2_(int*, int*, int*, float*, float*, float*, float*, int*, float*, int*);
int dgtts2_(int*, int*, int*, double*, double*, double*, double*, int*, double*, int*);
int cgtts2_(int*, int*, int*, float*, float*, float*, float*, int*, float*, int*);
int zgtts2_(int*, int*, int*, double*, double*, double*, double*, int*, double*, int*);

//hbgst (banded red general to standard)
int chbgst_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, int*);
int zhbgst_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, int*);

//hbtrd (banded red to tridiag)
int chbtrd_(char*, char*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*);
int zhbtrd_(char*, char*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*);

//hecon (reciprocal condition number thorugh LDL)
int checon_(char*, int*, float*, int*, int*, float*, float*, float*, int*);
int zhecon_(char*, int*, double*, int*, int*, double*, double*, double*, int*);

//hegst (generalized to standard EIG)
int chegst_(int*, char*, int*, float*, int*, float*, int*, int*);
int zhegst_(int*, char*, int*, double*, int*, double*, int*, int*);

//herfs (improve lin sys)
int cherfs_(char*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zherfs_(char*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//herfsx (improve lin sys)
int cherfsx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, float*, int*);
int zherfsx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, double*, int*);

//hetrd (standard to tridiag EIG)
int chetrd_(char*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int zhetrd_(char*, int*, double*, int*, double*, double*, double*, double*, int*, int*);

//hetrf (LDL)
int chetrf_(char*, int*, float*, int*, int*, float*, int*, int*);
int zhetrf_(char*, int*, double*, int*, int*, double*, int*, int*);

//hetri (inv by LDL)
int chetri_(char*, int*, float*, int*, int*, float*, int*);
int zhetri_(char*, int*, double*, int*, int*, double*, int*);

//hetrs (lin sys by LDL)
int chetrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int zhetrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);

//hfrk (herk in RPF format)
int chfrk_(char*, char*, char*, int*, int*, float*, float*, int*, float*, float*);
int zhfrk_(char*, char*, char*, int*, int*, double*, double*, int*, double*, double*);

//hgeqz (gen EIG by shifted QZ)
int shgeqz_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, float*, int*, float*, int*, int*);
int dhgeqz_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, double*, int*, double*, int*, int*);
int chgeqz_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int zhgeqz_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);

//hpcon (packed reciprocal condition by LDL)
int chpcon_(char*, int*, float*, int*, float*, float*, float*, int*);
int zhpcon_(char*, int*, double*, int*, double*, double*, double*, int*);

//hpgst (packed generalized to standard EIG)
int chpgst_(int*, char*, int*, float*, float*, int*);
int zhpgst_(int*, char*, int*, double*, double*, int*);

//hprfs (packed improve lin sys)
int chprfs_(char*, int*, int*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zhprfs_(char*, int*, int*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//hptrd (packed standard to tridag EIG
int chptrd_(char*, int*, float*, float*, float*, float*, int*);
int zhptrd_(char*, int*, double*, double*, double*, double*, int*);

//hptrf (packed LDL)
int chptrf_(char*, int*, float*, int*, int*);
int zhptrf_(char*, int*, double*, int*, int*);

//hptri (packed inv by LDL)
int chptri_(char*, int*, float*, int*, float*, int*);
int zhptri_(char*, int*, double*, int*, double*, int*);

//hptrs (packed lin sys by LDL)
int chptrs_(char*, int*, int*, float*, int*, float*, int*, int*);
int zhptrs_(char*, int*, int*, double*, int*, double*, int*, int*);

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

//opgtr (packed Q from reflectors)
int sopgtr_(char*, int*, float*, float*, float*, int*, float*, int*);
int dopgtr_(char*, int*, double*, double*, double*, int*, double*, int*);

//opmtr (C*Q matrix overwrit)
int sopmtr_(char*, char*, char*, int*, int*, float*, float*, float*, int*, float*, int*);
int dopmtr_(char*, char*, char*, int*, int*, double*, double*, double*, int*, double*, int*);

//orbdb (bidiagonalization) MISSING

//orcsd (CS decomposition) MISSING

//orgbr (bidiagonalization)
int sorgbr_(char*, int*, int*, int*, float*, int*, float*, float*, int*, int*);
int dorgbr_(char*, int*, int*, int*, double*, int*, double*, double*, int*, int*);

//orghr (Q from reflectors)
int sorghr_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int dorghr_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//orgl2 (Q from reflectors) UNBLOCKED?
int sorgl2_(int*, int*, int*, float*, int*, float*, float*, int*);
int dorgl2_(int*, int*, int*, double*, int*, double*, double*, int*);

//orglq (Q from reflectors)
int sorglq_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int dorglq_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//orgql (Q from reflectors)
int sorgql_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int dorgql_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//orgqr (Q from reflectors)
int sorgqr_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int dorgqr_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//orgrq (Q from reflectors)
int sorgrq_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int dorgrq_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//orgtr (Q from reflectors)
int sorgtr_(char*, int*, float*, int*, float*, float*, int*, int*);
int dorgtr_(char*, int*, double*, int*, double*, double*, int*, int*);

//ormbr (C*Q overwrite)
int sormbr_(char*, char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int dormbr_(char*, char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//ormhr (C*Q overwrite)
int sormhr_(char*, char*, int*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int dormhr_(char*, char*, int*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//ormlq (C*Q overwrite)
int sormlq_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int dormlq_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//ormql (C*Q overwrite)
int sormql_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int dormql_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//ormqr (C*Q overwrite)
int sormqr_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int dormqr_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//ormrq (C*Q overwrite)
int dormrq_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);
int sormrq_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);

//ormrz (C*Q overwrite)
int sormrz_(char*, char*, int*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int dormrz_(char*, char*, int*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//pbcon (reciprocal cond by chol)
int spbcon_(char*, int*, int*, float*, int*, float*, float*, float*, int*, int*);
int dpbcon_(char*, int*, int*, double*, int*, double*, double*, double*, int*, int*);
int cpbcon_(char*, int*, int*, float*, int*, float*, float*, float*, float*, int*);
int zpbcon_(char*, int*, int*, double*, int*, double*, double*, double*, double*, int*);

//pbequ (equiliprate cond)
int spbequ_(char*, int*, int*, float*, int*, float*, float*, float*, int*);
int dpbequ_(char*, int*, int*, double*, int*, double*, double*, double*, int*);
int cpbequ_(char*, int*, int*, float*, int*, float*, float*, float*, int*);
int zpbequ_(char*, int*, int*, double*, int*, double*, double*, double*, int*);

//pbrfs (banded improve lin sys)
int spbrfs_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dpbrfs_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int cpbrfs_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zpbrfs_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//pbstf (banded split chol)
int cpbstf_(char*, int*, int*, float*, int*, int*);
int dpbstf_(char*, int*, int*, double*, int*, int*);
int spbstf_(char*, int*, int*, float*, int*, int*);
int zpbstf_(char*, int*, int*, double*, int*, int*);

//pbtrf (banded chol)
int spbtrf_(char*, int*, int*, float*, int*, int*);
int dpbtrf_(char*, int*, int*, double*, int*, int*);
int cpbtrf_(char*, int*, int*, float*, int*, int*);
int zpbtrf_(char*, int*, int*, double*, int*, int*);

//pbtrs (banded lin sys by chol)
int spbtrs_(char*, int*, int*, int*, float*, int*, float*, int*, int*);
int dpbtrs_(char*, int*, int*, int*, double*, int*, double*, int*, int*);
int cpbtrs_(char*, int*, int*, int*, float*, int*, float*, int*, int*);
int zpbtrs_(char*, int*, int*, int*, double*, int*, double*, int*, int*);

//pftrf (chol)
int spftrf_(char*, char*, int*, float*, int*);
int dpftrf_(char*, char*, int*, double*, int*);
int cpftrf_(char*, char*, int*, float*, int*);
int zpftrf_(char*, char*, int*, double*, int*);

//pftri (inv by chol)
int spftri_(char*, char*, int*, float*, int*);
int dpftri_(char*, char*, int*, double*, int*);
int cpftri_(char*, char*, int*, float*, int*);
int zpftri_(char*, char*, int*, double*, int*);

//pftrs (lin sys by chol)
int spftrs_(char*, char*, int*, int*, float*, float*, int*, int*);
int dpftrs_(char*, char*, int*, int*, double*, double*, int*, int*);
int cpftrs_(char*, char*, int*, int*, float*, float*, int*, int*);
int zpftrs_(char*, char*, int*, int*, double*, double*, int*, int*);

//pocon (reciprocal cond by chol)
int spocon_(char*, int*, float*, int*, float*, float*, float*, int*, int*);
int dpocon_(char*, int*, double*, int*, double*, double*, double*, int*, int*);
int cpocon_(char*, int*, float*, int*, float*, float*, float*, float*, int*);
int zpocon_(char*, int*, double*, int*, double*, double*, double*, double*, int*);

//poequ (equilibrate)
int spoequ_(int*, float*, int*, float*, float*, float*, int*);
int dpoequ_(int*, double*, int*, double*, double*, double*, int*);
int cpoequ_(int*, float*, int*, float*, float*, float*, int*);
int zpoequ_(int*, double*, int*, double*, double*, double*, int*);

//poequb (equilibrate)
int spoequb_(int*, float*, int*, float*, float*, float*, int*);
int dpoequb_(int*, double*, int*, double*, double*, double*, int*);
int cpoequb_(int*, float*, int*, float*, float*, float*, int*);
int zpoequb_(int*, double*, int*, double*, double*, double*, int*);

//porfs (improve lin sys)
int sporfs_(char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dporfs_(char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int cporfs_(char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zporfs_(char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//porfsx (improve lin sys)
int sporfsx_(char*, char*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int dporfsx_(char*, char*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, int*, int*);
int cporfsx_(char*, char*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, float*, int*);
int zporfsx_(char*, char*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, double*, int*);

//potrf (chol)
int spotrf_(char*, int*, float*, int*, int*);
int dpotrf_(char*, int*, double*, int*, int*);
int cpotrf_(char*, int*, float*, int*, int*);
int zpotrf_(char*, int*, double*, int*, int*);

//potri (inv by chol)
int spotri_(char*, int*, float*, int*, int*);
int dpotri_(char*, int*, double*, int*, int*);
int cpotri_(char*, int*, float*, int*, int*);
int zpotri_(char*, int*, double*, int*, int*);

//potrs (lin sys by chol)
int spotrs_(char*, int*, int*, float*, int*, float*, int*, int*);
int dpotrs_(char*, int*, int*, double*, int*, double*, int*, int*);
int cpotrs_(char*, int*, int*, float*, int*, float*, int*, int*);
int zpotrs_(char*, int*, int*, double*, int*, double*, int*, int*);

//ppcon (packec reciprocal cond by chol)
int sppcon_(char*, int*, float*, float*, float*, float*, int*, int*);
int dppcon_(char*, int*, double*, double*, double*, double*, int*, int*);
int cppcon_(char*, int*, float*, float*, float*, float*, float*, int*);
int zppcon_(char*, int*, double*, double*, double*, double*, double*, int*);

//ppequ (packed equilibrate)
int sppequ_(char*, int*, float*, float*, float*, float*, int*);
int dppequ_(char*, int*, double*, double*, double*, double*, int*);
int cppequ_(char*, int*, float*, float*, float*, float*, int*);
int zppequ_(char*, int*, double*, double*, double*, double*, int*);

//pprfs (packed improve lin sys)
int spprfs_(char*, int*, int*, float*, float*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dpprfs_(char*, int*, int*, double*, double*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int cpprfs_(char*, int*, int*, float*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zpprfs_(char*, int*, int*, double*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//pptrf (packed chol)
int spptrf_(char*, int*, float*, int*);
int dpptrf_(char*, int*, double*, int*);
int cpptrf_(char*, int*, float*, int*);
int zpptrf_(char*, int*, double*, int*);

//pptri (packed inv by chol)
int spptri_(char*, int*, float*, int*);
int dpptri_(char*, int*, double*, int*);
int cpptri_(char*, int*, float*, int*);
int zpptri_(char*, int*, double*, int*);

//pptrs (packed lin sys by chol)
int spptrs_(char*, int*, int*, float*, float*, int*, int*);
int dpptrs_(char*, int*, int*, double*, double*, int*, int*);
int cpptrs_(char*, int*, int*, float*, float*, int*, int*);
int zpptrs_(char*, int*, int*, double*, double*, int*, int*);

//pstf2 (pivoting chol) UNBLOCKED?
int spstf2_(char*, int*, float*, int*, int*, int*, float*, float*, int*);
int dpstf2_(char*, int*, double*, int*, int*, int*, double*, double*, int*);
int cpstf2_(char*, int*, float*, int*, int*, int*, float*, float*, int*);
int zpstf2_(char*, int*, double*, int*, int*, int*, double*, double*, int*);

//pstrf (pivoting chol)
int spstrf_(char*, int*, float*, int*, int*, int*, float*, float*, int*);
int dpstrf_(char*, int*, double*, int*, int*, int*, double*, double*, int*);
int cpstrf_(char*, int*, float*, int*, int*, int*, float*, float*, int*);
int zpstrf_(char*, int*, double*, int*, int*, int*, double*, double*, int*);

//ptcon (tridiag reciprocal cond by LDL)
int sptcon_(int*, float*, float*, float*, float*, float*, int*);
int dptcon_(int*, double*, double*, double*, double*, double*, int*);
int cptcon_(int*, float*, float*, float*, float*, float*, int*);
int zptcon_(int*, double*, double*, double*, double*, double*, int*);

//pteqr (tridiag EIG)
int spteqr_(char*, int*, float*, float*, float*, int*, float*, int*);
int dpteqr_(char*, int*, double*, double*, double*, int*, double*, int*);
int cpteqr_(char*, int*, float*, float*, float*, int*, float*, int*);
int zpteqr_(char*, int*, double*, double*, double*, int*, double*, int*);

//ptrfs (tridiag improve lin sys)
int sptrfs_(int*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, float*, float*, int*);
int dptrfs_(int*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, double*, double*, int*);
int cptrfs_(char*, int*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zptrfs_(char*, int*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//pttrf (tridiag LDL)
int spttrf_(int*, float*, float*, int*);
int dpttrf_(int*, double*, double*, int*);
int cpttrf_(int*, float*, float*, int*);
int zpttrf_(int*, double*, double*, int*);

//pttrs (tridiag lin sys by LDL)
int spttrs_(int*, int*, float*, float*, float*, int*, int*);
int dpttrs_(int*, int*, double*, double*, double*, int*, int*);
int cpttrs_(char*, int*, int*, float*, float*, float*, int*, int*);
int zpttrs_(char*, int*, int*, double*, double*, double*, int*, int*);

//ptts2 (tridiag lin sys by LDL) UNBLOCKED?
int sptts2_(int*, int*, float*, float*, float*, int*);
int dptts2_(int*, int*, double*, double*, double*, int*);
int cptts2_(int*, int*, int*, float*, float*, float*, int*);
int zptts2_(int*, int*, int*, double*, double*, double*, int*);

//sbgst (red generalized to standard EIG)
int ssbgst_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*);
int dsbgst_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*);

//sbtrd (red standard to tridiag EIG)
int ssbtrd_(char*, char*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*);
int dsbtrd_(char*, char*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*);

//sfrk (syrk in REP)
int ssfrk_(char*, char*, char*, int*, int*, float*, float*, int*, float*, float*);
int dsfrk_(char*, char*, char*, int*, int*, double*, double*, int*, double*, double*);

//spcon (packed reciprocal cond by LDL)
int cspcon_(char*, int*, float*, int*, float*, float*, float*, int*);
int dspcon_(char*, int*, double*, int*, double*, double*, double*, int*, int*);
int sspcon_(char*, int*, float*, int*, float*, float*, float*, int*, int*);
int zspcon_(char*, int*, double*, int*, double*, double*, double*, int*);

//spgst (packed red generalized to standard EIG)
int sspgst_(int*, char*, int*, float*, float*, int*);
int dspgst_(int*, char*, int*, double*, double*, int*);

//sprfs (packed improve lin sys)
int ssprfs_(char*, int*, int*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dsprfs_(char*, int*, int*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int csprfs_(char*, int*, int*, float*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zsprfs_(char*, int*, int*, double*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//sptrd (packed red standard to tridiag EIG)
int ssptrd_(char*, int*, float*, float*, float*, float*, int*);
int dsptrd_(char*, int*, double*, double*, double*, double*, int*);

//sptrf (packed LDL)
int ssptrf_(char*, int*, float*, int*, int*);
int dsptrf_(char*, int*, double*, int*, int*);
int csptrf_(char*, int*, float*, int*, int*);
int zsptrf_(char*, int*, double*, int*, int*);

//sptri (packed inv b LDL)
int ssptri_(char*, int*, float*, int*, float*, int*);
int dsptri_(char*, int*, double*, int*, double*, int*);
int csptri_(char*, int*, float*, int*, float*, int*);
int zsptri_(char*, int*, double*, int*, double*, int*);

//sptrs (packed lin sys by LDL)
int ssptrs_(char*, int*, int*, float*, int*, float*, int*, int*);
int dsptrs_(char*, int*, int*, double*, int*, double*, int*, int*);
int csptrs_(char*, int*, int*, float*, int*, float*, int*, int*);
int zsptrs_(char*, int*, int*, double*, int*, double*, int*, int*);

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

//sycon (reiprocal cond by LDL)
int ssycon_(char*, int*, float*, int*, int*, float*, float*, float*, int*, int*);
int dsycon_(char*, int*, double*, int*, int*, double*, double*, double*, int*, int*);
int csycon_(char*, int*, float*, int*, int*, float*, float*, float*, int*);
int zsycon_(char*, int*, double*, int*, int*, double*, double*, double*, int*);

//syequb (equilibrate)
int ssyequb_(char*, int*, float*, int*, float*, float*, float*, float*, int*);
int dsyequb_(char*, int*, double*, int*, double*, double*, double*, double*, int*);
int csyequb_(char*, int*, float*, int*, float*, float*, float*, float*, int*);
int zsyequb_(char*, int*, double*, int*, double*, double*, double*, double*, int*);

//sygst (red gernatalized to standard EIG)
int ssygst_(int*, char*, int*, float*, int*, float*, int*, int*);
int dsygst_(int*, char*, int*, double*, int*, double*, int*, int*);

//syrfs (improve lin sys)
int ssyrfs_(char*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dsyrfs_(char*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int csyrfs_(char*, int*, int*, float*, int*, float*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int zsyrfs_(char*, int*, int*, double*, int*, double*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//syrfsx (improve lin sys)
int ssyrfsx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, int*, int*);
int dsyrfsx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, int*, int*);
int csyrfsx_(char*, char*, int*, int*, float*, int*, float*, int*, int*, float*, float*, int*, float*, int*, float*, float*, int*, float*, float*, int*, float*, float*, float*, int*);
int zsyrfsx_(char*, char*, int*, int*, double*, int*, double*, int*, int*, double*, double*, int*, double*, int*, double*, double*, int*, double*, double*, int*, double*, double*, double*, int*);

//sytrd (red standard to tridiag EIG) 
int ssytrd_(char*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dsytrd_(char*, int*, double*, int*, double*, double*, double*, double*, int*, int*);

//sytrf (LDL)
int ssytrf_(char*, int*, float*, int*, int*, float*, int*, int*);
int dsytrf_(char*, int*, double*, int*, int*, double*, int*, int*);
int csytrf_(char*, int*, float*, int*, int*, float*, int*, int*);
int zsytrf_(char*, int*, double*, int*, int*, double*, int*, int*);

//sytri (inv by LDL)
int ssytri_(char*, int*, float*, int*, int*, float*, int*);
int dsytri_(char*, int*, double*, int*, int*, double*, int*);
int csytri_(char*, int*, float*, int*, int*, float*, int*);
int zsytri_(char*, int*, double*, int*, int*, double*, int*);

//sytrs (lin sys by LDL
int ssytrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int dsytrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);
int csytrs_(char*, int*, int*, float*, int*, int*, float*, int*, int*);
int zsytrs_(char*, int*, int*, double*, int*, int*, double*, int*, int*);

//tbcon (banded reciprocal cond)
int stbcon_(char*, char*, char*, int*, int*, float*, int*, float*, float*, int*, int*);
int dtbcon_(char*, char*, char*, int*, int*, double*, int*, double*, double*, int*, int*);
int ctbcon_(char*, char*, char*, int*, int*, float*, int*, float*, float*, float*, int*);
int ztbcon_(char*, char*, char*, int*, int*, double*, int*, double*, double*, double*, int*);

//tbrfs (banded bounds for lin sys)
int stbrfs_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dtbrfs_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int ctbrfs_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int ztbrfs_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//tbtrs (banded lin sys)
int stbtrs_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, int*);
int dtbtrs_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, int*);
int ctbtrs_(char*, char*, char*, int*, int*, int*, float*, int*, float*, int*, int*);
int ztbtrs_(char*, char*, char*, int*, int*, int*, double*, int*, double*, int*, int*);

//tfsm (trsm in RFP)
int stfsm_(char*, char*, char*, char*, char*, int*, int*, float*, float*, float*, int*);
int dtfsm_(char*, char*, char*, char*, char*, int*, int*, double*, double*, double*, int*);
int ctfsm_(char*, char*, char*, char*, char*, int*, int*, float*, float*, float*, int*);
int ztfsm_(char*, char*, char*, char*, char*, int*, int*, double*, double*, double*, int*);

//tftri (inv in RFP)
int stftri_(char*, char*, char*, int*, float*, int*);
int dtftri_(char*, char*, char*, int*, double*, int*);
int ctftri_(char*, char*, char*, int*, float*, int*);
int ztftri_(char*, char*, char*, int*, double*, int*);

//tfttp (triangular copy TF to TP)
int stfttp_(char*, char*, int*, float*, float*, int*);
int dtfttp_(char*, char*, int*, double*, double*, int*);
int ctfttp_(char*, char*, int*, float*, float*, int*);
int ztfttp_(char*, char*, int*, double*, double*, int*);

//tfttr (triangular copy TF to TR)
int stfttr_(char*, char*, int*, float*, float*, int*, int*);
int dtfttr_(char*, char*, int*, double*, double*, int*, int*);
int ctfttr_(char*, char*, int*, float*, float*, int*, int*);
int ztfttr_(char*, char*, int*, double*, double*, int*, int*);

//tgevc (gen EIG)
int stgevc_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*, int*, float*, int*);
int dtgevc_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*, int*, double*, int*);
int ctgevc_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*, int*, float*, float*, int*);
int ztgevc_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*, int*, double*, double*, int*);

//tgexc (Schur reordering)
int stgexc_(int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*, int*, float*, int*, int*);
int dtgexc_(int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*, int*, double*, int*, int*);
int ctgexc_(int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*, int*, int*);
int ztgexc_(int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*, int*, int*);

//tgsen (Schur reordering)
int stgsen_(int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*, float*, int*, int*, float*, float*, float*, float*, int*, int*, int*, int*);
int dtgsen_(int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*, double*, int*, int*, double*, double*, double*, double*, int*, int*, int*, int*);
int ctgsen_(int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, int*, float*, int*, int*, float*, float*, float*, float*, int*, int*, int*, int*);
int ztgsen_(int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, int*, double*, int*, int*, double*, double*, double*, double*, int*, int*, int*, int*);

//tgsja (GSVD)
int stgsja_(char*, char*, char*, int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dtgsja_(char*, char*, char*, int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);
int ctgsja_(char*, char*, char*, int*, int*, int*, int*, int*, float*, int*, float*, int*, float*, float*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int ztgsja_(char*, char*, char*, int*, int*, int*, int*, int*, double*, int*, double*, int*, double*, double*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//tgsna (reciprocal cond for EIG)
int stgsna_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, int*, int*);
int dtgsna_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, int*, int*);
int ctgsna_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, int*, int*);
int ztgsna_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, int*, int*);

//tgsyl (generalized sylv)
int stgsyl_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*, int*);
int dtgsyl_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*, int*);
int ctgsyl_(char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*, int*);
int ztgsyl_(char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*, int*);

//tpcon (packed reciprocal cond)
int stpcon_(char*, char*, char*, int*, float*, float*, float*, int*, int*);
int dtpcon_(char*, char*, char*, int*, double*, double*, double*, int*, int*);
int ctpcon_(char*, char*, char*, int*, float*, float*, float*, float*, int*);
int ztpcon_(char*, char*, char*, int*, double*, double*, double*, double*, int*);

//tpmqrt (apply Q to blocked C) MISSING
//tpqrt (pentagonal QR) MISSING

//tprfs (bounds for lin sys)
int stprfs_(char*, char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dtprfs_(char*, char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int ctprfs_(char*, char*, char*, int*, int*, float*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int ztprfs_(char*, char*, char*, int*, int*, double*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//tptri (packed inv)
int ctptri_(char*, char*, int*, float*, int*);
int dtptri_(char*, char*, int*, double*, int*);
int stptri_(char*, char*, int*, float*, int*);
int ztptri_(char*, char*, int*, double*, int*);

//tptrs (packed lin sys)
int stptrs_(char*, char*, char*, int*, int*, float*, float*, int*, int*);
int dtptrs_(char*, char*, char*, int*, int*, double*, double*, int*, int*);
int ctptrs_(char*, char*, char*, int*, int*, float*, float*, int*, int*);
int ztptrs_(char*, char*, char*, int*, int*, double*, double*, int*, int*);

//tpttf (copy TP to TF)
int stpttf_(char*, char*, int*, float*, float*, int*);
int dtpttf_(char*, char*, int*, double*, double*, int*);
int ctpttf_(char*, char*, int*, float*, float*, int*);
int ztpttf_(char*, char*, int*, double*, double*, int*);

//tpttr (copy TP to TR)
int stpttr_(char*, int*, float*, float*, int*, int*);
int dtpttr_(char*, int*, double*, double*, int*, int*);
int ctpttr_(char*, int*, float*, float*, int*, int*);
int ztpttr_(char*, int*, double*, double*, int*, int*);

//trcon (reciprocal cond)
int strcon_(char*, char*, char*, int*, float*, int*, float*, float*, int*, int*);
int dtrcon_(char*, char*, char*, int*, double*, int*, double*, double*, int*, int*);
int ctrcon_(char*, char*, char*, int*, float*, int*, float*, float*, float*, int*);
int ztrcon_(char*, char*, char*, int*, double*, int*, double*, double*, double*, int*);

//trevc (EIG)
int ctrevc_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, int*, int*, float*, float*, int*);
int dtrevc_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, int*, int*, double*, int*);
int strevc_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, int*, int*, float*, int*);
int ztrevc_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, int*, int*, double*, double*, int*);

//trexc (Schur reordering)
int strexc_(char*, int*, float*, int*, float*, int*, int*, int*, float*, int*);
int dtrexc_(char*, int*, double*, int*, double*, int*, int*, int*, double*, int*);
int ctrexc_(char*, int*, float*, int*, float*, int*, int*, int*, int*);
int ztrexc_(char*, int*, double*, int*, double*, int*, int*, int*, int*);

//trrfs (bounds for lin sys)
int strrfs_(char*, char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int dtrrfs_(char*, char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);
int ctrrfs_(char*, char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, float*, int*);
int ztrrfs_(char*, char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, double*, int*);

//trsen (Schur reordering)
int strsen_(char*, char*, int*, int*, float*, int*, float*, int*, float*, float*, int*, float*, float*, float*, int*, int*, int*, int*);
int dtrsen_(char*, char*, int*, int*, double*, int*, double*, int*, double*, double*, int*, double*, double*, double*, int*, int*, int*, int*);
int ctrsen_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, float*, int*, int*);
int ztrsen_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, double*, int*, int*);

//trsna (reciprocal cond for EIG)
int strsna_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, int*, int*);
int dtrsna_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, int*, int*);
int ctrsna_(char*, char*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, int*, int*, float*, int*, float*, int*);
int ztrsna_(char*, char*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, int*, int*, double*, int*, double*, int*);

//trsyl (sylv)
int strsyl_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*);
int dtrsyl_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*);
int ctrsyl_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*);
int ztrsyl_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*);

//trtri (inv)
int strtri_(char*, char*, int*, float*, int*, int*);
int dtrtri_(char*, char*, int*, double*, int*, int*);
int ctrtri_(char*, char*, int*, float*, int*, int*);
int ztrtri_(char*, char*, int*, double*, int*, int*);

//trtrs (lin sys)
int strtrs_(char*, char*, char*, int*, int*, float*, int*, float*, int*, int*);
int dtrtrs_(char*, char*, char*, int*, int*, double*, int*, double*, int*, int*);
int ctrtrs_(char*, char*, char*, int*, int*, float*, int*, float*, int*, int*);
int ztrtrs_(char*, char*, char*, int*, int*, double*, int*, double*, int*, int*);

//trttf (copy TR to TF)
int strttf_(char*, char*, int*, float*, int*, float*, int*);
int dtrttf_(char*, char*, int*, double*, int*, double*, int*);
int ctrttf_(char*, char*, int*, float*, int*, float*, int*);
int ztrttf_(char*, char*, int*, double*, int*, double*, int*);

//trttp (copy TR to TP)
int strttp_(char*, int*, float*, int*, float*, int*);
int dtrttp_(char*, int*, double*, int*, double*, int*);
int ctrttp_(char*, int*, float*, int*, float*, int*);
int ztrttp_(char*, int*, double*, int*, double*, int*);

//tzrqf (red trapezoidal to triangular)
int stzrqf_(int*, int*, float*, int*, float*, int*);
int dtzrqf_(int*, int*, double*, int*, double*, int*);
int ctzrqf_(int*, int*, float*, int*, float*, int*);
int ztzrqf_(int*, int*, double*, int*, double*, int*);

//tzrzf (red trapezoidal to triangular)
int stzrzf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dtzrzf_(int*, int*, double*, int*, double*, double*, int*, int*);
int ctzrzf_(int*, int*, float*, int*, float*, float*, int*, int*);
int ztzrzf_(int*, int*, double*, int*, double*, double*, int*, int*);

//ung2r (Q from reflectors) UNBOCKED?
int cung2r_(int*, int*, int*, float*, int*, float*, float*, int*);
int zung2r_(int*, int*, int*, double*, int*, double*, double*, int*);

//ungbr (Q from reflectors)
int cungbr_(char*, int*, int*, int*, float*, int*, float*, float*, int*, int*);
int zungbr_(char*, int*, int*, int*, double*, int*, double*, double*, int*, int*);

//unghr (Q from reflectors)
int zunghr_(int*, int*, int*, double*, int*, double*, double*, int*, int*);
int cunghr_(int*, int*, int*, float*, int*, float*, float*, int*, int*);

//unglq (Q from reflectors)
int cunglq_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int zunglq_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//ungql (Q from reflectors)
int cungql_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int zungql_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//ungqr (Q from reflectors)
int cungqr_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int zungqr_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//ungrq (Q from reflectors)
int cungrq_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int zungrq_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//ungtr (Q from reflectors)
int cungtr_(char*, int*, float*, int*, float*, float*, int*, int*);
int zungtr_(char*, int*, double*, int*, double*, double*, int*, int*);

//unmbr (C * Q overwrite)
int cunmbr_(char*, char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zunmbr_(char*, char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//unmhr (C * Q overwrite)
int cunmhr_(char*, char*, int*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zunmhr_(char*, char*, int*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//unmlq (C * Q overwrite)
int cunmlq_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zunmlq_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//unmql (C * Q overwrite)
int cunmql_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zunmql_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//unmqr (C * Q overwrite)
int cunmqr_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zunmqr_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//unmrq (C * Q overwrite)
int cunmrq_(char*, char*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zunmrq_(char*, char*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//unmrz (C * Q overwrite)
int cunmrz_(char*, char*, int*, int*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zunmrz_(char*, char*, int*, int*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//unmtr (C * Q overwrite)
int cunmtr_(char*, char*, char*, int*, int*, float*, int*, float*, float*, int*, float*, int*, int*);
int zunmtr_(char*, char*, char*, int*, int*, double*, int*, double*, double*, int*, double*, int*, int*);

//upgtr (Q from reflectors)
int cupgtr_(char*, int*, float*, float*, float*, int*, float*, int*);
int zupgtr_(char*, int*, double*, double*, double*, int*, double*, int*);

//upmtr (C * Q overwrite)
int cupmtr_(char*, char*, char*, int*, int*, float*, float*, float*, int*, float*, int*);
int zupmtr_(char*, char*, char*, int*, int*, double*, double*, double*, int*, double*, int*);

#endif /* LAPACK_COMPUTATIONAL_H */
