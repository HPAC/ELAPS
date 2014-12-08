#ifndef LAPACK_REDUCTIONS_H
#define LAPACK_REDUCTIONS_H

////////////////////////////////////////////////////////////////////////////////
// reductions
////////////////////////////////////////////////////////////////////////////////


//gbbrd (banded red. to bidiagonal, orthogonal trans.)
int sgbbrd_(char*, int*, int*, int*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, int*);
int dgbbrd_(char*, int*, int*, int*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, int*);
int cgbbrd_(char*, int*, int*, int*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*, float*, int*, float*, float*, int*);
int zgbbrd_(char*, int*, int*, int*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*, double*, int*, double*, double*, int*);

//gebrd (red. to bidiagonal, orthogonal trans.)
int sgebrd_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*, int*);
int dgebrd_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*, int*);
int cgebrd_(int*, int*, float*, int*, float*, float*, float*, float*, float*, int*, int*);
int zgebrd_(int*, int*, double*, int*, double*, double*, double*, double*, double*, int*, int*);

//gehrd (red. to Hessenberg)
int sgehrd_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int dgehrd_(int*, int*, int*, double*, int*, double*, double*, int*, int*);
int cgehrd_(int*, int*, int*, float*, int*, float*, float*, int*, int*);
int zgehrd_(int*, int*, int*, double*, int*, double*, double*, int*, int*);

//gghrd (red. to U Hessenberg, orthogonal trans.)
int sgghrd_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int dgghrd_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*);
int cgghrd_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*, int*);
int zgghrd_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*, int*);

//hbgst (banded red general to standard)
int chbgst_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, float*, int*);
int zhbgst_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, double*, int*);

//hbtrd (banded red to tridiag)
int chbtrd_(char*, char*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*);
int zhbtrd_(char*, char*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*);

//sbgst (red generalized to standard EIG)
int ssbgst_(char*, char*, int*, int*, int*, float*, int*, float*, int*, float*, int*, float*, int*);
int dsbgst_(char*, char*, int*, int*, int*, double*, int*, double*, int*, double*, int*, double*, int*);

//sbtrd (red standard to tridiag EIG)
int ssbtrd_(char*, char*, int*, int*, float*, int*, float*, float*, float*, int*, float*, int*);
int dsbtrd_(char*, char*, int*, int*, double*, int*, double*, double*, double*, int*, double*, int*);

//spgst (packed red generalized to standard EIG)
int sspgst_(int*, char*, int*, float*, float*, int*);
int dspgst_(int*, char*, int*, double*, double*, int*);

//sptrd (packed red standard to tridiag EIG)
int ssptrd_(char*, int*, float*, float*, float*, float*, int*);
int dsptrd_(char*, int*, double*, double*, double*, double*, int*);

//sygst (red gernatalized to standard EIG)
int ssygst_(int*, char*, int*, float*, int*, float*, int*, int*);
int dsygst_(int*, char*, int*, double*, int*, double*, int*, int*);

//sytrd (red standard to tridiag EIG) 
int ssytrd_(char*, int*, float*, int*, float*, float*, float*, float*, int*, int*);
int dsytrd_(char*, int*, double*, int*, double*, double*, double*, double*, int*, int*);

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

#endif /* LAPACK_REDUCTIONS_H */
