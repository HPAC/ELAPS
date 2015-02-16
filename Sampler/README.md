ELAPS:Sampler
=============

The Samplers form the low level base of ELAPS.  Each Sampler is configured and
liked a fixed set of kernel routines (usually BLAS and LAPACK), a fixed
computer system  and fixed kernel implementations.  They accurately measure the
performance of individual kernel invocations in terms of execution time and, if
PAPI is available, performance counters (such as cache misses).


Compilation
-----------

To build a Sampler, invoke `make.sh` with a configuration file from `cfgs/`.  A
configuration file is essentially a bash script in which a series of
configuration parameters are defined.  A full template detailing all
parameters, as well as their effects and default values can be found in
`cfgs/examples/template.cfg`.  `cfgs/examples/` also contains several example
configurations that can serve as a base for your own configuration.

The build process will compile and link the Sampler in
`build/<name>/sampler.x`, where `<name>` is (by default) the basename of the
configuration file without the `.cfg`.

The most common parameters are the following:

* `KERNEL_HEADERS` is a list of header files. (default: BLAS and LAPACK)

* `LINK_FLAGS` are linking flags that include implementations for all kernels
  specified in `KERNELS`. (e.g. linking with BLAS and LAPACK)

* `PAPI_COUNTERS_MAX` and `PAPI_AVAIL` specify up to how many counters PAPI can
  use in parallel and what their codes (names) are.  By default,
  `PAPI_COUNTERS_MAX=0` disables PAPI support entirely.  [These can be
  determined by `gathercfg.sh`; see below.]

* `BACKEND` and associated parameters tell ELAPS:Mat how ot submit sampler
  jobs to remote machines through job systems (default: local execution)
  * `BACKEND_PREFIX` is put right in front of the Sampler command.  It should
    set threading variables for the kernel implementations, such as
    `OPENMP_NUM_THREADS`, where the string `"{nt}"` is used as a placeholder
    for the number of threads.

* `CPU_MODEL`, `NCORES`, `FREQUENCY_HZ`, and others contain further information
  on the target machine, which mainly allow ELAPS:Viewer to compute derived
  performance metrics, such as Gflops/s or efficiency.  [These can be determined
  by `gathercfg.sh`; see below]

### Automatically collecting configuration parameters

The script `gathercfg.sh` attempts to automatically detect many of the
system-dependent configuration parameters and produces text output that can be
directly included in a configuration script.  The detected options are
`NCORES`, `THREADS_PER_CORE`, `CPU_MODEL`, `FREQUENCY_HZ`, `PAPI_COUNTERS_MAX`,
and `PAPI_COUNTERS_AVAIL`.  However, `DFLOPS_PER_CYCLE` (how many double
precision floating point operations the CPU can issue per cycle) can so far not
be detected and needs to be set manually.


Usage
-----
To perform performance experiments, invoke the compiled Sampler (`sampler.x`)
and pass a sequence of kernel invocations (referred to as "calls") in stdin.
Each call is name of the kernel followed by its arguments, separated by spaces.
E.g.:

```
dgemm_ N N 1000 1000 1000 1.0 [1000000] 1000 [1000000] 1000 1.0 [1000000] 1000
dtrsm_ L L N U 1000 1000 1.0 [1000000] 1000 [1000000] 1000
```

Once the end of the input (or the special command `go`) is reached, the Sampler
executes all entered calls and afterwards prints one line to stdout for each of
them.  This line starts with the number cycles the call took (in terms of
`rdtsc`) followed by the values of all measured PAPI counters. E.g. (without
PAPI):

```
163421930
79574788
```

For further details on the call specification syntax and the full list of
available special commands see `SAMPLER.md` or type enter the `help` command in
any sampler.


A note on RDTSC and clockrates
------------------------------
Samplers measure clock cycle counts in terms of the instruction `rdtsc`, which
reads the CPU's time stamp counter.  This counter is usually guaranteed to be
incremented at a constant rate.  However, 

1. This rate does not need to be equal to CPU frequency, and
2. Features such as Turbo Boost and AVX instructions may change the core
   frequency, while the `rdtsc` is unchanged.

These properties in no way penalize the accuracy of `rdtsc` but they have to be
taken into account when interpreting the results, which not always translates
1-to-1 into core cycles.
