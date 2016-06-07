ELAPS Utility kernel routines
=============================

ELAPS provides a series of utility routines for experiment setups such as matrix
randomization and file-IO.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Constant matrix initialization (`memset`)](#constant-matrix-initialization-memset)
- [General matrix randomization (`gerand`)](#general-matrix-randomization-gerand)
- [Hermitian positive definite matrix randomization (`porand`)](#hermitian-positive-definite-matrix-randomization-porand)
- [File input and output (`readfile` and `writefile`)](#file-input-and-output-readfile-and-writefile)
  - [File input (`readfile`)](#file-input-readfile)
  - [File output (`rwritefile`)](#file-output-rwritefile)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


Constant matrix initialization (`memset`)
-----------------------------------------
The routines `imemset`, `smemset`, `dmemset`, `cmemset` and `zmemset` with the
signature `xmemset(m, n, alpha, A, ldA)` fill all entries of the matrix `A` of
size `m` x `n` and leading dimension `ldA` with the constant value `alpha`.


General matrix randomization (`gerand`)
---------------------------------------
The routines `igerand`, `sgerand`, `dgerand`, `cgerand`, and `zgerand` with the
signature `xgerand(m, n, A, ldA)` fill all entries of matrix `A` of size `m` x
`n` and leading dimension `ldA` with random numbers.  The integer version uses
numbers between 0 and `RAND_MAX`-1, while the other routines choose random
floating point numbers between 0 and 1 (in the complex case for both the real
and imaginary part.


Hermitian positive definite matrix randomization (`porand`)
-----------------------------------------------------------
The routines `sporand`, `sporand`, `cporand`, and `zporand` with the signature
`xporand(uplo, n, A, ldA)` fill the lower (`uplo = L`) or upper (`uplo = U`)
part of the matrix `A` of size `n` x `n` and leading dimension `ldA` with random
numbers, such that the resulting matrix is symmetric/hermitian positive definite
(SPD/HPD).  This is achieved by filling the specified half of the matrix with
random numbers between 0 and 1, and then adding `n` to the (real) diagonal.


File input and output (`readfile` and `writefile`)
--------------------------------------------------

### File input (`readfile`)
The routines `readfile` (in bytes), `ireadfile`, `sreadfile`, `dreadfile`,
`creadfile` and `zreadfile` with the signature `xreadfile(filename, m, n, A,
ldA, info)` fill the matrix `A` of size `m` x `n` and leading dimension `ldA`
with the contents of `filename`.  Upon success, the return value `info` is 0, if
the file was not found it is -1, and a positive value n indicates an error
reading the n-th element from the file.

### File output (`rwritefile`)
The routines `writefile` (in bytes), `iwritefile`, `swritefile`, `dwritefile`,
`cwritefile` and `zwritefile` with the signature `xwritefile(filename, m, n, A,
ldA, info)` writes the matrix `A` of size `m` x `n` and leading dimension `ldA`
to `filename`.  Upon success, the return value `info` is 0, if the file could
not be opened it is -1, and a positive value n indicates an error writing the
n-th element from the file.
