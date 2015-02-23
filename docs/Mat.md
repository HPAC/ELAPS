ELAPS:Mat
=========

This file describes ELAPS:Mat, the GUI used to create and submit performance
experiments. 


Startup
-------
On Startup, ELAPS:Mat automatically detects all compiled samplers (in
`../Sampler/build/`), loads their info files and associates them with
corresponding backends from `backends/`.  It then tries to revert to the last
state the Mat was in before closing.  If this fails, the command line option
`--reset` is passed or no previous state is detected, it defaults to a
predefined state.


GUI Components
--------------
This section details the functionality of the Mat's GUI components.

### Top Toolbar
The top toolbar allows to select the Sampler, fix the number of threads for
the kernel library, and run (or submit) jobs.  If you are missing a Sampler in
the list, check the console output of the Mat for hints and try to rebuild the
Sampler.

### The Call(s)
At the heart of the Mat is the call (or list of calls) for the experiment.
The "+" button below the list adds a new call and the "x" button next to each
call allows to remove it; calls can be reordered via drag'n'drop.

Typing in a call's routine field reveals the list of kernels provided by the
currently selected Sampler.  Once a routine name is entered completely,
corresponding argument fields are added, filled with default values and
formatted according to their type and meaning in the call (provided that  a
signature is associated with the kernel, otherwise a raw interface to the
Sampler is provided).  For BLAS and LAPACK kernels, the Mat also loads the
routine's documentation, which is accessible by hovering over the arguments
(provided the documentation git-submodule is installed).

The types of argument visible to the user can be changed in the "View" menu.
E.g., leading dimension arguments are by default hidden from the user.

### Data Arguments and Linking 
Data arguments (i.e., matrices, vectors, etc.) play an important role in
ELAPS:Mat.  By default, all data arguments are independent, however, the user
can choose to use the same argument in several locations within one or across
multiple calls.  If this is the case, ELAPS:Mat will automatically ensure that
all corresponding size dimensions match; changing one dimension will then also
affect other dimensions. 

By default, each argument uses the same memory region in all places.  See
"Varying Data Arguments" to see how different regions can be used

### Parallel calls
Selection the option "parallel calls" from the "Options" menu will cause all
calls to be executed in parallel OpenMP tasks using as many threads as needed.
As a result, only one overall runtime will be reported.

### Ranges
Each call in ELAPS:Mat is not executed once but several times, depending on the
selected ranges and repetition count.  Ranges can be selected from the "Ranges"
menu and can be understood as nested loops:

1. The outermost loop corresponds to the optional "outer" range.  Each value in
   this range will result in a separate data point in the resulting report.  The
   range variable can be used in the calls in place of dimension, leading
   dimension and scalar arguments.  (E.g., this can be used to see how kernels
   behave for varying operand sizes.)
   As an alternative to the default "outer" range, this range can be used to
   run the kernels with different thread counts.
2. The next loop repeats the same experiment several times. In the resulting
   report, statistical quantities are computed from these repeated experiments
   and are useful to get smoother results, avoid outliers and inspect the
   variability in performance.
3. The innermost loop corresponds to the optional "inner" range.  All calls will
   be executed for each value in this range but contribute to the same
   data point.  The "sum over" range will sum each contribution, while the
   "parallel range" will execute all contained calls in parallel, reporting the
   overall execution time (this range implies the "parallel calls" options).

### Varying Data Arguments
By default, all data arguments refer to the same memory location across all
ranges and repetitions.  Enabling the "vary matrices" option allows to change
this behavior and have data arguments refer to different memory regions in each
repetition or "inner" range iteration.  The main use of this feature is to
ensure that operands are placed out of cache.  Each operand can vary along each
of its dimensions.  Varying along the first dimension will automatically
increase the corresponding leading dimension arguments.  An additional offset
can increase the gap between successive regions (to, e.g., avoid performance
implications due to prefetching.

### Script Header
Using the script header option allows to run a custom "header" script before the
actual sampler is invoked.  This can be used to e.g. set individual environment
variables for the Sampler execution.

### Running/Submitting jobs
When running/submitting an experiment, a portable "report" file is generated.
This file contains all relevant information on the experiment (i.e., the state
of ELAPS:Mat at submit time) as well as the raw output of the invoked
ELAPS:Sampler.

Before and while the experiment is running, further auxiliary files are
generated in the same directory, which allow to follow exactly how the
experiment is performed.  These files are deleted once the experiments concludes
successfully.

Signatures
----------
Signatures (found in `signatures/`) provide additional information on kernels to
ELAPS:Mat.  Such a signature contains one entry for each of the kernels
arguments, specifying the arguments' meanings and their relations.  Signatures
are loaded dynamically by ELAPS:Mat depending on the currently selected kernel.
