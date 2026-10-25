# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 11:45:38 2026

@author: ronne
"""



import os
import glob
import numpy as np
import pandas as pd
from scipy.io import loadmat


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Directory containing the source .mat files and directory for the output CSVs.
INPUT_FOLDER = 'data/cast_experiment/mat'
OUTPUT_FOLDER = 'data/cast_experiment/csv'

# Mapping between the variable names stored in the .mat files and the column
# labels used in the target CSV. The dictionary order defines the column order
# in the exported file.
COLUMN_MAP = {
    'YawAngle':       'yaw angle',
    'RollAngle':      'roll angle',
    'PitchAngle':     'pitch angle',
    'SteerAngle':     'steer angle',
    'YawRate':        'yaw rate',
    'RollRate':       'roll rate',
    'PitchRate':      'pitch rate',
    'ForwardSpeed':   'speed',
    'SteerRate':      'steer rate',
    'PullForce':      'seat force Fy',
    'RollTorqueT4':   'roll torque T4',
    'PedalTorqueT6':  'pedal torque T6',
    'SteerTorque':    'steer torque T7',
}

# Complete list of variables to be extracted from each .mat file. This set
# includes the variables mapped to the reference CSV schema as well as the
# supplementary variables retained in addition to it.
COLUMNS_TO_KEEP = [
    'ForwardSpeed', 'YawAngle', 'PullForce', 'Rider', 'Maneuver',
    'SteerRate', 'RollRate', 'RearWheelRate', 'SteerTorque',
    'YawRate', 'SteerAngle', 'RollAngle', 'NISampleRate', 'Duration',
    'PitchAngle',
]


# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------
# Ensure the output directory exists.
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Enumerate and sort the source files for reproducible processing order.
mat_files = sorted(glob.glob(os.path.join(INPUT_FOLDER, '*.mat')))

for filepath in mat_files:
    filename = os.path.basename(filepath)
    print(f"Processing {filename} ...")

    # Load the file. The classic format is attempted first; the HDF5 backend
    # is used as a fallback for files written in the MATLAB 7.3 format.
    try:
        data = loadmat(filepath, simplify_cells=True)
    except NotImplementedError:
        import h5py
        with h5py.File(filepath, 'r') as f:
            data = {key: np.array(f[key]) for key in f.keys()}

    # Retrieve the sampling rate, defaulting to 200 Hz when not recorded.
    sample_rate = data.get('NISampleRate', 200)
    if isinstance(sample_rate, np.ndarray):
        sample_rate = float(sample_rate.flatten()[0])

    # Retrieve the recorded duration, when available.
    if 'Duration' in data:
        duration = float(np.array(data['Duration']).flatten()[0])
    else:
        duration = None

    # Assemble the output table.
    df = pd.DataFrame()

    # Determine the number of samples from the first available signal.
    n_samples = None
    for col in COLUMNS_TO_KEEP:
        if col in data:
            arr = np.array(data[col]).flatten()
            if n_samples is None:
                n_samples = len(arr)
            break

    if n_samples is None:
        print(f"  [warning] no signal found, file skipped.")
        continue

    # Build the time vector. When the duration is known, samples are spaced
    # uniformly over the recorded interval; otherwise the sampling rate is used.
    if duration is not None:
        time_vec = np.linspace(0, duration, n_samples)
    else:
        time_vec = np.arange(n_samples) / sample_rate

    df['time'] = time_vec

    # Add the variables mapped to the reference CSV schema, in the prescribed
    # order.
    for mat_col, csv_col in COLUMN_MAP.items():
        if mat_col in data:
            df[csv_col] = np.array(data[mat_col]).flatten()

    # Append the supplementary variables that are present in the .mat file but
    # absent from the reference CSV schema.
    extra_cols = []
    for col in COLUMNS_TO_KEEP:
        if col in data and col not in COLUMN_MAP:
            extra_cols.append(col)
            val = data[col]
            df[col] = val

    # Reorder the columns: reference CSV schema first, supplementary variables
    # afterwards.
    csv_order = ['time'] + list(COLUMN_MAP.values())
    ordered_cols = [c for c in csv_order if c in df.columns] + extra_cols
    df = df[ordered_cols]

    # Export as a tab-delimited CSV, matching the layout of the reference file.
    out_path = os.path.join(OUTPUT_FOLDER, filename.replace('.mat', '.csv'))
    df.to_csv(out_path, sep=';', index=True, index_label='')
    print(f"  [saved] {out_path} ({len(df)} rows, {len(ordered_cols)} columns)")

print(f"\nDone. {len(mat_files)} files processed -> {OUTPUT_FOLDER}")