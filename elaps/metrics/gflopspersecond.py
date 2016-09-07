"""Performance metric in Gflops/second."""

from __future__ import division


def metric(data, experiment, **kwargs):
    """Performance in billions of floating-point operations (Gflops) per second.

    Computed as:
        1e-9 * flops * freq / cycles

    1e-9:   Giga prefix
    flops:  minimal required mathematical flop count
    freq:   CPU frequency
    cycles: execution time in cycles (from time step counter)
    """
    nops = data.get("flops")
    cycles = data.get("cycles")
    freq = experiment.sampler.get("frequency")
    if nops is None or cycles is None or freq is None:
        return None
    return 1e-9 * nops * (freq / cycles)

metric.name = "performance [Gflops/s]"
