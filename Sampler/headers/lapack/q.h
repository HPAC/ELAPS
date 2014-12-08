#ifndef LAPACK_Q_H
#define LAPACK_Q_H

////////////////////////////////////////////////////////////////////////////////
// Computational routines (found by hand)
////////////////////////////////////////////////////////////////////////////////

//opgtr (packed Q from reflectors)
int sopgtr_(char*, int*, float*, float*, float*, int*, float*, int*);
int dopgtr_(char*, int*, double*, double*, double*, int*, double*, int*);

//opmtr (C*Q matrix overwrit)
int sopmtr_(char*, char*, char*, int*, int*, float*, float*, float*, int*, float*, int*);
int dopmtr_(char*, char*, char*, int*, int*, double*, double*, double*, int*, double*, int*);

//orbdb (bidiagonalization) MISSING

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

//tpmqrt (apply Q to blocked C) MISSING

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

#endif /* LAPACK_Q_H */
