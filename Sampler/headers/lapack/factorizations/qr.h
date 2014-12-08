#ifndef LAPACK_FACTORIZATION_QR_H
#define LAPACK_FACTORIZATION_QR_H

////////////////////////////////////////////////////////////////////////////////
// QR, RQ, QL, LQ
////////////////////////////////////////////////////////////////////////////////

//gelqf (LQ)
int sgelqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgelqf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgelqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgelqf_(int*, int*, double*, int*, double*, double*, int*, int*);

//geqlf (QL)
int sgeqlf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgeqlf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqlf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgeqlf_(int*, int*, double*, int*, double*, double*, int*, int*);

//geqp3 (QR)
int sgeqp3_(int*, int*, float*, int*, int*, float*, float*, int*, int*);
int dgeqp3_(int*, int*, double*, int*, int*, double*, double*, int*, int*);
int cgeqp3_(int*, int*, float*, int*, int*, float*, float*, int*, float*, int*);
int zgeqp3_(int*, int*, double*, int*, int*, double*, double*, int*, double*, int*);

//geqpf (QR)
int cgeqpf_(int*, int*, float*, int*, int*, float*, float*, float*, int*);
int dgeqpf_(int*, int*, double*, int*, int*, double*, double*, int*);
int sgeqpf_(int*, int*, float*, int*, int*, float*, float*, int*);
int zgeqpf_(int*, int*, double*, int*, int*, double*, double*, double*, int*);

//geqrf (QR)
int sgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgeqrf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgeqrf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgeqrf_(int*, int*, float*, int*, float*, float*, int*, int*);

//geqrt  (QR by WY repr.) MISSING
//geqrt2 (QR by WY repr.) MISSING
//geqrt3 (QR by WY repr.) MISSING

//gerqf (RQ)
int sgerqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int dgerqf_(int*, int*, double*, int*, double*, double*, int*, int*);
int cgerqf_(int*, int*, float*, int*, float*, float*, int*, int*);
int zgerqf_(int*, int*, double*, int*, double*, double*, int*, int*);

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

#endif /* LAPACK_FACTORIZATION_QR_H */
