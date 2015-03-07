#!/usr/bin/env python
"""Plotting routines for reports."""
from __future__ import division, print_function

from report import Report, apply_stat

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


default_colors = [
    "#004280", "#e6a500", "#bf0000", "#009999", "#5b59b2", "#969900",
    "#bf0073", "#bf9239", "#004ee6", "#ff7a00"
]

default_styles = {
    "legend": {"color": "#888888"},
    "med": {"linestyle": "-"},
    "min": {"linestyle": "--"},
    "max": {"linestyle": ":", "linewidth": 2},
    "avg": {"linestyle": "-."},
    "min-max": {"hatch": "...", "facecolor": (0, 0, 0, 0)},
    "std": {"alpha": .25},
    "all": {"linestyle": "None", "marker": "."},
}


def plot(datas, stat_names=["med"], colors={}, styles={}, xlabel=None,
         ylabel=None, figure=None):
    """Plot a series of data sets."""
    styles = default_styles.copy()
    styles.update(styles)

    range_min = min(min(data) for name, data in datas)
    range_max = max(max(data) for name, data in datas)

    if range_min == range_max:
        bar_datas = [(key, data.values()[0]) for key, data in datas]
        return bar_plot(bar_datas, stat_names, colors, styles, ylabel, figure)
    else:
        range_datas = []
        for key, data in datas:
            if min(data) == max(data):
                values = data.values[0]
                range_datas.append(
                    (key, {range_min: values, range_max: values})
                )
            else:
                range_datas.append((key, data))
        return range_plot(range_datas, stat_names, colors, styles, xlabel,
                          ylabel, figure)


def range_plot(datas, stat_names=["med"], colors={}, styles={}, xlabel=None,
               ylabel=None, figure=None):
    """Plot with range on the x axis."""
    # min-max stat
    stat_names = stat_names[:]
    if "min" in stat_names and "max" in stat_names:
        stat_names.insert(0, "min-max")
        stat_names.remove("min")
        stat_names.remove("max")

    # set up figure
    fig = figure or Figure()
    axes = fig.gca()
    axes.cla()
    axes.set_axis_bgcolor("#f0f0f0")
    if ylabel is not None:
        axes.set_ylabel(ylabel)
    axes.hold(True)

    # plots
    colorpool = default_colors[::-1]
    for name, data in datas:
        color = colors.get(name) or colorpool.pop()
        for stat_name in stat_names:
            if stat_name == "all":
                xs, ys = zip(*((key, value)
                               for key, values in data.iteritems()
                               for value in values))
                axes.plot(xs, ys, color=color, **styles["all"])
            elif stat_name == "min-max":
                min_data = apply_stat("min", data)
                max_data = apply_stat("max", data)
                xs = sorted(set(min_data) & set(max_data))
                min_ys = [min_data[x] for x in xs]
                max_ys = [max_data[x] for x in xs]
                axes.fill_between(xs, min_ys, max_ys, color=color,
                                  **styles["min-max"])
            elif stat_name == "std":
                avg_data = apply_stat("avg", data)
                std_data = apply_stat("std", data)
                xs = sorted(set(std_data) & set(avg_data))
                min_ys = [avg_data[x] - std_data[x] for x in xs]
                max_ys = [avg_data[x] + std_data[x] for x in xs]
                axes.fill_between(xs, min_ys, max_ys, color=color,
                                  **styles["std"])
            else:
                # all other stats
                stat_data = apply_stat(stat_name, data)
                xs = sorted(stat_data)
                ys = [stat_data[x] for x in xs]
                axes.plot(xs, ys, color=color, **styles[stat_name])

    # ymin = 0
    limits = axes.axis()
    axes.axis((limits[0], limits[1], 0, limits[3]))

    # legend
    colorpool = default_colors[::-1]
    legend = []
    legend_style = styles["legend"].copy()
    for name, values in datas:
        color = colors.get(name) or colorpool.pop()
        legend_style["color"] = color
        legend.append((Line2D([], [], **legend_style), name))
    legend_stat_names = stat_names[:]
    if "min" in legend_stat_names and "max" in legend_stat_names:
        legend_stat_names.insert(0, "min-max")
        legend_stat_names.remove("min")
        legend_stat_names.remove("max")
    color = styles["legend"]["color"]
    for stat_name in legend_stat_names:
        legend_style = styles["legend"].copy()
        if stat_name == "min-max":
            legend_elem = Patch(edgecolor=color, **styles[stat_name])
        elif stat_name == "std":
            legend_elem = Patch(color=color, **styles[stat_name])
        else:
            legend_elem = Line2D([], [], color=color, **styles[stat_name])
        legend.append((legend_elem, stat_name))
    if legend:
        axes.legend(*zip(*legend), loc=0, numpoints=3)

    return fig


def bar_plot(datas, stat_names=["med"], colors={}, styles={}, ylabel=None,
             figure=None):
    """Barplot."""
    # min-max stat
    stat_names = stat_names[:]
    if "min" in stat_names and "max" in stat_names:
        stat_names.insert(0, "min-max")
        stat_names.remove("min")
        stat_names.remove("max")

    # set up figure
    fig = figure or Figure()
    axes = fig.gca()
    axes.cla()
    axes.set_axis_bgcolor("#f0f0f0")
    if ylabel is not None:
        axes.set_ylabel(ylabel)
    axes.hold(True)

    width = .8 / len(datas)

    # plots
    for dataid, (name, data) in enumerate(datas):
        color = colors[name]
        for statid, stat_name in enumerate(stat_names):
            left = statid + dataid * width
            if stat_name == "all":
                xs = len(data) * [left + width / 2]
                ys = data
                axes.plot(xs, ys, color=color, **styles["all"])
            elif stat_name == "min-max":
                min_y = apply_stat("min", data)
                max_y = apply_stat("max", data)
                axes.bar(left, max_y - min_y, width, min_y, color=color)
            elif stat_name == "std":
                avg = apply_stat("avg", data)
                std = apply_stat("std", data)
                axes.bar(left, 2 * std, width, avg - std, color=color)
            else:
                # all other stats
                value = apply_stat(stat_name, data)
                axes.bar(left, value, width, color=color)

    # ymin = 0
    limits = axes.axis()
    axes.axis((limits[0], limits[1], 0, limits[3]))

    # xlabels
    axes.set_xticks([i + .4 for i in range(len(stat_names))])
    axes.set_xticklabels(stat_names)

    # legend
    legend = [(Patch(color=colors[name]), name) for name, data in datas]
    if legend:
        axes.legend(*zip(*legend), loc=0, numpoints=3)

    return fig
