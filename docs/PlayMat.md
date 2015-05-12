ELAPS PlayMat
=============

The *PlayMat*  in `bin/PlayMat` is a PyQt4-based graphical user interface to
create, edit and execute [`Experiment`](Experiment.md)s.  Its interface
elements closely resemble the `Experiment`'s attributes.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [ELAPS PlayMat](#elaps-playmat)
  - [Startup](#startup)
  - [Interface Elements](#interface-elements)
    - [Calls](#calls)
    - [Vary](#vary)
  - [Execution](#execution)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


Startup
-------

When started, the *PlayMat* by default reloads its last state before closing,
i.e., the last designed `Experiment`.  When an `Experiment` file (`.elr`) is
passed as an argument, that experiment is loaded instead.  When `--reset` is
passed, the *PlayMat* is reset to the following default `Experiment`:

    Sampler:    first found
    #threads:   1
    for i = 100:100:2000 :
        repeat 10 times:
            dgemm(N, N, i, i, i, 1, A, i, B, i, 1, C, i)

The *PlayMat* automatically detects and loads all available Samplers.  


Interface Elements
------------------

### Calls

The `Experiment`'s `calls` are entered in the *PlayMat*'s main area.  Calls are
added, cloned, and removed via the context-menu (right click) or keyboard
shortcuts.  They are reordered via drag'n'drop.

The *PlayMat* can hide certain types of arguments (e.g., leading dimensions)
from the user and automatically set their values.  This behaviour can be
changed from the `View` menu.  When shown, these arguments can be automatically
determined by the *PlayMat* through their context menu.

### Vary
The `vary` options are set through the operand argument's context menu and
visualized in the lower right corner of each operand.


Execution
---------

The `Experiment` is named executed through the arrow symbol on the top right.
(When *shift* is pressed, the last `Experiment`'s name is reused.)  An
executing (or pending) `Experiment` is independent from the *PlayMat*; the GUI
can be used immediately to set up new experiments.

The progress of all started `Experiment`s is shown on the bottom of the
*PlayMat*.  (It is determined by the contents of the generated Report file,
which is flushed after each `range` iteration.)  The context menu provides
options, to remove, kill or reload `Experiment`s as well as opening them in the
[*Viewer*](Viewer.md).
