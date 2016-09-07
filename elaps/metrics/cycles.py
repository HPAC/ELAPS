"""Cycle count metric."""


def metric(data, **kwargs):
    """Execution time in cycles.

    Computed as:
        cycles  (atomic metric)

    cycles: execution time in cycles (from time stamp counter)
    """
    return data.get("cycles")

metric.name = "time [cycles]"
