ELAPS Sampler
=============

At the core of the ELAPS framework is a low-level performance measurement tool
tailored to dense linear algebra operations: the Sampler.  This tool makes it
possible to measure the performance of individual kernel executions,
implementing this work-flow:
- Read from `stdin` a list of *calls*, i.e., kernel names with corresponding
  lists of arguments;
- execute the specified calls, thereby measuring their performance in terms of
  CPU cycles, and optionally through performance counters provided by PAPI;
- print the measured performance numbers to the standard output.


Compilation
-----------

In the `Sampler/` folder, invoke `make.sh` with a configuration file to
construct a specialized Sampler in `Sampler/buid/*/sampler.x`, where `*` is the
Sampler's name.  The configurations files, typically collected in
`Sampler/cfgs/`, are bash scripts that define a series of configuration
parameters.  `Sampler/cfgs/examples/template.cfg` contains a detailed
description of these parameters and their effects.  Many of these configuration
parameters can be detected automatically by running `Sampler/gathercfg.sh` on
the target system.


Usage
-----

The Sampler main loop reads `stdin` line by line.  Thereby discarding anything
following the comment character `#` and empty lines.  The lines are tokenized
(separated by white spaces) and treated according to the first token:  While
special commands invoke Sampler functions (see below); all other lines are
parsed as sampling calls.

Example:

    ./sampler.x <<END
    dgemm N N 1000 1000 1000 1.0 [1000000] 1000 [1000000] 1000 1.0 [1000000] 1000
    dtrsm L L N U 1000 1000 1.0 [1000000] 1000 [1000000] 1000
    END
    133590440
    76830416


### Sampling call syntax
A call is specified by a kernel name followed by arguments to this kernel
separated by spaces.  How the arguments are treated depends on their (pointer)
type:
- `char *` arguments expect strings that is stored and passed to the kernel as a
  pointer to its first character.  Strings cannot contain white spaces.
- Numeric arguments (`int *`, `float *`, and `double *`) expect any of the
  following formats:
  - A number in the corresponding format (e.g., `1000` for `int *`, or `3.5e-6`
    for `float *` or `double *`) is passed as a scalar by refernce.
  - A comma separated list of such numbers (e.g., `2,3` to represent the
    complex number *2 + 3i*) is stored in an array and passed as a pointer to
    its first element.
  - A count enclosed by brackets (e.g., `[1000000]`) will pass a buffer of such
    many elements of the expected type.  Arguments of this format are disjoint
    within the same call (no aliasing) but subsequent calls will reuese the same
    or overlapping buffers.
  - A variable name passes a pointer to the memory associated with the variable
    (see "Named Buffers" below")

### Special commands

#### `go`
Samples all recorded calls and prints the measurements to `stdout`.

#### `set_counters [` *counter* `[...]]`
Set the PAPI counters to be measured.  The event names (*counter*) are parsed to
event codes.  Unknown events or events incompatible with the previously selected
set are ignored.  Invoking `set_counters` without arguments disables PAPI.

`set_counters` takes affect *immediately* and affects all following sampling
phases.

#### `{omp` and `}`
Start and end an OpenMP parallel region.  Calls registered between these
commands are executed in parallel in OpenMP tasks and only return one total
measurement result.

#### `info` *kernel_name*
Print the signature of a kernel to `stderr` immediately.

`info` expects 1 argument:
- *kernel_name*:  Name of the kernel

#### `print` *text*
`print` prints the remainder of the line (*text*) to `stdout` immediately.


### Named Buffer
Named buffers are identified by variables beginning with a letter (e.g. `"A"`,
`"a_1234"`).  They are created and modified through the following commands, all
of which take effect immediately and not between kernel invocations.

#### `*malloc` *name size*
Allocate a Named Buffer, fill it with random data and set a pointer to its
beginning.  The prefix `*` identifies the data type and the initial random
numbers in the buffer:

| prefix | data type         | random numbers         |
| ------ | ----------------- | ---------------------- |
|        | `char`            | {0, 1, ..., 255}       |
| `i`    | `int`             | {0, 1, ..., `MAX_INT`} |
| `s`    | `float`           | [0, 1)                 |
| `d`    | `double`          | [0, 1)                 |
| `c`    | `complex<float>`  | [0, 1) + [0, 1) *i*    |
| `z`    | `complex<double>` | [0, 1) + [0, 1) *i*    |

`*malloc` expects two arguments:
- *name*: A previously unused buffer name, beginning with a letter.
- *size*: Number of elements of the associated data type to allocate.

#### `*offset` *name offset new_name*
Set a pointer to an offset into an existing Named Buffer.  

`*offset` expects three arguments:
- *name*: A previously allocated named buffer.
- *offset*: Number of elements of the data type (prefix `*`, see above) from the
  start of buffer *name*, where *new_name* shall point.
- *new_name*: A previously unused buffer name, beginning with a letter.

#### `free` *name*
Deletes a Named Buffer (or offset pointer) and all offsets computed from it.

`free` expects one argument:
- The name of the variable.


A note on RDTSC and clock speeds
-------------------------------- 
Samplers measure clock cycle counts in terms of the CPU's time stamp counter (in
X86: `rdtsc`).  This counter is guaranteed to be incremented at a constant rate
and thus yields reliable timings.  On the other hand, this rate is not
necessarily equal to the CPU clock speed, especially, when the clock speed is
dynamically changed due to Turbo Boost or power saving features.
