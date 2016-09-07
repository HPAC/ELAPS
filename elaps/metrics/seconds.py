"""Time metric in seconds."""

from __future__ import division


def metric(data, experiment, **kwargs):
    """Execution time in seconds.

    Computed as:
        cycles / freq

    cycles: execution time in cycles (from time step counter)
    freq:   CPU frequency
    """
    cycles = data.get("cycles")
    freq = experiment.sampler.get("frequency")
    if cycles is None or freq is None:
        return None
    return cycles / freq

metric.name = "time [s]"
