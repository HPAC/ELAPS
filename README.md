ELAPS
=====

Experimental Linear Algebra Performance Studies

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [What is ELAPS?](#what-is-elaps)
- [Requirements](#requirements)
- [Overview](#overview)
- [Installation](#installation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


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

  The Sampler comes with a set of utility routines that cover basic tasks of
  experiment setups, such as matrix initializations and file-IO.
  See [docs/Utility.md](docs/Utility.md).

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
  both design `Experiment`s in the *PlayMat* and study `Report`s and plots in
  the *Viewer*.
  See [docs/PlayMat.md](docs/PlayMat.md)
  and [docs/Viewer.md](docs/Viewer.md).


Installation
------------

To use ELAPS:
- clone the GitHub repository, and
- compile one or more `Sampler`s (see [docs/Sampler.md](docs/Sampler.md)).

Now, ELAPS is ready to go.  To get started, run `bin/PlayMat`.
