# Purpose: Reusable Zhoulab plot styling, physical geometry, annotations, and export.
# Input: Caller-provided data, errors, labels, Matplotlib axes, and output paths.
# Output: Plot artists or exported files only when the corresponding function is called.
# This helper is self-contained within the skill folder.
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.transforms import Bbox

FONT_PT = 9

AX_H_IN = 1.60
LINE_X_PADDING = 0.25
LINE_X_UNIT_IN = AX_H_IN / 4.5
PETH_AX_WIDTH_IN = 2.162162162162162

BAR_WIDTH = 0.45

BAR_GAP = 0.225

BAR_STEP = BAR_WIDTH + BAR_GAP
X_UNIT_IN = 0.5343228200371056
VIOLIN_X_UNIT_IN = X_UNIT_IN
VIOLIN_X_PADDING = .60
VIOLIN_WIDTH = BAR_WIDTH

EXPORT_PAD_IN = 0.04

DEFAULT_COLORS = ["#ca0020", "#0571b0", "#7b3294", "#f4a582", "#448c70", "#666666"]


def set_plot_style():
    font_manager.findfont("Arial", fallback_to_default=False)
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": FONT_PT,
            "font.weight": "normal",
            "axes.labelweight": "normal",
            "axes.titleweight": "normal",
            "axes.labelsize": FONT_PT,
            "axes.titlesize": FONT_PT,
            "xtick.labelsize": FONT_PT,
            "ytick.labelsize": FONT_PT,
            "legend.fontsize": FONT_PT,
            "axes.linewidth": 0.6,
            "patch.linewidth": 0.75,
            "lines.linewidth": 0.75,
            "lines.markersize": 3,
            "xtick.major.pad": 3, "ytick.major.pad": 3,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 2,
            "ytick.major.size": 2,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "legend.frameon": False,
            "legend.fancybox": False,
            "legend.shadow": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.transparent": True,
            "savefig.bbox": None,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "mathtext.fontset": "custom",
            "mathtext.rm": "Arial",
            "mathtext.it": "Arial:italic",
            "mathtext.bf": "Arial:bold",
        }
    )


def physical_panel(
    axis_width_in, margins=(0.52, 0.08, 0.46, 0.20), axis_height_in=AX_H_IN
):
    left, right, bottom, top = margins
    total_w = left + axis_width_in + right
    total_h = bottom + axis_height_in + top
    fig = plt.figure(figsize=(total_w, total_h))
    ax = fig.add_axes(
        [
            left / total_w,
            bottom / total_h,
            axis_width_in / total_w,
            axis_height_in / total_h,
        ]
    )
    ax.yaxis.labelpad = 2
    ax.tick_params(width=0.6, length=2, pad=3)
    ax.grid(False)
    return fig, ax


def line_panel(x, margins=(0.52, 0.08, 0.46, 0.20)):
    """Keep one ordered/numeric x unit at 9.0311 mm and 0.25-unit end padding."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if not len(x):
        raise ValueError("Need at least one finite x coordinate")
    xlim = (float(x.min())-LINE_X_PADDING, float(x.max())+LINE_X_PADDING)
    fig, ax = physical_panel(LINE_X_UNIT_IN*(xlim[1]-xlim[0]), margins)
    ax.set_xlim(*xlim)
    return fig, ax


def bar_panel(positions, margins=(0.52, 0.08, 0.46, 0.20)):
    positions = np.asarray(positions, dtype=float)
    if positions.ndim != 1 or not len(positions) or not np.isfinite(positions).all():
        raise ValueError("Need finite 1D bar positions")
    xlim = (float(positions.min()) - 0.6, float(positions.max()) + 0.6)
    fig, ax = physical_panel(X_UNIT_IN * (xlim[1] - xlim[0]), margins)
    ax.set_xlim(*xlim)
    return fig, ax


def violin_panel(positions, margins=(0.52, 0.08, 0.46, 0.20)):
    """Share the matching bar chart's positions, physical scale and data-axis ratio."""
    return bar_panel(positions, margins=margins)


def draw_violin(ax, position, values, color, *, mean=None, ci=None, marker="o", seed=0):
    """Draw raw points, Scott KDE and optional precomputed mean/CI; fit no model."""
    values = np.asarray(values, dtype=float).ravel()
    values = values[np.isfinite(values)]
    if ci is not None and mean is None:
        raise ValueError("A supplied interval needs its precomputed mean")
    mean = None if mean is None else float(mean)
    error = None
    if ci is not None:
        bounds = np.asarray(ci, dtype=float)
        if bounds.shape != (2,):
            raise ValueError("ci must contain the lower and upper endpoints")
        if mean is not None and np.isfinite(mean) and np.isfinite(bounds).all():
            if not bounds[0] <= mean <= bounds[1]:
                raise ValueError("Interval endpoints must bracket the supplied mean")
            error = np.array([[mean-bounds[0]], [bounds[1]-mean]])
    density_artists = []
    jitter = np.zeros(len(values))
    if len(values) > 1 and np.ptp(values) > np.finfo(float).eps * max(1., float(np.max(np.abs(values)))):
        from scipy.stats import gaussian_kde
        grid = np.linspace(values.min(), values.max(), 200)
        density = gaussian_kde(values, bw_method="scott")(grid)
        half = (VIOLIN_WIDTH / 2) * density / density.max()
        density_artists.append(ax.fill_betweenx(
            grid, position-half, position+half, color=color, alpha=.34, linewidth=0, zorder=1
        ))
        density_artists.extend(ax.plot(position-half, grid, color=color, linewidth=.75, zorder=1))
        density_artists.extend(ax.plot(position+half, grid, color=color, linewidth=.75, zorder=1))
        jitter = np.random.default_rng(seed).uniform(-.85, .85, len(values)) * np.interp(values, grid, half)
    points = ax.scatter(
        position+jitter, values, s=6, color=color, alpha=.8, marker=marker,
        linewidths=.5 if marker in ("x", "+", "1", "2", "3", "4", "|", "_") else 0,
        zorder=2,
    )
    summary = None
    if mean is not None and np.isfinite(mean):
        summary = ax.errorbar(
            position, mean, yerr=error, fmt="o", markersize=4,
            markerfacecolor="white", markeredgecolor="#555555", markeredgewidth=.6,
            color="#555555", elinewidth=.75, capsize=2, capthick=.75, zorder=4,
        )
    return {"density": density_artists, "points": points, "summary": summary}


def animal_offsets(n):
    return np.linspace(-0.12, 0.12, n) if n > 1 else np.zeros(n)


def draw_bar(ax, position, mean, error, color, animal_values=None):
    if not np.isfinite(mean):
        return
    ax.bar(
        position,
        mean,
        width=BAR_WIDTH,
        color=matplotlib.colors.to_rgba(color, .34),
        edgecolor=color,
        linewidth=0.75,
        zorder=2,
    )
    if error is not None and np.isfinite(error):
        ax.errorbar(
            position,
            mean,
            yerr=error,
            fmt="none",
            color=color,
            elinewidth=0.75,
            capsize=2,
            capthick=0.75,
            zorder=3,
        )
    if animal_values is not None:
        values = np.asarray(animal_values, dtype=float)
        offsets = animal_offsets(len(values))
        valid = np.isfinite(values)
        ax.scatter(
            position + offsets[valid],
            values[valid],
            marker="x",
            s=12,
            color=color,
            linewidths=0.5,
            zorder=4,
        )


def draw_animal_paths(ax, positions, values_by_animal):
    positions = np.asarray(positions, dtype=float)
    values = np.asarray(values_by_animal, dtype=float)
    if values.ndim != 2 or values.shape[1] != len(positions):
        raise ValueError("Need animals x conditions with stable identities")
    for offset, row in zip(animal_offsets(len(values)), values):
        ax.plot(
            positions + offset, row, color="#999999", linewidth=0.5, alpha=0.6, zorder=3
        )


def draw_error_line(
    ax, x, mean, error, color, label, marker="o", linestyle="-", marker_face=None
):
    x = np.asarray(x, dtype=float)
    mean = np.asarray(mean, dtype=float)
    ax.plot(
        x,
        mean,
        color=color,
        label=label,
        linewidth=0.75,
        marker=marker,
        markersize=3,
        markeredgewidth=0.6,
        markerfacecolor=color if marker_face is None else marker_face,
        linestyle=linestyle,
        zorder=3,
    )
    if error is not None:
        error = np.asarray(error, dtype=float)
        if error.ndim == 1 and error.shape == mean.shape:
            valid = np.isfinite(x) & np.isfinite(mean) & np.isfinite(error)
            yerr = error[valid]
        elif error.shape == (2, len(mean)):
            valid = np.isfinite(x) & np.isfinite(mean) & np.isfinite(error).all(axis=0)
            yerr = error[:, valid]
        else:
            raise ValueError("Error must be length n or 2 x n")
        if valid.any():
            ax.errorbar(
                x[valid],
                mean[valid],
                yerr=yerr,
                fmt="none",
                color=color,
                elinewidth=0.75,
                capsize=0,
                zorder=2,
            )


def draw_event_profile(
    ax, times, mean, error, color, label, linestyle="-", bounds=None
):
    times = np.asarray(times, dtype=float)
    mean = np.asarray(mean, dtype=float)
    ax.plot(
        times,
        mean,
        color=color,
        label=label,
        linewidth=0.75,
        linestyle=linestyle,
        zorder=3,
    )
    if bounds is not None:
        lower, upper = (np.asarray(v, dtype=float) for v in bounds)
    elif error is not None:
        error = np.asarray(error, dtype=float)
        lower, upper = mean - error, mean + error
    else:
        return
    valid = (
        np.isfinite(times) & np.isfinite(mean) & np.isfinite(lower) & np.isfinite(upper)
    )
    ax.fill_between(
        times, lower, upper, where=valid, color=color, alpha=0.18, linewidth=0, zorder=2
    )


def event_background(ax, window=None):
    if window is not None:
        ax.axvspan(*window, color="#eeeeee", linewidth=0, zorder=0)
    ax.axvline(0, color="#8c8c8c", linewidth=0.55, linestyle=":", zorder=1)


def draw_forest(ax, estimates, lower, upper, rows, color="#0571b0"):
    estimates, lower, upper, rows = (
        np.asarray(v, dtype=float) for v in (estimates, lower, upper, rows)
    )
    valid = (
        np.isfinite(estimates)
        & np.isfinite(lower)
        & np.isfinite(upper)
        & np.isfinite(rows)
    )
    ax.errorbar(
        estimates[valid],
        rows[valid],
        xerr=np.vstack(
            [estimates[valid] - lower[valid], upper[valid] - estimates[valid]]
        ),
        fmt="o",
        markersize=3,
        color=color,
        elinewidth=0.75,
        capsize=2,
        capthick=0.75,
    )
    ax.axvline(0, color="#8c8c8c", linewidth=0.6, linestyle=":", zorder=0)


def add_comparison_brackets(ax, comparisons, envelope_by_x):
    """comparisons: (left_x, right_x, real_test_label), ordered bottom to top.
    envelope_by_x: x -> finite animal values and mean+error, including intermediate bars.
    Raise if annotations do not fit; caller adjusts the common y range and retries.
    """
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    axes_box = ax.get_window_extent(renderer)
    px_per_pt = fig.dpi / 72
    gap_px, hook_px = 1.5 * px_per_pt, 2 * px_per_pt
    half_line_px = 0.3 * px_per_pt
    marker_radius_px = (np.sqrt(12) / 2 + 0.5 / 2) * px_per_pt
    previous_top = -np.inf
    artists = []
    try:
        for x1, x2, label in comparisons:
            if x1 > x2:
                x1, x2 = x2, x1
            peaks = []
            for position, values in envelope_by_x.items():
                if x1 <= position <= x2:
                    values = np.asarray(values, dtype=float).ravel()
                    values = values[np.isfinite(values)]
                    if len(values):
                        pixels = ax.transData.transform(
                            np.column_stack([np.full(len(values), position), values])
                        )[:, 1]
                        pixels = pixels[np.isfinite(pixels)]
                        if len(pixels):
                            peaks.append(float(pixels.max()))
            if not peaks:
                raise ValueError("Comparison has no finite data envelope")
            foot_px = max(
                max(peaks) + marker_radius_px + gap_px + half_line_px,
                previous_top + gap_px + half_line_px,
            )
            line_px = foot_px + hook_px
            foot = (foot_px - axes_box.y0) / axes_box.height
            line = (line_px - axes_box.y0) / axes_box.height
            (drawn,) = ax.plot(
                [x1, x1, x2, x2],
                [foot, line, line, foot],
                color="black",
                linewidth=0.6,
                transform=ax.get_xaxis_transform(),
                clip_on=True,
                zorder=10,
            )
            artists.append(drawn)
            text_bottom = (
                line_px + half_line_px + gap_px - axes_box.y0
            ) / axes_box.height
            text = ax.text(
                (x1 + x2) / 2,
                text_bottom,
                str(label),
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="normal",
                clip_on=True,
                zorder=10,
                gid="significance",
            )
            artists.append(text)
            box = text.get_window_extent(renderer)
            if box.width > axes_box.width-2*gap_px and ", " in str(label):
                text.set_text(str(label).replace(", ", ",\n", 1))
                box = text.get_window_extent(renderer)
            if box.width <= axes_box.width-2*gap_px:
                shift = max(axes_box.x0+gap_px-box.x0, 0)
                shift -= max(box.x1+shift-(axes_box.x1-gap_px), 0)
                if shift:
                    text.set_x(ax.transData.inverted().transform(
                        (ax.transData.transform((text.get_position()[0],0))[0]+shift,0))[0])
                    box = text.get_window_extent(renderer)
            if (
                box.x0 < axes_box.x0
                or box.x1 > axes_box.x1
                or foot_px - half_line_px < axes_box.y0
                or box.y1 + gap_px > axes_box.y1
            ):
                raise ValueError(
                    "Need more axis headroom/width for inside-axis comparisons"
                )
            previous_top = box.y1
    except Exception:
        for artist in artists:
            artist.remove()
        raise
    return artists


def content_bbox(fig, dpi):
    fig.set_dpi(dpi)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    extents = [fig.get_tightbbox(renderer)]
    texts = list(fig.texts)
    for ax in fig.axes:
        texts.extend([ax.xaxis.label, ax.yaxis.label, ax.title])
        texts.extend(ax.texts)
    for artist in texts:
        if artist.get_visible() and artist.get_text():
            extent = artist.get_window_extent(renderer).transformed(
                fig.dpi_scale_trans.inverted()
            )
            if np.isfinite(extent.extents).all():
                extents.append(extent)
    return Bbox.union(extents).padded(EXPORT_PAD_IN)


def export_plot(fig, outputs, png_dpi=600):
    bbox = content_bbox(fig, png_dpi)
    main = fig.axes[0]
    position = main.get_position()
    left = (position.x0*fig.get_figwidth()-bbox.x0)*72
    top = (bbox.y1-position.y1*fig.get_figheight())*72
    width = position.width*fig.get_figwidth()*72
    height = position.height*fig.get_figheight()*72
    geometry = "zhoulab-axis:" + ",".join(f"{v:.9f}" for v in (left,top,left+width,top+height))
    for output in outputs:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        options = dict(bbox_inches=bbox, pad_inches=0, transparent=True)
        if output.suffix.lower()==".png":
            options["dpi"] = png_dpi
        elif output.suffix.lower()==".pdf":
            options["metadata"] = {"Keywords": geometry}
        fig.savefig(output, **options)
    return bbox


def format_test_label(p=None, *, log_p=None, multiline=False):
    """Display the already selected raw/adjusted P; log_p can preserve numerical underflow."""
    if log_p is None:
        if p is None or not np.isfinite(p):
            return ""
        p = float(p)
        if not 0 < p <= 1:
            raise ValueError("A displayed zero P needs a finite log P from the same test")
        log_p = float(np.log(p))
    if not np.isfinite(log_p) or log_p > 1e-12:
        raise ValueError("Need a finite log probability no greater than zero")
    star = "***" if log_p < np.log(.001) else "**" if log_p < np.log(.01) else "*" if log_p < np.log(.05) else "ns"
    if log_p < np.log(.0001):
        exponent = int(np.floor(log_p/np.log(10.)))
        mantissa = float(np.exp(log_p-exponent*np.log(10.)))
        rounded = float(f"{mantissa:.2f}")
        if rounded >= 10:
            rounded, exponent = 1., exponent+1
        number = f"{rounded:.2f}" + r"$\times10^{" + str(exponent) + "}$"
    else:
        number = f"{np.exp(log_p):#.3g}"
    separator = ",\n" if multiline else ", "
    return star + separator + r"$\mathit{P}$=" + number


def place_point_test_labels(ax, labels, envelope_by_x):
    """Stagger numeric labels above data while retaining their original x coordinates."""
    fig=ax.figure;fig.canvas.draw()
    renderer=fig.canvas.get_renderer();bounds=ax.get_window_extent(renderer)
    gap=1.5*fig.dpi/72;texts=[];rows=[]
    try:
        for position,label in labels:
            text=ax.text(position,.98,label,transform=ax.get_xaxis_transform(),
                         ha="center",va="top",fontsize=FONT_PT,gid="significance",zorder=12)
            texts.append(text);box=text.get_window_extent(renderer)
            if box.width>bounds.width-2*gap:
                text.set_text(str(label).replace(", ",",\n",1));box=text.get_window_extent(renderer)
            if box.width>bounds.width-2*gap:
                raise ValueError("Numeric test text exceeds the fixed axis width")
            anchor=float(ax.transData.transform((position,0))[0])
            center=float(np.clip(anchor,bounds.x0+gap+box.width/2,bounds.x1-gap-box.width/2))
            if abs(center-anchor)>3*fig.dpi/72:
                raise ValueError("Need extra horizontal margin for anchored test labels")
            interval=(center-box.width/2,center+box.width/2)
            for level,row in enumerate(rows):
                if all(interval[1]+gap<=old[0] or interval[0]>=old[1]+gap for old in row):
                    row.append(interval);break
            else:
                level=len(rows);rows.append([interval])
            text._point_test_layout=(level,center,box.height,position)
        heights=[max(t._point_test_layout[2] for t in texts if t._point_test_layout[0]==level) for level in range(len(rows))]
        for text in texts:
            level,center,_,position=text._point_test_layout
            top=bounds.y1-gap-sum(heights[:level])-level*gap
            text.set_transform(ax.transAxes)
            text.set_position(((center-bounds.x0)/bounds.width,(top-bounds.y0)/bounds.height))
        lowest=min(t.get_window_extent(renderer).y0 for t in texts)
        values=np.concatenate([np.asarray(v,dtype=float).ravel() for v in envelope_by_x.values()])
        values=values[np.isfinite(values)]
        peak=float(ax.transData.transform((0,float(values.max())))[1])
        if lowest-gap<peak+(np.sqrt(12)/2+.25)*fig.dpi/72:
            raise ValueError("Need more y headroom for numeric test labels")
    except Exception:
        for text in texts:text.remove()
        raise
    return texts


def place_test_labels(ax, labels, stagger=False):
    """Keep labels inside the existing axis; separate neighboring zero tests."""
    fig = ax.figure
    artists = []
    for index, (position, label) in enumerate(labels):
        row = index % 2 if stagger else 0
        artist = ax.text(position, .955 - .15 * row, label,
                         transform=ax.get_xaxis_transform(), ha="center", va="top",
                         fontsize=FONT_PT, gid="significance")
        artists.append((row, artist))
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = ax.get_window_extent(renderer)
    gap = 1.5 * fig.dpi / 72
    for row in sorted({row for row, _ in artists}):
        texts = [artist for level, artist in artists if level == row]
        boxes = [artist.get_window_extent(renderer) for artist in texts]
        widths = [box.width for box in boxes]
        lefts = []
        for box in boxes:
            left = max(bounds.x0 + gap, box.x0)
            if lefts:
                left = max(left, lefts[-1] + widths[len(lefts)-1] + gap)
            lefts.append(left)
        overflow = max(0, lefts[-1] + widths[-1] - (bounds.x1-gap))
        lefts = [left-overflow for left in lefts]
        if lefts[0] < bounds.x0 + gap - .01:
            raise ValueError("Significance labels do not fit the existing axis width")
        for text, left, width in zip(texts, lefts, widths):
            x = (left + width/2 - bounds.x0) / bounds.width
            y = text.get_position()[1]
            text.set_transform(ax.transAxes)
            text.set_position((x, y))
    return [artist for _, artist in artists]


def check_test_labels(fig):
    """Check annotation bounds and collisions at the current physical font size."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        labels = [text for text in ax.texts if text.get_gid() == "significance"]
        bounds = ax.get_window_extent(renderer)
        boxes = [text.get_window_extent(renderer) for text in labels]
        for index, box in enumerate(boxes):
            if not bounds.contains(box.x0, box.y0) or not bounds.contains(box.x1, box.y1):
                raise ValueError("Significance annotation exceeds the existing axis")
            if any(box.overlaps(other) for other in boxes[index+1:]):
                raise ValueError("Significance annotations overlap")
            legend = ax.get_legend()
            if legend is not None and box.overlaps(legend.get_window_extent(renderer)):
                raise ValueError("Significance annotation overlaps the legend")
