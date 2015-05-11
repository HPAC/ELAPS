ELAPS Experiment
================

*This file is under construction*

The `Experiment` class is the central component of the `elaps` python module.
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

Setter: `set_sampler(sampler)`

### `papi_counters`

Setter: `set_papi_counters(papi_countes)`

### `nthreads`

Setter: `set_nthreads(nthreads)`

### `range`

Setters:
- `set_range([range_var, range_vals])` or `set_range(None)`
- `set_range_var(range_var)` and `set_range_vals(range_vals)`

### `nreps`

Setter: `set_nreps(nreps)`

### `sumrange`

Setters:
- `set_sumrange([sumrange_var, sumrange_vals])` or `set_sumrange(None)`
- `set_sumrange_var(sumrange_var)` and `set_sumrange_vals(sumrange_vals)`

### `sumrange_parallel`

Setter: `set_sumrange_parallel(sumrange_parallel)`

### `calls_parallel`

Setter: `set_calls_parallel(calls_parallel)`

### `calls`

Setters:
- `set_calls(calls)`
- `add_call(call)`, `set_call(callid, call)`, and `remove_call(callid)`
- `set_arg(callid, argid, value)`

### `vary`

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
