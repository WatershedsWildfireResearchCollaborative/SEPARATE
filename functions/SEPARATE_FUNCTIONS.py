# %% Required modules

import numpy as np
import pandas as pd
from datetime import timedelta, datetime
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import openpyxl
from collections import defaultdict
import PySimpleGUI as sg
from matplotlib.ticker import MaxNLocator
from scipy import stats
import math
# this is required for eps and pdf figure saving
import matplotlib
matplotlib.use('Agg')
import matplotlib.backends.backend_ps
import matplotlib.backends.backend_pdf

# from scipy.constants import minute
# from sklearn.linear_model import LinearRegression


# %% data analysis functions
def rename_repeating_dates(dates):
    """
    Takes a list of dates and returns a new list with repeated dates suffixed with a counter (e.g. '2022-01-01_2')

    Args:
        dates (list): A list of dates.

    Returns:
        list: A list of renamed dates.
    """
    # Create a default dict to count occurrences of each date
    date_counts = defaultdict(int)
    renamed_dates = []  # Initialize an empty list to store the renamed dates

    # Iterate over the dates and count occurrences
    for date in dates:
        date_counts[date] += 1  # Increment the count for the current date
        count = date_counts[date]  # Get the current count
        if count > 1:  # If the date is repeating
            # Append the date with the count to the renamed dates list
            renamed_dates.append(f"{date}_{count}")
        else:  # If the date is not repeating
            # Append the date as is to the renamed dates list
            renamed_dates.append(str(date))

    return renamed_dates  # Return the list of renamed dates


def separate_preprocessing(filename, sheetname, tip_type, tip_mag):
    """
    Loads tip data from an Excel file (.xlsx or .csv) and preprocesses it for analysis.

    Args:
        filename (str): Path to the Excel file.
        sheetname (str, optional): Sheet name or 'none' if using the default. Defaults to None.
        tip_type (str, optional): Type of tip data ('fixed interval' or 'cumulative tips'). Defaults to None.
        tip_mag (float, optional): Tip magnitude in mm. Defaults to None.

    Returns:
    tuple:
        - tip_datetime (pd.Series): A Pandas Series of datetime objects representing the timestamps of the tip data.
        - tip_depth (np.ndarray): A NumPy array of tip depth values.
        - logging_interval (float): The logging interval of the tip data (only applicable for 'fixed interval' tip type).
        - start_date (datetime.date): The start date of the tip data record.
        - end_date (datetime.date): The end date of the tip data record.
    """

    # Split the filename into name and extension
    _, file_extension = os.path.splitext(filename)
    file_extension = file_extension.lower()  # for consistency


    # Check if the file is an Excel file (.xlsx)
    if file_extension == '.xlsx':
        # If sheet name is not provided, load data from the first sheet
        if sheetname is None or sheetname == '':
            # Load in excel input data into data frame
            df = pd.read_excel(filename)
        else:
            # Load in excel input data based on the provided sheetname
            df = pd.read_excel(filename, sheet_name=sheetname)
    # Check if the file is a CSV file
    elif file_extension == '.csv':
        # Load in csv input data into data frame
        df = pd.read_csv(filename)
    else:
        raise ValueError("Unsupported file extension: " + file_extension)

    # get the header for each column
    headers = df.columns
    # set date time formating
    df[headers[0]] = pd.to_datetime(df[headers[0]], errors='coerce')
    # check for any issues
    if df[headers[0]].isna().any():
        print("Warning: Some datetime values could not be parsed!")

    # get start and end date of the record
    start_date = min(df[headers[0]]).date()
    end_date = max(df[headers[0]]).date()

    if tip_type == "Cumulative Tips":
        # If tips are recorded as cumulative tips, read in as is
        tip_datetime = pd.to_datetime(df[headers[0]])
        tip_depth = np.ones(len(tip_datetime))*tip_mag
        errmsg = None
        logging_interval = 1.0  # dummy value

    # If tips are recorded as depth per unit time (e.g. min), read in as:
    elif tip_type == "Fixed Interval":
        # get the logging interval
        logging_interval = df[headers[0]].diff().dt.total_seconds() / 60
        logging_interval = stats.mode(logging_interval)[0]  # logging_interval[0]

        # find zeros in the data where no tips occurred
        ind_zero = np.where(df[headers[1]] == 0)[0]
        logging_interval = stats.mode(logging_interval)[0]  # logging_interval[0]

        # remove 0 values from dataframe
        df_adj = df.drop(ind_zero).reset_index(drop=True)
        # get the dates
        tip_datetime = pd.to_datetime(df_adj[headers[0]])
        tip_depth = df_adj[headers[1]].to_numpy()

        # cum_rainfall=df_in[headers[1]].cumsum()
    else:
        raise ValueError('Invalid Tip type')
        errmsg = 'Invalid Tip Type'

    # Return dates, tib values, logging interval and start and end dates of the record
    return tip_datetime, tip_depth, logging_interval, start_date, end_date


def separate_ISC(tip_datetime, tip_depth, isc_t_max, min_depth, min_duration,
                           gap_plots_path, output_name, plt_ext):
    """
    Computes the optimal inter-event time (MIT) from tipping cup data using the coefficient of variation (CV) method.

    Args:
        tip_datetime (pd.Series): Pandas Series of datetime objects for each tip.
        tip_depth (np.ndarray): NumPy array of tip depth values.
        isc_t_max (float): Maximum inter-event test interval (hours) for ISC.
        min_depth (float): Minimum storm magnitude (tip units).
        min_duration (float): Minimum storm duration (hours).
        gap_plots_path (str): Path to save ISC analysis plots.
        output_name (str): Output name prefix for plots.
        plt_ext (str): Plot file extension (e.g., '.png').

    Returns:
        tuple: A tuple containing the computed Minimum Inter-Event Time (MIT) and other intermediate results, including:
            - tb0 (float): The optimal Minimum Inter-Event Time (MIT) computed by interpolation.
            - CV_IET (np.ndarray): The coefficient of variation (CV) of the inter-event times.
            - mean_IET (np.ndarray): The mean of the inter-event times.
            - std_IET (np.ndarray): The standard deviation of the inter-event times.
            - ISC_testintervals (np.ndarray): The tested inter-event intervals.
            - StormNumsRec (np.ndarray): The number of included and suppressed storms for each test interval.
    """
    # Create test intervals: 0.1 to 0.9 in steps of 0.1, then 1 to isc_time in steps of 1 (inclusive)
    if isc_t_max < 1:
        ISC_testintervals = np.arange(0.1, isc_t_max, 0.1)
    else:
        ISC_testintervals = np.concatenate((np.arange(0.1, 1.0, 0.1), np.arange(1, isc_t_max+1)))

    StormNumsRec = []
    mean_IET = np.empty(len(ISC_testintervals))
    std_IET = np.empty(len(ISC_testintervals))
    CV_IET = np.empty(len(ISC_testintervals))

    for i in np.arange(len(ISC_testintervals)):
        trial_interval = ISC_testintervals[i]

        # Clear variables (not needed in Python, so we just call the functions)
        ISC_storm_data, ISC_interevent_times = separate_storms(tip_datetime, tip_depth, trial_interval)

        try:
            ISC_storm_data, ISC_interevent_times, N_nofilter, N_suppressed = \
                separate_filter(ISC_storm_data, ISC_interevent_times, min_depth, min_duration)
        except:
            print('No valid data at this window size')
            ISC_interevent_times = []
            N_nofilter = len(ISC_storm_data)
            N_suppressed = len(ISC_storm_data)

        N_storms = N_nofilter - N_suppressed
        StormNumsRec.append([N_storms, N_suppressed])
        mean_IET[i] = np.nanmean(ISC_interevent_times)
        std_IET[i] = np.nanstd(ISC_interevent_times, ddof=1)
        # mean_IET[i] = np.nanmean(ISC_interevent_times - trial_interval)
        # std_IET[i] = np.nanstd(ISC_interevent_times - trial_interval, ddof=1)
        CV_IET[i] = std_IET[i] / mean_IET[i] if mean_IET[i] != 0 else np.nan

        # # Compute IET statistics (in hours)
        # if ISC_interevent_times.size > 0:
        #     mean_IET[i] = np.nanmean(ISC_interevent_times)
        #     std_IET[i] = np.nanstd(ISC_interevent_times, ddof=1)
        #     CV_IET[i] = std_IET[i] / mean_IET[i] if mean_IET[i] != 0 else np.nan
        # else:
        #     mean_IET[i] = np.nan
        #     std_IET[i] = np.nan
        #     CV_IET[i] = np.nan

    StormNumsRec = np.array(StormNumsRec)

    # Find last index where CV_IET > 1.
    CV0_idx = np.where(CV_IET > 1)[0]
    if CV0_idx.size == 0 or CV0_idx[-1] == len(ISC_testintervals) - 1:
        errmsg="Warning: ISC analysis did not converge. No MIT value - consider increasing ISC upper limit."
        print(errmsg)
        sg.popup_error(errmsg, title='Error', text_color='black', background_color='white',
                       button_color=('black', 'lightblue'))
        tb0 = None
        mean_tb = None
    else:
        cv_last = CV0_idx[-1]
        # Interpolate to get tb0 where CV_IET equals 1.
        f_tb = interp1d(CV_IET[cv_last:cv_last + 2], ISC_testintervals[cv_last:cv_last + 2])
        tb0 = f_tb(1.0)
        # Similarly, interpolate to get mean_IET at tb0.
        f_mean = interp1d(ISC_testintervals[cv_last:cv_last + 2], mean_IET[cv_last:cv_last + 2])
        mean_tb = f_mean(tb0)

        #------------------ Plotting Section ------------------
        # Plot IET statistics
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        axs[0].plot(ISC_testintervals, 1 / mean_IET, 'r-', linewidth=1, label='Mean of Time Between Storms')
        axs[0].plot(ISC_testintervals, 1 / std_IET, 'b-', linewidth=1, label='Std Dev of Time Between Storms')
        if tb0 is not None and mean_tb is not None:
            axs[0].plot(tb0, 1 / mean_tb, 'ko', markersize=8, label='Minimum Inter-event Time (MIT)')
        axs[0].set_ylim([0, axs[0].get_ylim()[1]])
        axs[0].set_xlim([0, np.max(ISC_testintervals)])
        axs[0].set_xticks(np.arange(0, np.max(ISC_testintervals), 6))
        if tb0 is not None:
            axs[0].text(tb0 + 1, 1 + axs[0].get_ylim()[1] / 20, f"MIT = {tb0:.1f} hrs")
        # axs[0].set_title("Analysis of Inter-event Independence")
        axs[0].legend(loc='upper right')
        axs[0].set_xlabel("Tested Inter-Event Interval [hrs]")
        axs[0].set_ylabel("Time [hrs$^{-1}$]")
        axs[0].grid(True)

        axs[1].plot(ISC_testintervals, CV_IET, 'k-', linewidth=1, label='CV')
        if tb0 is not None:
            axs[1].plot(tb0, 1, 'ko', markersize=7)
            axs[1].text(tb0 + 1, 1 + axs[1].get_ylim()[1] / 20, f"MIT = {tb0:.1f} hrs")
        axs[1].set_ylim([0, axs[1].get_ylim()[1]])
        axs[1].set_xlim([0, np.max(ISC_testintervals)])
        axs[1].set_xticks(np.arange(0, np.max(ISC_testintervals), 6))
        # axs[1].set_title("Independence Criterion")
        axs[1].set_xlabel("Tested Inter-Event Interval [hrs]")
        axs[1].set_ylabel("CV")
        axs[1].grid(True)

        # Save the first figure
        plot_fid = os.path.join(gap_plots_path, output_name + '_IndependenceCriterion' + plt_ext)
        plt.savefig(plot_fid)
        plt.close(fig)

        # plot up the number of storms included and suppressed
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        frac_included = StormNumsRec[:, 0] / (StormNumsRec[:, 0] + StormNumsRec[:, 1])
        frac_suppressed = StormNumsRec[:, 1] / (StormNumsRec[:, 0] + StormNumsRec[:, 1])
        ax2.plot(ISC_testintervals, frac_included, linewidth=1.5, label='Included Storms')
        ax2.plot(ISC_testintervals, frac_suppressed, linewidth=1.5, label='Suppressed Storms')
        if tb0 is not None:
            ax2.plot([tb0, tb0], [0, 1], 'k--', linewidth=1, label='MIT')
        ax2.set_ylabel('Fraction of Identified Storms')
        ax2.set_xlabel("Tested Inter-Event Interval [hrs]")
        ax2.legend(loc='upper right')
        ax2.grid(True)
        plot_fid = os.path.join(gap_plots_path, output_name + '_SuppressedStorms' + plt_ext)
        plt.savefig(plot_fid)  # save
        plt.close()

        return tb0, mean_tb, CV_IET, mean_IET,std_IET, ISC_testintervals, StormNumsRec


def separate_storms(tip_datetime, tip_depth, test_interval):
    """
    Identify breaks in storms and generate storm records.

    Args:
        tip_datetime (list): List of datetime objects representing tip timestamps.
        tip_depth (np.ndarray): NumPy array of numeric tip values representing tip magnitudes.
        test_interval (float): Test interval in hours; if the time difference between consecutive tips exceeds this, a storm break is assumed.

    Returns:
        tuple: A tuple containing:
            - storms (list): List of dictionaries, where each dictionary contains:
                - 'indices': List of indices for tips in the storm.
                - 'start': Storm start datetime.
                - 'end': Storm end datetime.
                - 'duration': Storm duration in hours.
                - 'magnitude': Storm magnitude (sum of tip_depth).
                - 'intensity_avg': Average intensity (magnitude/duration)
            - interevent_times (np.ndarray): NumPy array of inter-event times (hours) corresponding to the time differences that exceeded the test_interval.
    """
    storms = []
    interevent_times = []
    storm_idx = []  # will hold indices for the current storm
    n = len(tip_datetime)
    dt_tips = []  # list to hold differences (in hours) between consecutive tips

    for i in range(n - 1):
        # Compute difference in hours between tip i+1 and tip i.
        dt = (tip_datetime[i + 1] - tip_datetime[i]).total_seconds() / 3600.0
        dt_tips.append(dt)

        if dt > test_interval:
            # We have identified a break.
            interevent_times.append(dt)
            if i == n - 2:
                # Special case: the break occurs at the second-to-last tip.
                storm_idx.append(i)  # add current index
                # Build storm record from current storm indices.
                storm_record = build_storm_record(tip_datetime, tip_depth, storm_idx)
                storms.append(storm_record)
                storm_idx = []
                # Start a new storm with the last tip.
                storm_idx.append(i + 1)
                storm_record = build_storm_record(tip_datetime, tip_depth, storm_idx)
                storms.append(storm_record)
                storm_idx = []
            else:
                # General case: break found, but not at the end.
                storm_idx.append(i)  # add current index
                storm_record = build_storm_record(tip_datetime, tip_depth, storm_idx)
                storms.append(storm_record)
                storm_idx = []
        else:
            # No break; add current index to the current storm.
            storm_idx.append(i)
            # If we're at the second-to-last tip, also add the last tip.
            if i == n - 2:
                storm_idx.append(i + 1)
                storm_record = build_storm_record(tip_datetime, tip_depth, storm_idx)
                storms.append(storm_record)
                storm_idx = []

    return storms, np.array(interevent_times)


def build_storm_record(tip_datetime, tip_depth, indices):
    """
    Given a list of indices for a storm, compute and return a dictionary with storm metrics.

    Args:
        tip_datetime (list): List of datetime objects representing tip timestamps.
        tip_depth (np.ndarray): NumPy array of numeric tip values representing tip magnitudes.
        indices (list): List of indices corresponding to the current storm.

    Returns:
        dict: A dictionary with storm metrics, including:
            - 'indices': List of indices for tips in the storm.
            - 'start': Storm start datetime.
            - 'end': Storm end datetime.
            - 'duration': Storm duration in hours.
            - 'magnitude': Storm magnitude (sum of tip_depth).
            - 'intensity_avg': Average intensity (magnitude/duration).
    """
    # Ensure indices is not empty.
    if not indices:
        return None
    # get start time
    start_datetime = tip_datetime[indices[0]]
    # get end time
    end_datetime = tip_datetime[indices[-1]]
    # compute duration
    duration = (end_datetime - start_datetime).total_seconds() / 3600.0
    # compute magnitude
    magnitude = np.sum(tip_depth[indices])
    # compute intensity
    intensity_avg = magnitude / duration if duration != 0 else np.nan
    # return values in a dictionary
    return {
        'indices': indices.copy(),
        'start': start_datetime,
        'end': end_datetime,
        'duration': duration,
        'magnitude': magnitude,
        'intensity_avg': intensity_avg
    }


def separate_filter(storm_data, interevent_times, min_mag, min_dur):
    """
    Filter storm data based on minimum magnitude and duration criteria.

    Args:
        storm_data (list): List of dictionaries containing storm data.
        interevent_times (np.ndarray): NumPy array of inter-event times.
        min_mag (float): Minimum magnitude threshold (optional).
        min_dur (float): Minimum duration threshold (optional).

    Returns:
        tuple: A tuple containing:
            - storm_data (list): Filtered list of storm data dictionaries.
            - interevent_times (np.ndarray): Updated NumPy array of inter-event times.
            - N_nofilter (int): Number of storms before filtering.
            - N_suppressed (int): Number of storms suppressed by filtering.
    """

    N_nofilter = len(storm_data)
    flag_idx = []  # indices of storms to suppress

    # Build flag indices based on the criteria.
    for i, storm in enumerate(storm_data):
        duration = storm['duration']
        magnitude = storm['magnitude']
        # Apply filtering logic
        if min_dur is not None and min_mag is not None:
            if duration > min_dur and magnitude > min_mag:
                continue
            else:
                flag_idx.append(i)

        elif min_mag is not None and min_dur is None:
            if magnitude > min_mag:
                continue
            else:
                flag_idx.append(i)

        elif min_dur is not None and min_mag is None:
            if duration > min_dur:
                continue
            else:
                flag_idx.append(i)

    N_suppressed = len(flag_idx)

    # convert flag_idx to numpy array
    flag_idx = np.array(flag_idx, dtype=int)  # Ensure it's an integer array
    # If flag_idx has values, proceed with filtering
    if flag_idx.size>0:
        # Remove storms from storm_data
        storm_data = [storm for i, storm in enumerate(storm_data) if i not in flag_idx]


        # Handling interevent_times updates
        if flag_idx[-1] == N_nofilter - 1 and len(flag_idx) > 1:
            # Case where last storm is removed and previous values are sequential
            initial_idx = len(flag_idx) - 1
            indices2remove = [initial_idx]
            while initial_idx > 0 and flag_idx[initial_idx] - flag_idx[initial_idx - 1] == 1:
                initial_idx -= 1
                indices2remove.append(initial_idx)

            interevent_times = np.delete(interevent_times, indices2remove)
            flag_idx = flag_idx[:-len(indices2remove)]

        elif flag_idx[-1] == N_nofilter - 1 and len(flag_idx) == 1:
            interevent_times = np.delete(interevent_times, -1)  # Remove last row
            flag_idx= np.delete(flag_idx, -1)  # Trim last index for storm

        if flag_idx.size>0:  # Verify still exists after trimming
            if flag_idx[0] == 0:
                flag_idx=flag_idx[1:]
                interevent_times[flag_idx - 1] += interevent_times[flag_idx]  # Add IET preceding removed storms
                interevent_times = np.delete(interevent_times, flag_idx)  # Remove flagged interevent times
                interevent_times = np.delete(interevent_times, 0)  # Remove first IET
            else:
                interevent_times[flag_idx - 1] += interevent_times[flag_idx]
                # Now, delete all flagged indices AT ONCE to avoid shifting issues
                interevent_times = np.delete(interevent_times, flag_idx)


    return storm_data, interevent_times, N_nofilter, N_suppressed


def separate_profiler(StormIDX, storm_data, tip_datetime, tip_depth, int_min):
    """
    Extract storm profile data.

    Args:
        StormIDX (int): Storm index (0-based) to process.
        storm_data (list): List of dictionaries containing storm data.
        tip_datetime (list): Global tip timestamps.
        tip_depth (np.ndarray): NumPy array of numeric tip values.
        int_min (int): Intensity interval (in minutes).

    Returns:
        tuple: A tuple containing:
            - iD_Mag (np.ndarray): Calculated intensities (tip units per hour) for each window.
            - iD_time (np.ndarray): Corresponding times (in minutes) for intensities.
            - R_fit (np.ndarray): Interpolated cumulative rainfall (tip units).
            - t_fit (np.ndarray): Time values (in minutes) for interpolation.
            - tip_idx (list): Tip indices for the specified storm.
            - cum_rain (np.ndarray): Cumulative rainfall for the storm.
            - duration_min (int): Storm duration in minutes (floor value).

        If there are insufficient tips (<= 2), returns (None, None, None, None, None, None, None).
    """
    # Extract the tip indices for the specified storm.
    tip_idx = storm_data[StormIDX]['indices']

    # Check that we have more than 2 tips.
    if len(tip_idx) <= 2:
        return None, None, None, None, None, None, None

    # Get the tip times for this storm.
    tip_times = [tip_datetime[i] for i in tip_idx]
    start_time_abs = storm_data[StormIDX]['start']

    # Compute relative tip times (in minutes) relative to the storm start.
    relative_tip_times = np.array([(tt - start_time_abs).total_seconds() / 60.0 for tt in tip_times])

    # Compute cumulative rainfall for the storm.
    cum_rain = np.cumsum(tip_depth[tip_idx])

    # Compute storm duration in minutes (floor value).
    duration_min = int(np.floor(storm_data[StormIDX]['duration'] * 60))

    # Generate an interpolation time vector at 1-minute resolution.
    fit_dt = 1  # minute resolution
    t_fit = np.arange(0, duration_min + fit_dt, fit_dt)  # in minutes

    # Interpolate cumulative rainfall onto the new time grid.
    # Using linear interpolation with extrapolation if needed.
    f_interp = interp1d(relative_tip_times, cum_rain, kind='linear', bounds_error=False, fill_value="extrapolate")
    R_fit = f_interp(t_fit)

    # Only compute intensities if time vector spans more than int_min minutes.
    if np.max(t_fit) > int_min:
        # Prepare arrays for intensity (iD_Mag) and corresponding time indices (iD_time).
        # Compute intensity for each window of length int_min (in minutes) along t_fit.
        num_windows = len(t_fit) - int_min
        iD_Mag = np.full(num_windows, np.nan)
        iD_time = np.full(num_windows, np.nan)
        for t in range(num_windows):
            t_adj = t + int_min  # this is the ending index of the window
            # Compute intensity: difference in cumulative rainfall over the window,
            # divided by the window duration in hours.
            iD_Mag[t] = (R_fit[t_adj] - R_fit[t_adj - int_min]) / (int_min / 60.0)
            iD_time[t] = t_fit[t_adj]

    else:
        iD_Mag = np.nan
        iD_time = np.nan
        R_fit = np.nan
        t_fit = np.nan

    return iD_Mag, iD_time, R_fit, t_fit, tip_idx, cum_rain, duration_min

    # change this to function call plot_inter_event_histogram


def plot_inter_event_histogram(filtered_interevent_times, mean_tb, Fixed_MIT, gap_plots_path, output_name, plt_ext):
    """
    Plots a histogram of inter-event times with an exponential fit.

    Parameters:
    - filtered_interevent_times: array-like, inter-event times [hrs]
    - mean_tb: float, mean of the inter-event times [hrs]
    - gap_plots_path: str, path to save the figure
    - output_name: str, prefix for the output filename
    - plt_ext: str, file extension (e.g., '.png')
    - Fixed_MIT: float, used for bin width in histogram
    """

    # Exponential PDF fit
    lam = 1 / mean_tb
    max_time = max(filtered_interevent_times)
    x_vals = np.arange(0, max_time + 1, 0.1)
    y_vals = lam * np.exp(-lam * x_vals)

    # Create bins using fixed MIT
    bins = np.arange(0, max_time + Fixed_MIT, Fixed_MIT)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(filtered_interevent_times, bins=bins, density=True, alpha=0.75,
            label=f'Histogram (bin width = {np.round(Fixed_MIT,2)})')
    ax.plot(x_vals, y_vals, 'r-', lw=2, label='Exponential Fit')

    ax.set_xlabel("Inter-Event Time [hours]")
    ax.set_ylabel("Probability Density")
    ax.set_title("Distribution of Inter-Storm Times (Not Including Suppressed Storms)")
    ax.legend(loc='upper right')
    ax.grid(False)
    plt.box(True)
    plt.tight_layout()

    # Save figure
    filename = f"{output_name}_ExponentialFit{plt_ext}"
    plt.savefig(os.path.join(gap_plots_path, filename))
    plt.close()


def separate_peak_intensity(start_time_abs, t_fit, R_fit, intensity_interval):
    """
    Calculate the peak intensity (iD_Mag) and corresponding time for a given storm profile.

    Args:
        start_time_abs (datetime): The absolute start time of the storm.
        t_fit (np.ndarray): Time vector (in minutes) from interpolation.
        R_fit (np.ndarray): Interpolated cumulative rainfall values.
        intensity_interval (Union[int, float]): The intensity interval in minutes.

    Returns:
        tuple: A tuple containing:
            - intensity_interval (Union[int, float]): Same as input.
            - peakiD_Mag (float): The peak intensity (tip units per hour).
            - peakiD_datetime (datetime): Datetime corresponding to the peak intensity.
            - peakiD_time_relative (float): Relative time (in minutes) at which the peak occurs.

        If max(t_fit) is not greater than intensity_interval, returns (intensity_interval, np.nan, np.nan, np.nan).
    """
    # Check if t_fit is None; if so, return default values.
    # print(intensity_interval)
    if t_fit is None:
        return intensity_interval, np.nan, np.nan, np.nan, None
    if np.max(t_fit) > intensity_interval:
        # Preallocate arrays for intensity and time. The number of windows equals len(t_fit)-intensity_interval.
        num_windows = len(t_fit) - int(intensity_interval)
        iD_Mag = np.full(num_windows, np.nan)
        iD_time = np.full(num_windows, np.nan)

        # Loop through each window.
        for t in range(num_windows):
            t_adj = t + int(intensity_interval)  # ending index of the window
            # Compute intensity: difference in cumulative rainfall over the window,
            # divided by (intensity_interval in hours)
            iD_Mag[t] = (R_fit[t_adj] - R_fit[t_adj - int(intensity_interval)]) / (intensity_interval / 60.0)
            iD_time[t] = t_fit[t_adj]  # using the time at the end of the window

        # Find index/indices where intensity is maximum.
        # Use np.nanmax to ignore NaNs.
        max_intensity = np.nanmax(iD_Mag)
        idx_peaks = np.where(iD_Mag == max_intensity)[0]
        # If there are multiple peaks, take the last one.
        idx_peak = idx_peaks[-1]

        peakiD_Mag = iD_Mag[idx_peak]
        peakiD_time_relative = iD_time[idx_peak]   # in minutes; add 1 min to offset zero indexing

        # MATLAB code adds: start_time_abs + (peakiD_time_relative/1400)
        # This seems to convert minutes to days using a factor ~ 1400 (normally 1440 minutes/day).
        # We mimic that exactly.
        peakiD_datetime = start_time_abs + timedelta(days=peakiD_time_relative / 1440.0)
    else:
        peakiD_Mag = np.nan
        peakiD_datetime = np.nan
        peakiD_time_relative = np.nan

    return intensity_interval, peakiD_Mag, peakiD_datetime, peakiD_time_relative


def output_fitting_parameters_to_file(software_metadata, user_parameters, gap_CV, gap_mean,gap_std, stormgap_array,
                                      StormNumsRec,  output_name, gap_plots_path, output_ext):
    """
    Outputs the fitting parameters from the independence criterion method to an Excel file.

    Args:
        software_metadata (list): List of strings containing the software version information.
        user_parameters (dict): Dictionary of user provided parameters.
        gap_CV (float): The coefficient of variation of the time between events.
        gap_mean (float): The mean time between events.
        gap_std (float): The standard deviation of the time between events.
        stormgap_array (np.ndarray): Array of storm gap values from the optimization.
        StormNumsRec (np.ndarray): Array of storm numbers and suppressed storms.
        output_name (str): The name of the output file.
        gap_plots_path (str): The path to the folder where the plots will be saved.
        output_ext (str): File extension for output (e.g. '.xlsx' or '.csv').

    Returns:
        None
    """
    software_metadata_df = pd.DataFrame({'Software Metadata': software_metadata})
    # user inputs
    user_parameters_df = pd.DataFrame(list(user_parameters.items()), columns=['User Parameters', 'Parameter'])
    # model coefficients
    # mdl_info = ['Storm Gap Best-Fit', f'y={round(mdl_a, 2)}*x^{round(mdl_b, 2)}',
    #             'y = number of storms', 'x = storm gap (hours)']
    # best_fit_df = pd.DataFrame({'Fit Parameters': mdl_info})

    # modeled values
    # Create Output Table of Storm Parameters
    columns = ['Minimum_Storm_Separation_Time', 'Coefficient_of_Variation', 'Mean','Standard_Deviation', "Number_of_Included_Storms", "Number_of_Suppressed_Storms"]
    units = ['hours',  '-', 'hours', 'hours', '-', '-']
    # stormgap_array, gap_mean, gap_std, gap_CV, StormNumsRec
    include_storms = StormNumsRec[:, 0]
    suppress_storms = StormNumsRec[:, 1]
    combined_xy = np.hstack((stormgap_array.flatten().reshape(-1, 1), gap_CV.flatten().reshape(-1, 1),
                             gap_mean.flatten().reshape(-1, 1),gap_std.flatten().reshape(-1, 1),include_storms.flatten().reshape(-1, 1),
                            suppress_storms.flatten().reshape(-1, 1)))

    values_df = pd.DataFrame(combined_xy, columns=columns)
    # output = pd.DataFrame(values_df, columns=columns)
    output_headers = pd.DataFrame([units], columns=columns)

    # get file extension
    output_ext = output_ext.lower()
    if output_ext not in (".xlsx", ".csv"):
        output_ext = ".xlsx" # fail-safe into xlsx
    # output file name
    output_file_name = f"{output_name}_ISC_analysis{output_ext}"  # create a file name
    out_fid  = os.path.join(gap_plots_path, output_file_name)  # set up full file path

    if output_ext == ".xlsx": # write xlsx
        with pd.ExcelWriter(out_fid, engine='openpyxl') as writer:
            sheetname = 'Independent_Storms_Criterion'
            # write citations and version info to excel
            software_metadata_df.to_excel(writer, sheet_name=sheetname, index=False, startrow=0, header=False)

            # write user inputs to excel
            s_row = len(software_metadata) + 1
            user_parameters_df.to_excel(writer, sheet_name=sheetname, index=False, startrow=s_row, header=False)
            # s_row = s_row + len(user_parameters) + 1
            # best_fit_df.to_excel(writer, sheet_name=sheetname, index=False, header=False, startrow=s_row)

            # Write the output DataFrame below the metadata
            # s_row = s_row + len(best_fit_df) + 1
            s_row = s_row + len(user_parameters) + 1
            output_headers.to_excel(writer, sheet_name=sheetname, index=False, startrow=s_row)

            # Write the output DataFrame below the metadata
            s_row = s_row + 2
            values_df.to_excel(writer, sheet_name=sheetname, index=False, startrow=s_row, header=False)
            # output.to_excel(writer, sheet_name=sheetname, index=False, startrow=s_row)
    else:
        with open(out_fid, "w", newline="") as f:
            # metadata (one col)
            software_metadata_df.to_csv(f, index=False, header=False)
            # blank line
            f.write("\n")
            # user parameters (two cols)
            user_parameters_df.to_csv(f, index=False, header=False)
            # blank line
            f.write("\n")
            # header row (units)
            output_headers.to_csv(f, index=False, header=True)
            # data
            values_df.to_csv(f, index=False, header=False)


def separate_profile_plots(interval, tip_units, Peak_int, Peak_time, t_fit, R_fit, tip_idx, iD_time, iD_Mag,
                           fig_title, output_folder, storm_id_name, plt_ext):
    """
       Creates a plot of the cumulative rainfall and peak intensity for a given storm profile.

       Args:
           interval (int): The time interval for the intensity calculation.
           tip_units (str): The units of the tip values.
           Peak_int (float): The peak intensity value.
           Peak_time (float): The time of the peak intensity.
           t_fit (np.ndarray): The time values for the cumulative rainfall plot.
           R_fit (np.ndarray): The cumulative rainfall values.
           tip_idx (np.ndarray): The indices of the tip values.
           iD_time (np.ndarray): The time values for the intensity plot.
           iD_Mag (np.ndarray): The intensity values.
           fig_title (str): The title of the plot.
           output_folder (str): The folder where the plot will be saved.
           storm_id_name (str): The name of the storm ID.
           plt_ext (str): The file extension for the plot.

       Returns:
           None
   """
    x = t_fit/60 # convert to hours
    y = R_fit # cumulative rainfall

    x2=iD_time/60 # convert to hours
    y2=iD_Mag # rainfall intensity

    # this shouldn't happen but if the peak intensity is negative, set it to nan
    if Peak_int<0:
        Peak_int=np.nan

    # plot up cumulative rainfall and peak intensity
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(x2,y2, 'r-')
    ax1.plot(Peak_time/60, Peak_int, 'ro') # plot peak as a red dot

    ax1.set_ylabel(f'{int(interval)}-minute Intensity, ' + tip_units + r'/hr', color='r')
    ax1.tick_params('y', colors='r')

    ax2.plot(x, y, 'b-')
    if len(tip_idx) < 5:  # if less than five points plot the points as well as the line
        fig_title += f'Note: Limited event data (< 5 tips)'

    ax1.set_xlabel('Time (hours)')
    ax2.set_ylabel('Cumulative Storm Rainfall, ' + tip_units, color='b')
    ax2.tick_params('y', colors='b')
    plt.title(fig_title, loc='left', fontsize=14)
    ax1.set_ylim(0, max(y2) * 1.1)  # Ensures a little padding on top
    ax2.set_ylim(0, max(y) * 1.1)  # Ensures a little padding on top
    plt.subplots_adjust(top=0.6)  # create extra white space for long title

    # plt.show()
    # save the plots
    plot_fid = os.path.join(output_folder, storm_id_name + plt_ext)
    plt.savefig(plot_fid)  # save with basename+storm_id where id == k+1
    plt.close(fig)


def separate_outputs(output, storm_profiles, storm_raw_profiles, tip_units, I_intervals, data_opt,
                     header_parameters, output_path, output_name, plot_int, plt_ext, plot_start_date, plot_end_date,
                     software_metadata, columns, units, output_ext):
    """
    Create final output spreadsheets and summary plots.

    Parameters:
    output (list[dict]): List of dictionaries containing basic storm parameters and peak intensities.
    storm_profiles (dict): Dictionary of storm profiles, where each key is a unique storm name and each value is a profile data dictionary.
    storm_raw_profiles (dict): Dictionary of raw storm profiles, where each key is a unique storm name and each value is a raw profile data dictionary.
    tip_units (str): Units for tipping data.
    I_intervals (list): List of intensity intervals in hours.
    data_opt (bool): Whether to output detailed storm profile data.
    header_parameters (dict): Dictionary of header parameters.
    output_path (str): Folder path for output.
    output_name (str): Base output file name.
    plot_int (str): Plot interval.
    plt_ext (str): File extension for plots (e.g. '.png').
    plot_start_date (str): Start date for plotting (optional).
    plot_end_date (str): End date for plotting (optional).
    software_metadata (list[str]): List of software metadata strings.
    columns (list[str]): List of column names.
    units (list[str]): List of units.
    output_ext (str): File extension for output (e.g. '.xlsx' or '.csv').

    Returns:
    str: Error message (if any) or None.
    """
    output_headers = pd.DataFrame([units], columns=columns)

    # Convert date fields to datetime and then format as strings.
    output['Start'] = pd.to_datetime(output['Start']).dt.strftime('%Y-%m-%d %H:%M:%S')
    sdates = pd.to_datetime(output['Start'])  # storm start dates used for plots later
    output['End'] = pd.to_datetime(output['End']).dt.strftime('%Y-%m-%d %H:%M:%S')
    output = output.round(decimals=2)

    # Build metadata DataFrames.
    software_metadata_df = pd.DataFrame({'Software Metadata': software_metadata})
    user_parameters_df = pd.DataFrame(list(header_parameters.items()), columns=['User Parameters', 'Parameter'])

    errmsg = None
    is_csv = output_ext.lower() == ".csv"
    # stack all the data
    all_profiles_rows = []

    if data_opt:
        for storm_name, profile_data in storm_profiles.items():
            # left block (profile)
            left = pd.DataFrame({
                "Storm ID": storm_name,
                "Cumulative Storm Time (hours)": profile_data.get("Cumulative Storm Time (hours)", []),
                "Intensity Profile (mm/hr)": profile_data.get(
                    f"{plot_int}-min Intensity ({tip_units}/hr)", []
                ),
            })

            # right block (raw)
            raw_profile = storm_raw_profiles.get(storm_name)
            if raw_profile is not None:
                right = pd.DataFrame({
                    "Storm ID": storm_name,
                    "TBRG Time Stamp": raw_profile.get("TBRG Time Stamp", []),
                    "Cumulative Storm Time (hours) (raw)": raw_profile.get("Cumulative Storm Time (hours)", []),
                    f"Cumulative Rainfall ({tip_units})": raw_profile.get(
                        f"Cumulative Rainfall ({tip_units})", []
                    ),
                })
            else:
                right = pd.DataFrame()

            #  pad the shorter one to the length of the longer one
            max_len = max(len(left), len(right))
            left = left.reindex(range(max_len))
            right = right.reindex(range(max_len))

            # build two empty columns between the datasets
            blanks = pd.DataFrame({
                "": [np.nan] * max_len,
                " ": [np.nan] * max_len
            })

            combined = pd.concat([left, blanks, right], axis=1)
            all_profiles_rows.append(combined)

    # final stacked table
    all_profiles_df = (
        pd.concat(all_profiles_rows, ignore_index=True)
        if all_profiles_rows else pd.DataFrame()
    )

    try:
        if is_csv:
            # ---------------- CSV OUTPUT ----------------
            summary_fid = os.path.join(output_path, f"{output_name}_SummaryTable.csv")
            # Write summary file
            with open(summary_fid, "w", newline="") as f:
                # software metadata (one column)
                software_metadata_df.to_csv(f, index=False, header=False)
                # blank line
                f.write("\n")
                # user parameters (two columns)
                user_parameters_df.to_csv(f, index=False, header=False)
                # blank line
                f.write("\n")
                # 4. header row (units)
                output_headers.to_csv(f, index=False, header=True)
                # 5. actual summary table (no header, since headers just written)
                output.to_csv(f, index=False, header=False)

            # Write all profiles file
            if data_opt and not all_profiles_df.empty:
                all_profiles_df.to_csv(
                    os.path.join(output_path, f"{output_name}_All_Storm_Profiles.csv"),
                    index=False
                )

            # per-storm CSVs; this will kick out a separate csv for each storm profile
            # if data_opt:
            #     for storm_name, profile_data in storm_profiles.items():
            #         df_profile = pd.DataFrame({
            #             'Cumulative Storm Time (hours)': profile_data.get('Cumulative Storm Time (hours)', []),
            #             f'Intensity Profile ({tip_units}/hr)': profile_data.get(
            #                 f'{plot_int}-min Intensity ({tip_units}/hr)', [])
            #         })
            #         df_profile.to_csv(
            #             os.path.join(output_path, f"{output_name}_{storm_name}_profile.csv"),
            #             index=False
            #         )
            #         if storm_name in storm_raw_profiles:
            #             pd.DataFrame(storm_raw_profiles[storm_name]).to_csv(
            #                 os.path.join(output_path, f"{output_name}_{storm_name}_raw.csv"),
            #                 index=False
            #             )

        else:
            # ---------------- EXCEL OUTPUT ----------------
            output_file_name = f"{output_name}_SummaryTable.xlsx"
            output_table_fid = os.path.join(output_path, output_file_name)
            sheetname = "Storms_Summary"
            with pd.ExcelWriter(output_table_fid, engine='openpyxl') as writer:
                # metadata
                software_metadata_df.to_excel(writer, sheet_name=sheetname,
                                              index=False, startrow=0, header=False)
                s_row = len(software_metadata) + 1
                user_parameters_df.to_excel(writer, sheet_name=sheetname,
                                            index=False, startrow=s_row, header=False)

                # headers + summary
                s_row = s_row + len(header_parameters) + 1
                output_headers.to_excel(writer, sheet_name=sheetname,
                                        index=False, startrow=s_row)
                s_row = s_row + 2
                output.to_excel(writer, sheet_name=sheetname,
                                index=False, startrow=s_row, header=False)

                # stacked tables as extra sheets
                if data_opt and not all_profiles_df.empty:
                    all_profiles_df.to_excel(writer, sheet_name="All_Storm_Profiles", index=False)

                    # # keep per-storm sheets
                    # for storm_name, profile_data in storm_profiles.items():
                    #     df_profile = pd.DataFrame({
                    #         'Cumulative Storm Time (hours)': profile_data.get('Cumulative Storm Time (hours)', []),
                    #         f'Intensity Profile ({tip_units}/hr)': profile_data.get(
                    #             f'{plot_int}-min Intensity ({tip_units}/hr)', [])
                    #     })
                    #     metadata = profile_data.get('Storm Metadata', {})
                    #     df_meta = pd.DataFrame(list(metadata.items()),
                    #                            columns=['User Parameters', 'Parameter'])
                    #
                    #     df_meta.to_excel(writer, sheet_name=storm_name,
                    #                      index=False, header=False)
                    #     df_profile.to_excel(writer, sheet_name=storm_name,
                    #                         index=False, startrow=len(df_meta) + 1)
                    #
                    #     if storm_name in storm_raw_profiles:
                    #         df_raw = pd.DataFrame(storm_raw_profiles[storm_name])
                    #         df_raw.to_excel(writer, sheet_name=storm_name,
                    #                         index=False, startrow=len(df_meta) + 1,
                    #                         startcol=len(df_profile.columns) + 2)

    except Exception as e:
        errmsg = (
            "Failed to write output file(s). "
            "Ensure the file is closed before running the code.\n"
            f"Error: {e}"
        )
        sg.popup_error(
            errmsg,
            title='Error',
            text_color='black',
            background_color='white',
            button_color=('black', 'lightblue')
        )


    # Build summary plots (histograms of storm durations, magnitudes, and intensities)
    plt.figure(figsize=(8, 3))
    plt.subplot(1, 3, 1)
    data_to_plot = output['Duration']
    hist_values, bin_edges, _ = plt.hist(data_to_plot, bins=10, edgecolor='black')
    plt.locator_params(axis='x', nbins=5)
    lf = hist_values.max()
    plt.ylim(0, lf + 1)
    plt.xlabel('Storm Duration, hours')
    plt.ylabel('Frequency')

    plt.subplot(1, 3, 2)
    data_to_plot = output['Magnitude']
    hist_values, bin_edges, _ = plt.hist(data_to_plot, bins=10, edgecolor='black')
    plt.locator_params(axis='x', nbins=5)
    lf = hist_values.max()
    plt.ylim(0, lf + 1)
    plt.xlabel(f'Storm Magnitude, {tip_units}')
    plt.ylabel('Frequency')

    plt.subplot(1, 3, 3)
    data_to_plot = output['Storm_Intensity']
    hist_values, bin_edges, _ = plt.hist(data_to_plot, bins=10, edgecolor='black')
    plt.locator_params(axis='x', nbins=5)
    lf = hist_values.max()
    plt.ylim(0, lf + 1)
    plt.xlabel(f'Storm Intensity, {tip_units}/hr')
    plt.ylabel('Frequency')

    # Adjust spacing between subplots
    # plt.subplots_adjust(hspace=0.1)
    s_date = user_parameters_df['Parameter'][1]
    e_date = user_parameters_df['Parameter'][2]
    fig_title = (f'{output_name}\nDate Range: {s_date} - {e_date}')

    plt.suptitle(fig_title, fontsize=14)
    plt.tight_layout()
    # plt.show()
    sum_plot_name = f"{output_name}_summary_plot{plt_ext}"
    sum_plot_path = os.path.join(output_path, sum_plot_name)
    plt.savefig(sum_plot_path)

    # Produce plots of storm magnitude through the datset duration
    # set x axis to show all start dates of the storms
    # sdates_date = sdates.dt.date
    # Convert s_date and e_date to Series
    # s_date_series = pd.Series([s_date])  # full dataset start date
    # e_date_series = pd.Series([e_date])  # full dataset end date
    # x_dates = pd.concat([s_date_series, sdates_date, e_date_series], ignore_index=True)

    # full duration
    # start date
    start_date = datetime.strptime(s_date, '%Y-%m-%d').date()
    # end date
    end_date = datetime.strptime(e_date, '%Y-%m-%d').date()

    # generate full series plots
    # reducing number of labels on x-axis
    data_len = (end_date - start_date).days  # get number of days in the dataset
    days_2_disp = 10  # maximum number of days to display
    if data_len <= days_2_disp:
        num_dates = data_len
    else:
        num_dates = 10  # Set to the number of intervals you want between start_date and end_date

    # step_size = (end_date - start_date).days // (num_dates - 1)  # Calculate the step size
    # # get date series to plot
    # dates = [start_date + timedelta(days=i * step_size) for i in range(num_dates)]
    # x_dates = pd.Series(dates)  # final dates to label on x axis
    data_len = (end_date - start_date).days  # get number of days in the dataset
    days_2_disp = 10  # maximum number of days to display
    num_dates = days_2_disp + 1  # include start and end dates
    dates = [start_date + timedelta(days=int(i)) for i in np.linspace(0, data_len, num_dates, endpoint=True)]
    x_dates = pd.Series(dates)  # final dates to label on x axis

    # Plot storm magnitude through time and cumulative rainfall
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    # plot magnitude data
    ax1.bar(sdates, output['Magnitude'], width=2, align='center', color='blue')
    # ax2.plot(sdates, np.cumsum(output['Magnitude']), color='black')
    ax2.step(sdates, np.cumsum(output['Magnitude']), color='black', where='post')
    #  setup x axis labels
    ax1.xaxis.set_ticks(x_dates)
    x_dates_pd = pd.to_datetime(x_dates)
    plt.xlim(x_dates_pd.min().date(), x_dates_pd.max().date())
    date_format = mdates.DateFormatter('%Y-%m-%d')  # Format as YYYY-MM-DD
    ax1.xaxis.set_major_formatter(date_format)
    ax1.tick_params(axis='x', labelrotation=90)
    plt.subplots_adjust(bottom=0.3)  # Adjust the value as needed
    ax2.set_ylabel('Cumulative Rainfall, ' + tip_units, color='black')
    ax1.set_ylabel('Storm Magnitude,' + tip_units, color='blue')
    fig_title = (f'{output_name}: {start_date} - {end_date}')
    plt.title(fig_title, fontsize=14)
    sum_plot_name2 = f"{output_name}_magnitude_cumulative_rainfall_full{plt_ext}"
    sum_plot_path2 = os.path.join(output_path, sum_plot_name2)
    plt.savefig(sum_plot_path2)

    # Plot storm magnitude through time and 15-min rainfall intensity
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    # plot magnitude data
    ax1.bar(sdates, output['Magnitude'], width=2, align='center', color='blue')
    ax2.scatter(sdates, output['Peak_i15'], color='red', edgecolor='black', linewidth=0.3, zorder=3)  # .iloc[:, 0]
    #  setup x axis labels
    ax1.xaxis.set_ticks(x_dates)
    x_dates_pd = pd.to_datetime(x_dates)
    plt.xlim(x_dates_pd.min().date(), x_dates_pd.max().date())
    date_format = mdates.DateFormatter('%Y-%m-%d')  # Format as YYYY-MM-DD
    ax1.xaxis.set_major_formatter(date_format)
    ax1.tick_params(axis='x', labelrotation=90)
    plt.subplots_adjust(bottom=0.3)  # Adjust the value as needed
    ax2.set_ylabel(f'15-minute Intensity,  {tip_units}/hr', color='black')
    ax1.set_ylabel('Storm Magnitude,' + tip_units, color='blue')
    fig_title = (f'{output_name}: {start_date} - {end_date}')
    plt.title(fig_title, fontsize=14)
    sum_plot_name3 = f"{output_name}_magnitude_rainfall_intensity_full{plt_ext}"
    sum_plot_path3 = os.path.join(output_path, sum_plot_name3)
    plt.savefig(sum_plot_path3)

    # Collar et al., 2025 style plot for all storms w/ >2 tips
    profiles_for_plot = []

    for storm_name in storm_raw_profiles:
        raw_prof = storm_raw_profiles[storm_name]
        t = pd.Series(raw_prof.get("Cumulative Storm Time (hours)", []), dtype="float")
        p = pd.Series(raw_prof.get(f"Cumulative Rainfall ({tip_units})", []), dtype="float")

        if len(t) == 0 or len(p) == 0:
            continue

        # normalize
        t_tot = t.max()
        p_tot = p.max()
        if t_tot == 0 or p_tot == 0:
            continue

        profiles_for_plot.append((t / t_tot, p / p_tot))

    if profiles_for_plot:
        N = len(profiles_for_plot)


        alpha = max(math.exp(-math.sqrt(N) / 12.0), 0.05)
        lw = max(2.0 * (N ** (-0.175)), 0.5)

        fig, ax = plt.subplots()
        for t_norm, p_norm in profiles_for_plot:
            ax.plot(t_norm, p_norm, color="black", alpha=alpha, linewidth=lw)

        # 1:1 line in red
        ax.plot([0, 1], [0, 1], color="red", linewidth=1.0, linestyle="-", label="1:1")

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal", adjustable="box")  # square axes
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

        ax.set_xlabel("Elapsed time / Total time")
        ax.set_ylabel("Cumulative rainfall / Total rainfall")

        # only show legend if you want the 1:1 labeled
        ax.legend(loc="lower right")

        prof_plot_name = f"{output_name}_all_storm_profiles{plt_ext}"
        prof_plot_path = os.path.join(output_path, prof_plot_name)
        plt.tight_layout()
        plt.savefig(prof_plot_path)
        plt.close(fig)



    # add a subsampled time series if supplied
    if plot_end_date or plot_start_date:
        if plot_end_date:
            end_date = datetime.strptime(plot_end_date, '%Y-%m-%d').date()
        else:
            end_date = datetime.strptime(e_date, '%Y-%m-%d').date()

        if plot_start_date:
            start_date = datetime.strptime(plot_start_date, '%Y-%m-%d').date()
        else:
            start_date = datetime.strptime(s_date, '%Y-%m-%d').date()

        data_len = (end_date - start_date).days  # get number of days in the dataset
        days_2_disp = 10  # maximum number of days to display
        if data_len <= days_2_disp:
            num_dates = data_len
        else:
            num_dates = 10  # Set to the number of intervals you want between start_date and end_date

        data_len = (end_date - start_date).days  # get number of days in the dataset
        days_2_disp = 10  # maximum number of days to display
        num_dates = days_2_disp + 1  # include start and end dates
        dates = [start_date + timedelta(days=int(i)) for i in np.linspace(0, data_len, num_dates, endpoint=True)]
        x_dates = pd.Series(dates)  # final dates to label on x axis

        # step_size = (end_date - start_date).days // (num_dates - 1)  # Calculate the step size
        # # get date series to plot
        # dates = [start_date + timedelta(days=i * step_size) for i in range(num_dates)]
        # x_dates = pd.Series(dates)  # final dates to label on x axis

        # Plot storm magnitude through time and cumulative rainfall
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        # plot magnitude data
        ax1.bar(sdates, output['Magnitude'], width=2, align='center', color='blue')
        ax2.step(sdates, np.cumsum(output['Magnitude']), color='black', where='post')
        #  setup x axis labels
        ax1.xaxis.set_ticks(x_dates)
        x_dates_pd = pd.to_datetime(x_dates)
        plt.xlim(x_dates_pd.min().date(), x_dates_pd.max().date())
        date_format = mdates.DateFormatter('%Y-%m-%d')  # Format as YYYY-MM-DD
        ax1.xaxis.set_major_formatter(date_format)
        ax1.tick_params(axis='x', labelrotation=90)
        plt.subplots_adjust(bottom=0.3)  # Adjust the value as needed
        ax2.set_ylabel('Cumulative Rainfall, ' + tip_units, color='black')
        ax1.set_ylabel('Storm Magnitude,' + tip_units, color='blue')
        fig_title = (f'{output_name}: {start_date} - {end_date}')
        plt.title(fig_title, fontsize=14)
        sum_plot_name2 = f"{output_name}_magnitude_cumulative_rainfall_sub{plt_ext}"
        sum_plot_path2 = os.path.join(output_path, sum_plot_name2)
        plt.savefig(sum_plot_path2)

        # Plot storm magnitude through time and 15-min rainfall intensity
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        # plot magnitude data
        ax1.bar(sdates, output['Magnitude'], width=2, align='center', color='blue')
        ax2.scatter(sdates, output['Peak_i15'], color='red', edgecolor='black', linewidth=0.3, zorder=3)
        #  setup x axis labels
        ax1.xaxis.set_ticks(x_dates)
        x_dates_pd = pd.to_datetime(x_dates)
        plt.xlim(x_dates_pd.min().date(), x_dates_pd.max().date())
        date_format = mdates.DateFormatter('%Y-%m-%d')  # Format as YYYY-MM-DD
        ax1.xaxis.set_major_formatter(date_format)
        ax1.tick_params(axis='x', labelrotation=90)
        plt.subplots_adjust(bottom=0.3)  # Adjust the value as needed
        ax2.set_ylabel(f'15-minute Intensity,  {tip_units}/hr', color='black')
        ax1.set_ylabel('Storm Magnitude,' + tip_units, color='blue')
        fig_title = (f'{output_name}: {start_date} - {end_date}')
        plt.title(fig_title, fontsize=14)
        sum_plot_name3 = f"{output_name}_magnitude_rainfall_intensity_sub{plt_ext}"
        sum_plot_path3 = os.path.join(output_path, sum_plot_name3)
        plt.savefig(sum_plot_path3)

    return errmsg

