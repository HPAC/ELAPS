ELAPS Experiment
================

*This file is under construction*

The `Experiment` class is the central component of the `elaps` Python module.
It both statically represents the experiments within the ELAPS framework and
features functionality to support their design and handling.


Setup and Attributes
--------------------

The `Experiment` setup essentially describes how and in what environment the set
of kernel invocations defined in its `calls` attribute shall be executed.  The
attributes of the `Experiment` class that form this setup are described in this
section.

For each attribute `*`, there exists a setter function `set_*()`.  These
functions incorporate type and consistency checks for the attribute values and
should be preferred over setting the attributes directly.  Upon encountering
invalid or incompatible values, the setters will throw corresponding exceptions.
Each setter allows two optional keyword arguments:
- `force=True` tells the `Experiment` to, if possible, avoid exceptions by
  replacing incompatible values with default ones or otherwise adjusting itself
  to ensure consistency.
- `check_only=True` will only perform the consistency checks (and possibly throw
  exceptions) but will not not actually set the attribute to the given value

The following subsections present the `Experiment` attributes "top down", i.e.,
each attribute may be affected by the preceding attributes' values.

### `sampler`
A data structure (`dict`) describing the [Sampler](Sampler.md) used in the
experiment.  This data structure is generated automatically alongside each
Sampler compilation as `info.py` in its build directory.  To load such
structures, the package `elaps.io` provides the routines the utility routines
`load_sampler(name)` and `load_all_samplers()`.

Relevant for the `Experiment` setup are the following `sampler` entries:
- `papi_enabled`: Whether PAPI is available.  If so: 
  - `papi_counters_avail`: A list of available PAPI event names.
  - `papi_counters_max`: Maximum number of parallel counters.
- `nt_max`: The maximum number of threads on the system.
- `omp_enabled`: Wether OpenMP support is available (for `sumrange_parallel` and
  `calls_parallel`).
- `kerlens`: A `dict` of available kernel names with their C signatures.

Setter: `set_sampler(sampler)`

### `papi_counters`
The list of PAPI counters (as a `tuple`) to be measured.  The counters have to
be supported by the Sampler and cannot exceed its counter limit.

Setter: `set_papi_counters(papi_countes)`

### `nthreads`
The number of threads used by the kernel library.  The number of threads is
limited by the Sampler.

Instead of a number, `range[0]` (the range variable) can be used as a value to
let the number of threads depend on the ranges value.

Setter: `set_nthreads(nthreads)`

### `range`
`[range_var, range_vals]`, a range variable and range values as a 2-element
`list`, or `None`.  If set, `range_var` is an `elaps.symbolic.Symbol`, while the
`range_vals` is a finite iterable (such as a `list` or an
`elaps.symbolic.Range`).

Setters:
- `set_range([range_var, range_vals])` or `set_range(None)`
- `set_range_var(range_var)` and `set_range_vals(range_vals)`

### `nreps`
The number of repetitions (positive `int`).

Setter: `set_nreps(nreps)`

### `sumrange`
`[sumrange_var, sumrange_vals]`, a range variable and range values as a
2-element `list`, or `None`.  If set, `sumrange_var` is an
`elaps.symbolic.Symbol`, while the `sumrange_vals` is a finite iterable (such as
a `list` or an `elaps.symbolic.Range`) that may depend symbolically on
`range_var`. (e.g., if `range_var == Symbol("i")`, one could have `range_vals =
Range("1:i")`.)

Setters:
- `set_sumrange([sumrange_var, sumrange_vals])` or `set_sumrange(None)`
- `set_sumrange_var(sumrange_var)` and `set_sumrange_vals(sumrange_vals)`

### `sumrange_parallel`
Wether the calls in the sumrange shall we executed in parallel.  The used
Sampler must support OpenMP for this option.

Setter: `set_sumrange_parallel(sumrange_parallel)`

### `calls_parallel`
Wether the calls for one sumrange iteration shall be executed in parallel.  The
used Sampler must support OpenMP for this option.  The option is automatically
implied when `sumrange_parallel == True`.

Setter: `set_calls_parallel(calls_parallel)`

### `calls`
The `list` of kernel invocations to be sampled.  Each kernel in this list must
be supported by the Sampler.  

There are two types of calls:
- `elaps.signature.Call` instances represent calls with associated `Signature`s.
- `elaps.signature.BasicCall` instances can be used if no corresponding
  `Signature`, however these calls have severely limited functionality with
  respect to data handling.

The types of arguments for calls and their possible values are discussed in the
following subsections.

Setters:
- `set_calls(calls)`
- `add_call(call)`, `set_call(callid, call)`, and `remove_call(callid)`
- `set_arg(callid, argid, value)`

#### Calls with a `Signature` (`Call`)
`Signature`s can be loaded through `elaps.io.load_signature(name)` or
`elaps.io.load_all_signatures()`.  Calling such a Signature, results in a
corresponding `Call` instance.  For more details on `Signature`s see
[Signature.md](Signature.md).

Within an `Experiment`, a `Call`'s values have to conform with its `Signature`
and possibly other calls' in the `Experiment`:
- Flag arguments must contain allowed values (e.g., `N` or `T` for a `trans`
  argument).
- Dimension arguments must be positive `int`s or `elaps.symbolic.Expression`s
  (symbolic expressions), which may depend on both the `range_var` and
  `sumrange_var`.
- Scalar arguments must be numbers or symbolic `Expressions`s that evaluate to
  the associated data types (`int`, `float`, or `complex`).
- Data arguments (or operands) must be strings beginning with a letter.
  Operands may occur repeatedly both within one call and across calls; in this
  case all corresponding dimension and leading dimension arguments must have
  consistent values.
- Leading dimension arguments must be `int`s or symbolic `Expression`s that are
  at least as large as the first dimension of the corresponding operand.

#### Calls without a `Signature` (`BasicCall`)
Each sampler provides minimal signatures for each of its associated kernels,
which basically are lists of the involved C arguments (e.g. `("dcopy", "int *",
"double *", "int *", "double *", "int *")`).
- `char *` arguments can be passed any string.
- Any other argument (`int *`, `float *`, or `double *`) can be passed values in
  two different formats:
  - A single value or a list of values, e.g. `1,2` to represent the complex
    number *1 + 2 i*.
  - A size in brackets (e.g. `"[100000]"`) will pass a buffer of such many
    elements from the Sampler's Dynamic Memory buffer.
  In both formats, symbolic `Expression`s are allowed.

### `vary`
Wether operands refer to the same memory buffers across repetitions and
iterations of the sumrange and how they depend on these iterations.
`vary` is a `dict` that has one entry for each operand, which in turn is a
`dict` with they following keys:
- `with`: A `set` of variables with which the operand varies.  Can contain
  `"rep"` (to vary with repetitions) and the `sumrange_var`.
- `along`: Along which dimension the variable shall vary. (only makes sense for
  matrix operands.)  If `along == 0`, matrix arguments for different iterations
  would be stacked along their first dimension (in BLAS data layout forming a
  column stack), thereby increasing the leading dimension; `along == 1` would
  stack them along their second dimension (in BLAS data layout forming a row
  stack).
- `offset`: An additional offset to further separate consecutive iterations'
  operands.  Can be an `int` or a symbolic `Expression`.

Setters:
- `set_vary(name, with_=None, along=None, offset=0)`
- `set_vary_with(name, with_)`, `add_vary_with(name, with_var)`, and
  `remove_vary_with(name, with_var)`
- `set_vary_along(name, along)`
- `set_vary_offset(name, offset)`


Execution and Job Submission
----------------------------


Storing and Loading Experiments
-------------------------------
