ELAPS
=====

Experimental Linear Algebra Performance Studies


What is ELAPS?
--------------

ELAPS is a multi-platform open source environment for fast yet powerful
experimentation with dense linear algebra kernels, algorithms, and libraries.
It allows to construct experiments to investigate how performance and
efficiency vary depending on  factors such as caching, algorithmic parameters,
problem size, and parallelism.  Experiments are designed either through Python
scripts or a specialized GUI, and run on the whole spectrum of architectures,
ranging from laptops to clusters, accelerators, and supercomputers.  The
resulting experiment reports provide various metrics and statistics that can be
analyzed both numerically and visually.


Requirements
------------

- C/C++ compiler
- Python version 2.7.x
- PyQt4
- Matplotlib

- Kernels to measure (e.g. BLAS/LAPACK libraries)


Overview
--------

The Framework consists for three layers:

- The first, "bottom" layer is written in C/C++ and contains the Sampler, a
  low-level command line tool responsible for executing and timing individual
  kernels.  The Sampler has to be compiled for each specific combination of
  hardware and libraries (the only stage in which the user needs to configure
  the system); ELAPS can interface with any number of Samplers.
  See [docs/Sampler.md](docs/Sampler.md).

- The second, "middle" layer is the Python library `elaps`, which centers
  around the class `Experiment` that implements the previously introduced
  experiments.  An Experiment can be executed on different Samplers, both
  locally or through job submission systems.  The outcome is a `Report`, which
  provides not only structured access to the individual measurements, but also
  functionality to analyze different metrics and statistics.
  See [docs/Experiment.md](docs/Experiment.md)
  and [docs/Report.md](docs/Report.md).

  This layer also includes the `plot` module, which is based on the matplotlib
  library, and is used to easily visualize Reports in graphical form.
  See [docs/plot.md](docs/plot.md).

- The third, "top" layer adds a graphical user interface, written in PyQt4, to
  both design `Experiment`s in the *PlayMat* and study Reports and plots in the
  *Viewer*.
  See [docs/PlayMat.md](docs/PlayMat.md)
  and [docs/Viewer.md](docs/Viewer.md).


Installation
------------

Installing ELAPS boils down to configuring and compiling Samplers; the Python
package "elaps" including the GUI  should work "out of the box".


Bugs
----

This project is in a early stage, so bugs are to be expected (especially in the
GUI parts).  If you found one, please file an issue detailing how you reached
the problem and the error message or stack trace if any is printed in the
console.  Thank you!

- [There are currently no known bugs]
