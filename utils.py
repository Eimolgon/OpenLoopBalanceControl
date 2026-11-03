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


from scipy import signal
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


def NRMSE_and_RMSE(df_opt, df_meas, sig, ti, tf, N_sampling):
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
    x_meas = df_meas.loc[(df_meas['time']>ti) & (df_meas['time']<tf), sig]
    x_meas = x_meas[::N_sampling].to_numpy()
    x_opt = df_opt[sig].to_numpy()
    
    std_exp = np.std(x_meas)
    std_opt = np.std(x_opt)
    
    mean_exp = np.mean(x_meas)
    mean_opt = np.mean(x_opt)


    
    diff = x_meas - x_opt
    res = np.mean((diff)**2)
    rmse = np.sqrt(res)
    nrmse = rmse/std_exp
    

    correlation = signal.correlate((x_meas-mean_exp)/std_exp, (x_opt-mean_opt)/std_opt, mode="full")/min(len(x_meas),len(x_opt))
    plt.plot(correlation)
    R2_max = np.max(correlation)**2
    lags = signal.correlation_lags(x_meas.size, x_opt.size, mode="full")
    fs = 1/np.mean(np.diff(df_meas['time'][::N_sampling]))
    lag = lags[np.argmax(correlation)]/fs
    
    


    return(rmse, nrmse, R2_max, lag)



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


    
    diff = x_meas - x
    res = np.mean((diff)**2)
    rmse = np.sqrt(res)

    return(rmse)

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



def generate_txt(n, bike):
    """
    Generate a .txt benchmark file for bike n.

    Path: Synth_bike_n/Parameters/Synth_bike_nBenchmark.txt
    """
    key_map = {
        'lambda': 'lam',
        'c': 'c',
        'm_H': 'mH',
        'x_H': 'xH',
        'z_H': 'zH',
        'I_Hxx': 'IHxx',
        'I_Hzz': 'IHzz',
        'I_Hxz': 'IHxz',
        'm_R': 'mR',
        'r_R': 'rR',
        'I_Rxx': 'IRxx',
        'I_Ryy': 'IRyy',
        'm_F': 'mF',
        'r_F': 'rF',
        'I_Fxx': 'IFxx',
        'I_Fyy': 'IFyy',
        'm_B': 'mB',
        'x_B': 'xB',
        'z_B': 'zB',
        'I_Bxx': 'IBxx',
        'I_Bzz': 'IBzz',
        'I_Bxz': 'IBxz',
        'w': 'w',
    }

    fixed_params = {'g': 9.81}

    output_order = [
        'IBxx', 'IBxz', 'IByy', 'IBzz',
        'IFxx', 'IFyy',
        'IHxx', 'IHxz', 'IHyy', 'IHzz',
        'IRxx', 'IRyy',
        'c', 'g', 'lam',
        'mB', 'mF', 'mH', 'mR',
        'rF', 'rR',
        'w',
        'xB', 'xH', 'zB', 'zH',
    ]

    inv_map = {v: k for k, v in key_map.items()}

    lines = []
    for tkt_name in output_order:
        if tkt_name in fixed_params:
            value = fixed_params[tkt_name]
        elif tkt_name in inv_map:
            value = bike.get(inv_map[tkt_name], 0.0)
        else:
            value = 0.0
        lines.append(f"{tkt_name} = {value}+/-0.0")

    # Build path: data/bicycles/Synth_bike_n/Parameters/Synth_bike_nBenchmark.txt
    folder = f"data/bicycles/Synth_bike_{n}"
    filepath = os.path.join(folder, "Parameters", f"Synth_bike_{n}Benchmark.txt")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines) + '\n')
        
        
def apply_lag(x, lag_samples, fill=0):
    """
    Shift a signal by `lag_samples` samples.
    
    Parameters
    ----------
    x : array-like
        Signal to shift.
    lag_samples : int
        Shift in samples.
        Positive : signal delayed (shifted to the right).
        Negative : signal advanced (shifted to the left).
    fill : float
        Fill value at the edges (default: NaN).
    
    Returns
    -------
    np.ndarray
    """
    x = np.asarray(x, dtype=float)
    out = np.full_like(x, fill)
    
    if lag_samples > 0:
        out[lag_samples:] = x[:-lag_samples]
    elif lag_samples < 0:
        out[:lag_samples] = x[-lag_samples:]
    else:
        out[:] = x
    
    return out


def solution_to_dict(solution, config, len_x, len_r):
    
    col_q = ['q1','q2','q3','q4','q5','q6','q7','q8']
    col_u = ['u1','u2','u3','u4','u5','u6','u7','u8']
    
    if config['Fy'] == False:
        col_r = ['T6','T7']
    if config['Fy'] == True:
        col_r = ['F_y','T6','T7']
    if config['roll_control'] == True:
        col_r = ['T6','T7','T4','Fy','Fz']
        
    sol_reshaped = solution.reshape(len_x + len_r, -1)
    sol_dict = {}
        
    for k,col in enumerate(col_q+col_u+col_r):
        
        sol_dict[col] = sol_reshaped[k]
        
    return(sol_dict)
    
def solution_dict_to_x0(sol_dict):
    
    NUM_NODES = sol_dict[list(sol_dict.keys())[0]].shape[0]
    n_keys = len(list(sol_dict.keys()))
    x0 = np.empty((n_keys, NUM_NODES))
        
    for k, key in enumerate(sol_dict.keys()):
        x0[k, :]=sol_dict[key]
    
    return(x0)



def sliding_windows(signals: dict[str, np.ndarray], N: int, M: int) -> dict[int, dict[str, np.ndarray]]:
    """
    Applies sliding windows to multiple signals simultaneously.
    If the remaining points at the end would form an incomplete window,
    they are appended to the last complete window instead.

    Parameters
    ----------
    signals : dict {signal_name: array}
    N       : window size
    M       : overlap between consecutive windows

    Returns
    -------
    dict[int, dict[str, np.ndarray]]
        Key = window index, value = dict {signal_name: windowed sub-signal}
    """
    step = N - M
    if step <= 0:
        raise ValueError("Step (N - M) must be strictly positive.")

    length = len(next(iter(signals.values())))
    result = {}
    window_id = 0
    start = 0

    # Create full-size windows
    while start + N <= length:
        window = {name: sig[start:start + N] for name, sig in signals.items()}
        result[window_id] = window
        window_id += 1
        start += step

    # Remaining points: extend the last window instead of creating a short one
    if start < length and result:
        last_id = window_id - 1
        last_start = last_id * step
        result[last_id] = {name: sig[last_start:] for name, sig in signals.items()}

    return result



def recombine_windows(
    windows: dict[int, dict[str, np.ndarray]],
    M: int
) -> dict[str, np.ndarray]:
    """
    Recombines overlapping windows back into a single signal per key,
    removing the M overlapping points between consecutive windows.

    Parameters
    ----------
    windows     : dict[int, dict[str, np.ndarray]]
                  Output of sliding_windows_multi_full_last.
    M           : int, overlap size between consecutive windows.


    Returns
    -------
    dict[str, np.ndarray]
        One recombined signal per key.
    """
    if not windows:
        return {}

    keys = list(next(iter(windows.values())).keys())
    result = {key: [] for key in keys}
    

    for i, wid in enumerate(sorted(windows.keys())):
        window = windows[wid]
        
        
        for key in keys:

            result[key].append(window[key][M:-M])

    # Concatenate all slices per key
    recombined = {key: np.concatenate(result[key]) for key in keys}

    return recombined



from pathlib import Path


def _rmse(a, b):
    """RMSE rounded to 3 decimals."""
    return round(float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2))), 3)


def _plot_pair(ax, t, y_opt, y_exp, color, label_opt, label_exp, show_rmse=True):
    """Plots optimal vs experimental on the same axis with RMSE in legend."""
    if show_rmse:
        label_opt += f" — RMSE: {_rmse(y_opt, y_exp)}"
    ax.plot(t, y_opt, color=color, label=label_opt)
    ax.plot(t, y_exp, color=color, ls="--", label=label_exp)


def _style_axis(ax, title, xlabel, ylabel, xlim=None):
    """Applies consistent styling to a subplot."""
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xlim is not None:
        ax.set_xlim(xlim)
    ax.legend(bbox_to_anchor=(1.01, 1.05))


def plot_res_type_2(
    solution_dict: dict,
    x_meas_dict: dict,
    params: dict,
    config: dict,
    save: bool = False,
    path: str = ".",
    figname: str = "result",
):
    """
    Plots optimal vs experimental results for a vehicle dynamics model.

    Parameters
    ----------
    solution_dict : dict of optimal signals (q1, q2, q3, ..., u3, ..., T4, T6, T7, Fy, Fz)
    x_meas_dict   : dict of measured/experimental signals
    time_simu     : time vector
    params        : model parameters dict (must contain 'rear_wheel_r')
    config        : config dict (keys: 'steer_torque', 'roll_control', 'Fy')
    save          : if True, saves figure as SVG and PNG
    path          : output directory
    figname       : output filename stem
    """
    colors = ["b", "g", "r", "k"]
    time = x_meas_dict['time']
    xlim = (time[0], time[-1])
    
    param_str = {str(param) : value for param, value in zip(params.keys(),params.values())}
    wheel_radius = param_str["rear_wheel_r"]

    with plt.rc_context({"lines.linewidth": 1}):
        fig, axs = plt.subplots(3, 2, figsize=(18, 24), sharex=True,
                                constrained_layout=True)

        # ─── Trajectory ───────────────────────────────────────────────
        axs[0, 0].plot(solution_dict["q1"], solution_dict["q2"], label="path_opt")
        axs[0, 0].plot(x_meas_dict["q1"], x_meas_dict["q2"], ls="--", label="path_synth")
        _style_axis(axs[0, 0], "Trajectory", "x [m]", "y [m]")

        # ─── Speed ────────────────────────────────────────────────────
        u_opt = -solution_dict["u6"] * wheel_radius
        u_exp = x_meas_dict["speed"]
        _plot_pair(axs[0, 1], time, u_opt, u_exp, colors[0], "$u_{opt}$", "exp")
        _style_axis(axs[0, 1], "Speed", "time [s]", "u [m/s]", xlim)

        # ─── Angles ───────────────────────────────────────────────────
        angles = [
            ("q3",  "q3",   "\\psi",   colors[0]),
            ("q4",  "q4",  "\\phi",   colors[1]),
            ("q7",  "q7", "\\delta", colors[2]),
        ]
        for sol_key, meas_key, label, c in angles:
            opt = np.rad2deg(solution_dict[sol_key])
            exp = np.rad2deg(x_meas_dict[meas_key])
            _plot_pair(axs[1, 0], time, opt, exp, c,
                       f"${label}_{{opt}}$", f"${label}_{{meas}}$")
        _style_axis(axs[1, 0], "Angles", "time [s]", "Angles [deg]", xlim)

        # ─── Angle rates ──────────────────────────────────────────────
        angle_rates = [
            ("u3", "u3",   "\\dot{\\psi}",   colors[0]),
            ("u4", "u4",  "\\dot{\\phi}",   colors[1]),
            ("u7", "u7", "\\dot{\\delta}", colors[2]),
        ]
        for sol_key, meas_key, label, c in angle_rates:
            opt = np.rad2deg(solution_dict[sol_key])
            exp = np.rad2deg(x_meas_dict[meas_key])
            _plot_pair(axs[2, 0], time, opt, exp, c,
                       f"${label}_{{opt}}$", f"${label}_{{meas}}$")
        _style_axis(axs[2, 0], "Angle rates", "time [s]", "Angle rates [deg/s]", xlim)

        # ─── Longitudinal torque ──────────────────────────────────────
        T6_opt = solution_dict["T6"]
        T6_exp = x_meas_dict["T6"]
        _plot_pair(axs[2, 1], time, T6_opt, T6_exp, colors[0],
                   "$T_{pedal}$", "$T6_{ref}$")
        _style_axis(axs[2, 1], "Longitudinal motion torques", "time [s]", "Torque [Nm]", xlim)

        # ─── Balance control torques ──────────────────────────────────
        ax = axs[1, 1]
        has_balance_plot = False

        if config.get("steer_torque"):
            T7_opt = solution_dict["T7"]
            T7_exp = x_meas_dict["T7"]
            _plot_pair(ax, time, T7_opt, T7_exp, colors[0], "$T_7$", "$T7_{ref}$")
            has_balance_plot = True

        if config.get("roll_control"):
            roll_signals = [
                ("T4", "roll_torque_T4",  "$T4$",  "$T4_{ref}$",  colors[1]),
                ("Fy", "seat_force_Fy",   "$Fy$",  "$Fy_{ref}$",  colors[2]),
                ("Fz", "seat_force_Fz",   "$Fz$",  "$Fz_{ref}$",  colors[3]),
            ]
            for sol_key, meas_key, lbl_opt, lbl_exp, c in roll_signals:
                _plot_pair(ax, time, solution_dict[sol_key], x_meas_dict[meas_key],
                           c, lbl_opt, lbl_exp)
            has_balance_plot = True

        if config.get("Fy"):
            Fy_opt = solution_dict["Fy"]
            Fy_exp = x_meas_dict["Fy"]
            _plot_pair(ax, time, Fy_opt, Fy_exp, colors[2], "$Fy$", "$Fy_{ref}$")
            has_balance_plot = True

        if has_balance_plot:
            _style_axis(ax, "Balance control torques", "time [s]", "Torque / Force [Nm]", xlim)
        else:
            ax.set_visible(False)

        # ─── Save ─────────────────────────────────────────────────────
        if save:
            out = Path(path)
            out.mkdir(parents=True, exist_ok=True)
            fig.savefig(out / f"{figname}_1_2.svg")
            fig.savefig(out / f"{figname}_1_2.png")

        # plt.close(fig)