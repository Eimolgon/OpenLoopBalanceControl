# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 14:04:02 2026

@author: ronne
"""



import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.interpolate import CubicSpline

from IPython.display import HTML

from matplotlib.animation import FuncAnimation, HTMLWriter, PillowWriter, FFMpegWriter



from symbrim.utilities.plotting import Plotter
from scipy.signal import butter, filtfilt

import os

from datetime import datetime

def make_new_results_folder(loc, suffixe=""):
    """
    make_new_results_folder


    """
    os.makedirs('results', exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    file_name = loc + f"{timestamp}/"
    if suffixe:
        file_name += f"_{suffixe}"
    
    try:
        os.makedirs(file_name, exist_ok=True)
        path = os.path.abspath(file_name)
        print(f"File generated : {path}")
        return file_name
    except OSError as e:
        print(f"Error when generating file : {e}")
        return None

def animate_solution(t_simu, x_opt, r_opt, bicycle, x, r, p, ani_name):

    # Create some functions to interpolate the results.
    x_eval = CubicSpline(t_simu, x_opt)
    r_eval = CubicSpline(t_simu, r_opt)
    # dis_eval = CubicSpline(t_simu, dis.T)
    # max_disturbance = dis.max()

    # Plot the initial configuration of the model
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(8, 8))
    plotter = Plotter.from_model(bicycle, ax=ax)
    # plotter.add_vector(
    #     disturbance * bicycle.rear_frame.wheel_hub.axis / max_disturbance,
    #     bicycle.rear_frame.saddle.point,
    #     name="disturbance",
    #     color="r",
    # )
    # plotter.lambdify_system((x, r, disturbance, param))
    # plotter.evaluate_system(x_eval(0.0), r_eval(0.0),dis[0], param_vals)
    param, param_vals = zip(*p.items())
    plotter.lambdify_system((x, r, param))
    plotter.evaluate_system(x_eval(0.0), r_eval(0.0), param_vals)
    plotter.plot()
    X, Y = np.meshgrid(np.arange(-1, 10, 0.5), np.arange(-1, 3, 0.5))
    ax.plot_wireframe(X, Y, np.zeros_like(X), color="k", alpha=0.3, rstride=1, cstride=1)
    ax.invert_zaxis()
    ax.invert_yaxis()
    ax.set_xlim(X.min(), X.max())
    ax.set_ylim(Y.min(), Y.max())
    ax.view_init(19, 14)
    ax.set_aspect("equal")
    ax.axis("off")

    fps = 30
    # ani = plotter.animate(
    #     lambda ti: (x_eval(ti), r_eval(ti), dis_eval(ti), param_vals), frames=np.arange(0, t_simu[-1], 1 / fps), blit=False
    # )

    ani = plotter.animate(
        lambda ti: (x_eval(ti), r_eval(ti), param_vals), frames=np.arange(0, t_simu[-1], 1 / fps), blit=False
    )

    display(HTML(ani.to_jshtml(fps=fps)))

    html_writer = HTMLWriter()
    ani.save(ani_name if ani_name.endswith(".html") else ani_name + ".html", writer=html_writer)



def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def butter_lowpass_filter(data, highcut, fs, order=4):
    nyq = 0.5 * fs
    high = highcut / nyq
    b, a = butter(order, high, btype='low')
    return filtfilt(b, a, data)



def RMSE(x, x_meas):
    """
    Computes RMSE to assess optimization performance

    Parameters
    ----------
    x : numpy array
        ground truth.
    x_meas : numpy array
        signal.

    Returns
    -------
    RMSE

    """

    res = np.mean((x_meas - x)**2)
    res = np.sqrt(res)

    return(res)

import matplotlib as mpl

def plot_BA(df1, df2, col1, col2, label1, label2):
    """
    Bland-Altman plot with academic LaTeX styling.

    Parameters
    ----------
    df1, df2 : DataFrame
        Two data sources to compare.
    col1, col2 : str
        Column names to compare.
    ax : matplotlib Axes, optional
        Target axes (creates one if None).

    Returns
    -------
    ax : matplotlib Axes
    """

    # ── Data ──────────────────────────────────────────────────────────
    diff = df1[col1] - df2[col2]
    mean = (df1[col1] + df2[col2]) / 2

    diff_mean = np.mean(diff)
    diff_std = np.std(diff, ddof=1)          # sample std
    loa_upper = diff_mean + 1.96 * diff_std
    loa_lower = diff_mean - 1.96 * diff_std

    # ── Global style (LaTeX-like) ─────────────────────────────────────
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Computer Modern", "DejaVu Serif"],
        "mathtext.fontset": "cm",             # Computer Modern for math
        "axes.linewidth": 0.8,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 8,
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
    })

    # ── Plot ──────────────────────────────────────────────────────────

    fig, ax = plt.subplots(figsize=(5,3))

    # Data points
    ax.scatter(mean, diff, s=13, alpha=0.5,
               edgecolors="black", linewidths=0.4,
               facecolors="steelblue", zorder=3)

    # Mean difference (solid)
    ax.axhline(diff_mean, color="black", linewidth=1.0,
               linestyle="-", zorder=2,
               label=r"$\bar{d} = %.3f$" % diff_mean)

    # Limits of agreement (dashed)
    ax.axhline(loa_upper, color="black", linewidth=0.8,
               linestyle="--", zorder=2,
               label=r"$\bar{d}+1.96\,s = %.3f$" % loa_upper)
    ax.axhline(loa_lower, color="black", linewidth=0.8,
               linestyle="--", zorder=2,
               label=r"$\bar{d}-1.96\,s = %.3f$" % loa_lower)

    # ── Annotations (right margin) ────────────────────────────────────
    x_max = mean.max()
    x_range = mean.max() - mean.min()
    offset = 0.18 * x_range

    ax.annotate(r"$\bar{d}$", xy=(x_max + offset, diff_mean),
                fontsize=9, va="center", ha="left")
    ax.annotate(r"$+1.96\,s$", xy=(x_max + offset, loa_upper),
                fontsize=9, va="center", ha="left")
    ax.annotate(r"$-1.96\,s$", xy=(x_max + offset, loa_lower),
                fontsize=9, va="center", ha="left")

    # ── Axes & layout ─────────────────────────────────────────────────
    ax.set_xlabel(f"{label1}", fontsize=11)
    ax.set_ylabel(f"{label2}", fontsize=11)
    ax.set_xlim(mean.min() - 0.05 * x_range, x_max + 0.18 * x_range)

    # Spines: keep left & bottom only (LaTeX minimalism)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Tick direction inward
    ax.tick_params(direction="in", length=4, width=0.7)

    # Legend outside or inside top-right, no frame
    ax.legend(bbox_to_anchor=(1.1, 1.05), frameon=False, handlelength=1.8)

    ax.grid(axis="y", linestyle=":", linewidth=0.4, alpha=0.5)
    
    plt.tight_layout()

    return ax, diff_mean, diff_std
