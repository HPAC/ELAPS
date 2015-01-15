#!/usr/bin/env python
from __future__ import division, print_function

from viewerqt import Viewer_Qt
from qmplplot import QMPLplot

import signal


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Viewer_Qt(QMPLplot)

if __name__ == "__main__":
    main()
