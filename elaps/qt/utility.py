#!/usr/bin/env python
"""Qt utility routines."""
from __future__ import division, print_function


def widget_setinvalid(widget, state=True):
    """Set the invalid attribute and refresh."""
    widget.setProperty("invalid", state)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
