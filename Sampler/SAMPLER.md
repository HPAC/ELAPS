Usage of ELAPS:Samplers
=======================

This file details the interactive usage of Samplers, i.e. how the Sampler
treats its stdin.

The Sampler's stdin is read line by line.  Hash (`#`) is the comment character:
anything following a `#` is ignored.  Empty lines are also ignored.
Each line is tokenized (split by white spaces); the first token determines the
meaning of that line.  This token can be either a kernel name or a special
command.
(If a kernel has the same name as a command, the command shadows the kernel.)

### `go`
`go` executes all pending calls and prints their performance measurements to
stdout.  If there are calls pending at the end of stdin, `go` is implicitly
issued.
It expects no arguments.


Kernel Call Syntax
------------------
If the first token identifies a kernel, a corresponding call is added to the
list of pending calls.  The remaining tokens in that line are parsed as its
arguments. E.g.

```
dgemm_ N N 1000 1000 1000 1.0 [1000000] 1000 [1000000] 1000 1.0 [1000000] 1000
```

How the arguments are treated depends on their (pointer) type:

* `char *` expects any string, that is stored and passed to the kernel as a
  pointer to its first character.  Strings cannot contain white spaces.
* Any numeric argument type (`int *`, `float *`, and `double *`) expects any of
  the following formats:
  * A number in the corresponding format (e.g., 1000 for `int *`, `3.5e-6` for
    `float *` or `double *`) is passed as a scalar by refernce.
  * A comma separated list of such numbers (e.g., `2,3` to represent the
    complex number *2 + 3i*) is stored in an array and passed as a pointer to
    its first element.  (No whitespaces around the commas!)
  * A count enclosed by brackets (e.g., `[1000000]`) will pass a memory region
    of such many elements of the expected type.  Arguments of this
    format in the same call will point to disjoint regions; subsequent calls
    reuse the same memory regions for their such formatted arguemnts.
  * A variable name passes a pointer to the memory associated with the variable
    (see "Using variables" below")
    

Using Variables
---------------
Variables identify designated memory regions.  Variable names must be strings
beginning with a letter (e.g. "`A`", "`a_1234`").  Variables are prepared and
modified through the following commands:

### `*malloc`
`malloc` (or `[isdcz]malloc`) allocates a variable and initializes it with
random data (between 0 and 1 for floating point types).
It expects two arguments:

* The name of the variable.
* The size of the corresponding memory region.  Which `[sdczi]malloc` is used
  determines the units of this size:
  * `malloc`: bytes
  * `imalloc`: `int`s
  * `cmalloc`: `floats`s
  * `dmalloc`: `doubles`s
  * `cmalloc`: `float`s x 2 (complex float)
  * `zmalloc`: `doubles`s x 2 (complex double)

### `*offset`
`offset` (of `[isdcz]offset`) computes an offset into a variables memory region
resulting in a new variable.
It expects three arguments:

* The name of the base variable from which the offset is computed.
* The offset into the memory region.  As for `*malloc`, The prefix of `offset`
  determines how this offset size is interpreted.  The datatypes used for the
  `malloc` of the base variable and the `offset` need not coincide. 
  There are no bound checks and negative offsets are allowed!
* The name of the target variable which points to the offset memory region.

### `free`
`free` deletes a variable.  If the variable was created by `*malloc`, its memory
region is freed.  All variables derived from the deleted variable are also
deleted.  
It expects one argument:

* The name of the variable.

`free` takes affect *immediately*!  Registered but not yet executed calls
referencing a freed variable will be discarded when the execution of calls is
initiated.
There is no need to free variables before the end of stdin;  `free` only exists
to allow to associate a previously used variable name with a different memory
region!


PAPI
----

### `set_counters`
`set_counters` sets the desired PAPI counters.  Invoked without further
arguments, it disables the use of PAPI.  Invoked with arguments, each argument
is parsed as a PAPI counter name.

`set_counters` takes affect *immediately*!  This means once the execution of
calls is initiated, the most recently set counters are used for `all` calls.


Parallel Regions
----------------
Calls can be executed in parallel as OpenMP tasks by enclosing them in `{omp`
and `}`; each on its own line.

### `{omp`
`{omp` marks the beginning of parallel region.
It expects no arguments.

### `}`
`}` marks the end of a parallel region.
If a parallel region is still open when the execution of calls is initiated, it
is implicitly closed.
It expects no arguments.


Utility 
-------

### `info`
`info` prints the signature of a kernel to stderr.
It expects 1 argument:

* Name of the kernel

### `date`
`date` prints the current Unix time in seconds to stdout.
It expects no arguments.

`date` takes affect *immediately*!  If not preceded by a `go` it will print the
time before executing the calls.

### `print`
`print` prints all its arguments to stdout as strings.

`print` takes affect *immediately*!  To interlace measurement output with
comments through print, you need to execute `go` first.
