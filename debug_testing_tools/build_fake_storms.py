import numpy as np
from datetime import datetime, timedelta
import pandas as pd

# ------------------------
# Fake Storm Data Creation
# ------------------------

# Parameters for fake data
tip_type = 'Cumulative Tips'  # Choose 'Fixed Interval' or 'Cumulative Tips'
logging_interval = 1  # minutes; required for fixed interval
tip_mag = 0.2  # each tip adds 0.2 mm rainfall
# min_depth = 0.2  # minimum event rainfall depth threshold (mm)
# min_duration = 0  # minimum event duration threshold (hours)

# Base time for the dataset
base_time = datetime(2022, 1, 1, 0, 0, 0)
# Output file path for debugging
out_profile_fid = r'C:\Users\Scott\Desktop\debug\syn_cum.xlsx'


# Build fake timestamps and storm segmentation arrays
timestamps = []
storms = []  # storm identifier per tip
stormIDs = []  # same as storms in this simple case

# Storm 1: 5 tips (good)
for i in range(5):
    timestamps.append(base_time + timedelta(minutes=i))
    storms.append(1)
    stormIDs.append(1)

# Gap of 15 minutes, then Storm 2: 2 tips (suppressed: too few tips)
base_time += timedelta(minutes=15)
for i in range(2):
    timestamps.append(base_time + timedelta(minutes=i))
    storms.append(2)
    stormIDs.append(2)

# Gap, then Storm 3: 6 tips (good)
base_time += timedelta(minutes=15)
for i in range(6):
    timestamps.append(base_time + timedelta(minutes=i))
    storms.append(3)
    stormIDs.append(3)

# Gap, then Storm 4: 1 tip (suppressed: only one tip)
base_time += timedelta(minutes=15)
timestamps.append(base_time)
storms.append(4)
stormIDs.append(4)

# Gap, then Storm 5: 7 tips (good)
base_time += timedelta(minutes=15)
for i in range(7):
    timestamps.append(base_time + timedelta(minutes=i))
    storms.append(5)
    stormIDs.append(5)

# Convert lists to numpy arrays
timestamp_date_in = np.array(timestamps)
storms_in = np.array(storms)
stormID_in = np.array(stormIDs)

# Create tip values (each tip is tip_mag) and cumulative rainfall
tipvals = np.full(len(timestamp_date_in), tip_mag)
cumrain = np.cumsum(tipvals)

# -------------------------------
# Build DataFrame for Excel Output
# -------------------------------

if tip_type == 'Fixed Interval':
    # Create a fixed time series from start to end at a 1-minute interval.
    start_time = min(timestamp_date_in)
    end_time = max(timestamp_date_in)
    fixed_timestamps = pd.date_range(start=start_time, end=end_time, freq=f'{logging_interval}T')
    df_fixed = pd.DataFrame({'timestamp': fixed_timestamps})

    # Create a DataFrame for the raw tip data.
    df_tips = pd.DataFrame({
        'timestamp': pd.to_datetime(timestamp_date_in),
        'tip': tipvals
    })

    # Use merge_asof with a tolerance so that only timestamps that are nearly identical get merged.
    # Here, we set the tolerance to half of the logging interval.
    tolerance = pd.Timedelta(minutes=logging_interval / 2)
    df_fixed = pd.merge_asof(df_fixed, df_tips, on='timestamp', direction='nearest', tolerance=tolerance)

    # Fill in missing tip values with 0
    df_fixed['tip'] = df_fixed['tip'].fillna(0)

    # Optionally compute cumulative rainfall
    df_fixed['cumulative'] = df_fixed['tip'].cumsum()

    # Format the timestamps as desired
    df_fixed['timestamp'] = df_fixed['timestamp'].dt.strftime('%m/%d/%y %H:%M:%S')

    # Write to Excel
    df_fixed.to_excel(out_profile_fid, index=False)

    print("Fixed Interval data exported to:", out_profile_fid)

else:  # Cumulative Tips
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(timestamp_date_in),
        'n_tips': np.cumsum(np.ones(len(timestamp_date_in))),
        'tip': tipvals,
        'cumulative': cumrain
    })
    # Format timestamps as a string
    df['timestamp'] = df['timestamp'].dt.strftime('%m/%d/%y %H:%M:%S')

    # Write to Excel
    df.to_excel(out_profile_fid, index=False)
    print("Cumulative Tips data exported to:", out_profile_fid)

print("Data exported successfully!")

