import numpy as np
from datetime import datetime, timedelta
import pandas as pd

# ------------------------
# Parameters for Fake Data
# ------------------------
tip_type = 'Cumulative Tips'  # (not used below since we output both)
logging_interval = 1          # in minutes (for fixed interval)
tip_mag = 0.2                 # each tip adds 0.2 mm rainfall
min_depth = 0.2               # (thresholds not applied in synthetic data)
min_duration = 0              # (thresholds not applied)

# Output file paths
out_profile_cumulative = r'C:\Users\Scott\Desktop\syn_cum.xlsx'
out_profile_fixed = r'C:\Users\Scott\Desktop\syn_fixed.xlsx'

# ------------------------
# Build Fake Timestamps and Storm IDs
# ------------------------
timestamps = []
storms = []       # storm identifier per tip
stormIDs = []     # same as storms in this simple case

# 1. Add an initial row with tip value 0 to indicate deployment time.
base_time = datetime(2022, 1, 1, 0, 0, 0)
timestamps.append(base_time)
storms.append(0)        # 0 indicates deployment
stormIDs.append(0)

# Create multiple storms with varied tip counts and longer gaps.
# We'll create 10 storms using a list of dictionaries.
storm_specs = [
    {'num_tips': 5, 'gap_days': 0},  # Storm 1 (immediately after deployment)
    {'num_tips': 3, 'gap_days': 2},  # Storm 2
    {'num_tips': 6, 'gap_days': 3},  # Storm 3
    {'num_tips': 1, 'gap_days': 2},  # Storm 4
    {'num_tips': 7, 'gap_days': 4},  # Storm 5
    {'num_tips': 5, 'gap_days': 2},  # Storm 6
    {'num_tips': 2, 'gap_days': 3},  # Storm 7
    {'num_tips': 8, 'gap_days': 2},  # Storm 8
    {'num_tips': 4, 'gap_days': 3},  # Storm 9
    {'num_tips': 10, 'gap_days': 2}  # Storm 10
]

storm_counter = 1
for spec in storm_specs:
    # Increase base_time by the specified gap in days before starting the next storm.
    base_time += timedelta(days=spec['gap_days'])
    for i in range(spec['num_tips']):
        # For realism, tips occur at one-minute intervals within a storm.
        timestamps.append(base_time + timedelta(minutes=i))
        storms.append(storm_counter)
        stormIDs.append(storm_counter)
    storm_counter += 1

# Convert lists to numpy arrays.
timestamp_date_in = np.array(timestamps)
storms_in = np.array(storms)
stormID_in = np.array(stormIDs)

# Create tip values (each tip adds tip_mag) and cumulative rainfall.
tipvals = np.full(len(timestamp_date_in), tip_mag)
tipvals[0] = 0  # initial deployment row has tip value 0.
cumrain = np.cumsum(tipvals)

# -------------------------------
# Export Data to Excel
# -------------------------------

# --- Fixed Interval ---
# Create a continuous time series at the fixed interval (1 minute) from the earliest to latest timestamp.
start_time = min(timestamp_date_in)
end_time = max(timestamp_date_in)
fixed_timestamps = pd.date_range(start=start_time, end=end_time, freq=f'{logging_interval}T', tz='America/Los_Angeles')
df_fixed = pd.DataFrame({'timestamp': fixed_timestamps})

# Build a DataFrame for the raw tip data and ensure timezone awareness.
df_tips = pd.DataFrame({
    'timestamp': pd.Series(timestamp_date_in).dt.tz_localize('America/Los_Angeles'),
    'tip': tipvals
})

# Merge the fixed time series with the tip data using merge_asof with tolerance.
tolerance = pd.Timedelta(minutes=logging_interval / 2)
df_fixed = pd.merge_asof(df_fixed, df_tips, on='timestamp', direction='nearest', tolerance=tolerance)

# Fill missing tip values with 0.
df_fixed['tip'] = df_fixed['tip'].fillna(0)

# Optionally compute cumulative rainfall.
df_fixed['cumulative'] = df_fixed['tip'].cumsum()

# Format timestamps as strings.
df_fixed['timestamp'] = df_fixed['timestamp'].dt.strftime('%m/%d/%y %H:%M:%S')

# Write to Excel.
df_fixed.to_excel(out_profile_fixed, index=False)
print("Fixed Interval data exported to:", out_profile_fixed)

# --- Cumulative Tips ---
# Create a Series for the timestamps, ensuring timezone localization.
ts_series = pd.Series(timestamp_date_in).dt.tz_localize('America/Los_Angeles')

df_cum = pd.DataFrame({
    'timestamp': ts_series,
    'n_tips': np.cumsum(np.ones(len(timestamp_date_in))),
    'tip': tipvals,
    'cumulative': cumrain
})

# Prepend an extra row with initial deployment values (all zeros).
initial_row = pd.DataFrame({
    'timestamp': [ts_series.iloc[0]],
    'n_tips': [0],
    'tip': [0],
    'cumulative': [0]
})
df_cum = pd.concat([initial_row, df_cum], ignore_index=True)

# Format the timestamp column as strings.
df_cum['timestamp'] = pd.to_datetime(df_cum['timestamp']).dt.strftime('%m/%d/%y %H:%M:%S')

# Write to Excel.
df_cum.to_excel(out_profile_cumulative, index=False)
print("Cumulative Tips data exported to:", out_profile_cumulative)

print("Data exported successfully!")
