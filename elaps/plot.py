#!/usr/bin/env python
"""Plotting routines for reports."""
from __future__ import division, print_function

import defines
from report import Report, apply_stat

from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def plot(datas, stat_names=["med"], colors=[], styles={}, xlabel=None,
         ylabel=None, legendargs={}, figure=None):
    """Plot a series of data sets."""
    styles = defines.plot_styles.copy()
    styles.update(styles)

    # set up figure
    fig = figure
    if not fig:
        from matplotlib import pyplot
        fig = pyplot.gcf()
    fig.patch.set_facecolor(defines.face_color)
    axes = fig.gca()
    axes.cla()
    axes.set_axis_bgcolor(defines.background_color)
    if ylabel is not None:
        axes.set_ylabel(ylabel)
    axes.hold(True)

    # filter empty data
    datas = [(name, data) for name, data in datas if data]
    if not datas:
        return fig

    range_vals = [val for name, data in datas for val in data
                  if val is not None]
    if not range_vals:
        bar_datas = [(key, data[None]) for key, data in datas]
        return bar_plot(bar_datas, stat_names, colors, styles, ylabel,
                        legendargs, fig)
    else:
        range_datas = []
        for key, data in datas:
            if None in data:
                range_datas.append((key, {
                    min(range_vals): data[None],
                    max(range_vals): data[None]
                }))
            else:
                range_datas.append((key, data))
        return range_plot(range_datas, stat_names, colors, styles, xlabel,
                          ylabel, legendargs, fig)


def range_plot(datas, stat_names=["med"], colors=[], styles={}, xlabel=None,
               ylabel=None, legendargs={}, figure=None):
    """Plot with range on the x axis."""
    # min-max stat
    stat_names = stat_names[:]
    if "min" in stat_names and "max" in stat_names:
        stat_names.insert(0, "min-max")
        stat_names.remove("min")
        stat_names.remove("max")

    fig = figure

    axes = fig.gca()
    axes.set_xlabel(xlabel)

    # plots
    colorpool = (colors + defines.colors)[::-1]
    for name, data in datas:
        color = colorpool.pop()
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

    # axis limits
    range_vals = [val for name, data in datas for val in data
                  if val is not None]
    limits = list(axes.axis())
    # ymin
    limits[2] = 0
    gap = (limits[1] - limits[0]) / 20
    # xmin
    range_min = min(range_vals)
    if range_min > 0 and range_min < gap:
        limits[0] = 0
    else:
        limits[0] = range_min - gap
    # xmax
    range_max = max(range_vals)
    limits[1] = range_max + gap
    axes.axis(limits)

    # legend
    colorpool = (colors + defines.colors)[::-1]
    legend = []
    legend_style = styles["legend"].copy()
    for name, values in datas:
        color = colorpool.pop()
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
        args = {"loc": 0, "numpoints": 3}
        args.update(legendargs)
        axes.legend(*zip(*legend), **args)

    return fig


def bar_plot(datas, stat_names=["med"], colors=[], styles={}, ylabel=None,
             legendargs={}, figure=None):
    """Barplot."""
    # min-max stat
    stat_names = stat_names[:]
    if "min" in stat_names and "max" in stat_names:
        stat_names.insert(0, "min-max")
        stat_names.remove("min")
        stat_names.remove("max")

    fig = figure

    axes = fig.gca()

    groupwidth = .8
    width = groupwidth / len(datas)

    # plots
    colorpool = (colors + defines.colors)[::-1]
    for dataid, (name, data) in enumerate(datas):
        color = colorpool.pop()
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
                axes.plot([left, left + width], [avg, avg], linestyle="--",
                          color="#000000")
            else:
                # all other stats
                value = apply_stat(stat_name, data)
                axes.bar(left, value, width, color=color)

    # xlabels
    axes.set_xticks([i + groupwidth / 2 for i in range(len(stat_names))])
    axes.set_xticklabels(stat_names)

    # axis limits
    limits = list(axes.axis())
    # ymin
    limits[2] = 0
    # xmin
    limits[0] = -(1 - groupwidth)
    # xmax
    limits[1] = len(stat_names) + (1 - groupwidth)
    axes.axis(limits)

    # legend
    colorpool = (colors + defines.colors)[::-1]
    legend = []
    for name, data in datas:
        color = colorpool.pop()
        legend.append((Patch(color=color), name))
    if legend:
        args = {"loc": 0, "numpoints": 3}
        args.update(legendargs)
        axes.legend(*zip(*legend), **args)

    return fig
