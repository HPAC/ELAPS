ELAPS
==========

Experimental Linear Algebra Performance Studies

What is ELAPS?
---------

ELAPS provides an intuitive interface to common performance related questions
regarding dense linear algebra kernels and algorithms, such as
* How fast is my BLAS implementation on this system?
* How well does my BLAS implementation use my system's resources?
* For which parameter value do I obtain the best performance?
* How does the cache locality of operands affect this kernel?
* Which algorithm/sequence of kernels is faster?

Requirements
------------

* C/C++ compilers
* python version 2.7.x
* PyQt4
* Matplotlib

* Kernels to measure (e.g. BLAS/LAPACK libraries)


Overview
------------

The Framework consists for three parts:

1. A collection of Samplers, 
2. The GUI, and
3. The viewer

### Samplers
The Samplers, located in `Sampler/`, form the low level base of the Framework.
Each Sampler is configured and liked a fixed set of kernel routines (usually
BLAS and LAPACK), a fixed computer system  and fixed kernel implementations.
They accurately measure the performance of individual kernel invocations in
terms of execution time and, if PAPI is available, performance counters (such
as cache misses).

For further details on Samplers, see `Sampler/README.md`

### The GUI
The GUI, located in `GUI/Gui.py`, creates and runs/submits performance
experiments using previously compiled Samplers.  Central to the GUI is the
visual representation of kernels and their operands that now only facilitates
the user's understanding of how the kernels function but also automatically
completes common kernel operands such as matrix sizes and leading dimensions.
Further features, such as performing experiments for ranges of matrix sizes, or
number of threads, as well as placing operands in or out of cache, cover many
common performance experiments.

For further details on the GUI, see `GUI.md`.

### The Viewer
Each performance experiment submitted in the GUI results in a portable
experiment report.  The Viewer, located in `GUI/Viewer.py`, loads these reports
and helps the user analyze them by plotting their performance in terms of
different metrics ranging from execution time in cycles to Gflops/s and
efficiency.  Export features for these plots and underlying data yield
presentation and paper quality figures with minimal effort.

For further details on the Viewer, see `Viewer.md`.


Installation
------------

Installing FLAPS boils down to configuring and compiling Samplers; both the
GUI and Viewer should work "out of the box".

### Notes on installing the prerequisites
The required packages listed above can be installed in many ways, which depend
on the operating system.  Below are commands to install these packages using
common package managers.

* MacPorts (OS X):

    sudo port install gcc py27-pyqt4 matplotlib

* AptGet (Debian, Ubuntu)

    sudo apt-get install python-qt4 python-matplotlib


Bugs
----

This project is in a early stage, so bugs are to be expected (especially in the
GUI).  If you found one, please file an issue detailing how you reached the
problem and the error message or stack trace if any is printed in the console.
Thank you!

* [There are currently no known bugs]
