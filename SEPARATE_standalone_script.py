"""
SEPARATE (Standalone Version)
Storm Event Partitioning And Rainfall Analytics for Tipping-bucket rain gauge data Evaluation

Authors:
    Scott R. David (Utah State University)
    Brendan P. Murphy (Simon Fraser University)

Version: 1.1
Last Updated: 2025-12-01
License: MIT License

Description:
    This standalone version of SEPARATE processes tipping bucket rain gauge (TBRG) data to identify and
    analyze discrete storm events. It uses a fixed minimum inter-event time (MIT) approach, with options
    for user-defined or statistically derived separation criteria (e.g., Independent Storms Criterion).

    The script is designed for batch or automated use and does not launch the graphical user interface (GUI).
    Users must configure all input file paths, parameters, and analysis options directly within this script.

Key Features:
    - Compatible with both fixed-interval and cumulative tip rainfall records
    - Supports user-defined or statistical storm separation criteria
    - Calculates storm duration, magnitude, average and peak intensities
    - Exports tabular and graphical outputs to user-defined directories

Usage Notes:
    - Edit the `filename`, `output_path`, and related input parameters below before running.
    - Ensure required dependencies are installed (see below).
    - Outputs will be saved in the specified directory, including summary tables and storm figures.

Repository:
    https://github.com/WatershedsWildfireResearchCollaborative/SEPARATE

Dependencies:
    Python >= 3.10, < 3.13
    pandas, numpy, matplotlib, scipy

Citation:
    Murphy & David (2024), [submitted to JOSS]
"""


# %% import required packages
software_metadata = ['SEPARATE - Summary Storm Event Output Table', 'Version 1.1 (12/01/2025)',
                     'Licensed under the MIT License.']
import numpy as np
from datetime import datetime
import pandas as pd
import os

# from functions.build_SEPARATE_layout import build_SEPARATE_layout
try:
    # Try import if installed via pip (PyPI)
    from separate.functions import SEPARATE_FUNCTIONS as sf
    from separate.functions import SEPARATE_utilities as su
except ImportError:
    try:
        # Fallback if running from a cloned repo
        import functions.SEPARATE_FUNCTIONS as sf
        import functions.SEPARATE_utilities as su
        print("Using local module imports (from cloned repo).")
    except ImportError:
        raise ImportError(
            "Could not import SEPARATE modules.\n"
            "Make sure you have installed the package using pip (`pip install separate`) "
            "or are running this script from the cloned repository with the correct folder structure."
        )

# ===================== USER CONFIGURATION SECTION ===================== #
# Define all user-specified inputs here before running the script.
# ====================================================================== #

# --- INPUT FILE ---
filename = r'C:\Users\Scott\Desktop\Example_Datasets\ExampleData_FixedInterval.xlsx'  # Path to input .xlsx or .csv file
sheetname = ''  # (Optional) Name of sheet in Excel file; leave blank to use the first sheet

# --- TIP DATA SETTINGS ---
tip_type = 'Fixed Interval'  # Options: 'Cumulative Tips' or 'Fixed Interval'
tip_mag = 0.2                 # Tip volume (e.g., 0.2 mm per tip)
tip_units = 'mm'              # Units of rainfall depth: 'mm', 'cm', or 'in'

# --- STORM SEPARATION CRITERION ---
storm_gap_type_name = 'Independent Storms Criterion (ISC)'  # Options: 'User-Defined MIT (UDM)', 'Independent Storms Criterion (ISC)'
storm_gap = ''              # If using UDM, specify fixed inter-event time in hours
isc_time = 48               # If using ISC, specify max inter-event time to test in hours (recommended default: 48)

# --- FILTERING OPTIONS ---
min_depth_TF = False        # Apply minimum storm depth threshold? (True/False)
min_depth = 0.2             # Minimum storm depth (same units as tip_mag); only used if min_depth_TF = True

min_duration_TF = False     # Apply minimum storm duration threshold? (True/False)
min_duration = 0.5          # Minimum storm duration in hours; only used if min_duration_TF = True

# --- OUTPUT SETTINGS ---
output_path = r'C:\Users\Scott\Desktop\final'  # Output folder for results
output_name = 'example_fixed'                           # Prefix used for output file naming

plt_ext = '.png'           # Plot image format: '.png', '.jpg', '.eps', or '.pdf'
plot_start_date = ''       # Optional: Limit plots to start on this date ('YYYY-MM-DD'), or leave blank
plot_end_date = ''         # Optional: Limit plots to end on this date ('YYYY-MM-DD'), or leave blank

data_opt = True            # Save raw & interpolated storm data for each event? (True/False)
plot_opt = True            # Generate storm plots? (True/False)
plot_int = 15              # Storm intensity duration to use for peak intensity plot/profile (in minutes)


# ....................Adjust naming conventions and inputs...................
# Adjust some parameter names to make them shorter
if storm_gap_type_name == 'User-Defined MIT (UDM)':
    storm_gap_type = 'UDM'
elif storm_gap_type_name == 'Travel Time Criterion (TTC)': # note this is not implemented yet
    storm_gap_type = 'RTTC'
elif storm_gap_type_name == 'Independent Storms Criterion (ISC)':
    storm_gap_type = 'ISC'
    if isc_time >48:
        isc_warning =  """
        Warning:
        IC Upper Limit Warning: Using testing intervals greater than SEPARATE’s default value of 48 hours will 
        result in slower processing times. Conversely, while using values less than the default value of 
        48 hours may increase processing times, this can also lead to poorer fits and lower confidence in the selection of the MIT
        """
        print(isc_warning)

else:
    storm_gap_type = 'ISC'
    print('Storm gap type not valid. Defaulting to Statistically Independent Storms')

# if minimum depth is not selected default the value to None
if not min_depth_TF :
    min_depth = None

# if minimum duration is not selected default the value to None
if not min_duration_TF:
    min_duration = None

# if providing a start and end date for the final plots then check the format is correct
tf_date = True
if plot_start_date:
    try:
        datetime.strptime(plot_start_date, '%Y-%m-%d').date()
    except:
        tf_date = False
        error_msg_dates = "Input date formats can not be interpreted please input date as YYYY-MM-DD "
        raise ValueError(error_msg_dates)


if plot_end_date:
    try:
        datetime.strptime(plot_end_date, '%Y-%m-%d').date()
    except:
        tf_date = False
        error_msg_dates = "Input date formats can not be interpreted please input date as YYYY-MM-DD "
        raise ValueError(error_msg_dates)


# Check all user inputs and data types are correct
# Build dict to use existing validation functions
input_args = {
    "input_file": filename,
    "sheet_name": sheetname,
    "Tip_Record_Type": tip_type,
    "tip_mag": tip_mag,
    "units": tip_units,
    "Storm_Gap_Type": storm_gap_type_name,
    "fixed_mit": storm_gap,
    "isc_interval": isc_time,
    "min_depth_bool": min_depth_TF,
    "min_depth": min_depth,
    "min_duration_bool": min_duration_TF,
    "min_duration": min_duration,
    "output_path": output_path,
    "output_name": output_name,
    "plt_ext": plt_ext,
    "plot_int": plot_int,
    "data_opt": data_opt,
    "plot_opt": plot_opt,
    "plt_start_date": plot_start_date,
    "plt_end_date": plot_end_date,
}

# Required types dictionary
dtype_args = {
    "input_file": "str",
    "sheet_name": "str",
    "Tip_Record_Type": "str",
    "tip_mag": "float",
    "units": "str",
    "Storm_Gap_Type": "str",
    "fixed_mit": "float",
    "isc_interval": "float",
    "min_depth_bool": "bool",
    "min_depth": "float",
    "min_duration_bool": "bool",
    "min_duration": "float",
    "output_path": "str",
    "output_name": "str",
    "plt_ext": "str",
    "plot_int": "float",
    "data_opt": "bool",
    "plot_opt": "bool",
    "plt_start_date": "str",
    "plt_end_date": "str",
}

# Check for required fields
required_fields = su.check_for_required_fields(input_args)
tf_fields, missing_fields = su.is_gui_filled(input_args, required_fields)
if not tf_fields:
    raise ValueError(f"Missing required fields: {missing_fields}")
# Check input data types
tf_type, type_error_msg = su.check_input_type(input_args, required_fields, dtype_args)
if not tf_type:
    raise ValueError(f"Input type error:\n{type_error_msg}")


#%%  ................................Execute SEPARATE algorithm...........................................

# get input file type
_, input_ext = os.path.splitext(filename)
input_ext = input_ext.lower()

# load in data from Excel or csv
#Read-in Data & Process TBRG Data
tip_datetime, tip_depth, logging_interval, start_date, end_date = sf.separate_preprocessing(filename, sheetname,
                                                                                            tip_type, tip_mag)

# check that the input data is consistent with the user input tip type
# tip_is_valid, inferred = su.validate_tip_type(tip_datetime, tip_type)
valid_tip, inferred_tip, raw_datetime = su.validate_tip_type_from_raw_file(filename, sheetname,
                                                                           tip_type)

if not valid_tip:
    print(f"Warning: Tip type mismatch.\nYou selected '{tip_type}', but SEPARATE inferred '{inferred_tip}'")


# get minimum time between storms in hours
if storm_gap_type == 'ISC':
    isc_t_max =  isc_time # maximum duration to look over for finding minimum inter-event time

    # Check for extreme inter-event intervals
    if isc_t_max > 500:
        ic_error = (
            "IC Upper Limit Error: Testing inter-event intervals greater than 500 hours are "
            "not currently allowed in SEPARATE. Reduce the time of your upper limit."
        )
        raise ValueError(ic_error)


    if isc_t_max <= 1:
        low_ic_error = (
            "IC Upper Limit Error: Testing inter-event intervals less than or equal to 1 hour are "
            "not currently allowed in SEPARATE. Increase the time of your upper limit.")
        raise ValueError(low_ic_error)


    # create folder for output plot
    gap_plots_folder = output_name + '_ISC_analysis'
    gap_plots_path = os.path.join(output_path, gap_plots_folder)
    if not os.path.exists(gap_plots_path):
        os.makedirs(gap_plots_path, exist_ok=True)


    # compute storm gap using optimized method
    Fixed_MIT, mean_tb, CV_IET, mean_IET, std_IET, ISC_testintervals, StormNumsRec= sf.separate_ISC(tip_datetime,
                                                                                                    tip_depth,
                                                                                                    isc_t_max,
                                                                                                    min_depth,
                                                                                                    min_duration,
                                                                                                    gap_plots_path,
                                                                                                    output_name,
                                                                                                    plt_ext)

elif storm_gap_type == 'RTTC':
    # note this is not actively included in separate and will be available in future releases
    inter_event_interval = ''
    gap_plots_path = ''  # dummy value
    storm_gap = ''
    Fixed_MIT = 0 # calculate travel time Solyom & Tucker (2004), doi:10.1029/2003JF000032
    # Tt_max = sf.calculate_Tt_max(flow_dist, relief, BF_depth, n)
    # Fixed_MIT = Tt_max


elif storm_gap_type == 'UDM':
    Fixed_MIT = storm_gap
    gap_plots_path = ''  # dummy value
    inter_event_interval = ''
else:
    Fixed_MIT = 0
    raise ValueError('Storm gap type not valid')


# separate storms

# identifying breaks in storms
storms, interevent_times = sf.separate_storms(tip_datetime, tip_depth, Fixed_MIT)

# filter for additional criteria
storm_data, filtered_interevent_times, N_nofilter, N_suppressed  = sf.separate_filter(storms, interevent_times,
                                                                                      min_depth,min_duration)

if storm_gap_type == "ISC":
    sf.plot_inter_event_histogram(filtered_interevent_times, mean_tb, Fixed_MIT, gap_plots_path,
                                  output_name, plt_ext)

total_storms = N_nofilter
suppressed_storms = N_suppressed
N_storms = total_storms - suppressed_storms
# % Storm Profiling and Peak Intensity Calculation

# setup rainfall intensity intervals to calculate
I_intervals = np.array([5, 10, 15, 30, 60])  # Storm Intensity Intervals, units: minutes
# ensure the rain fall intensity is not shorter than the logging interval
I_intervals_chk = I_intervals[I_intervals > logging_interval]
I_intervals = I_intervals / 60.0  # Convert Intensity Intervals to Hours
if len(I_intervals_chk) < 1:
    errmsg = ("Logging interval is greater than storm intensity intervals.\nPlease specify a user "
              "defined interval that is longer than the logging intervals.")
    raise ValueError(errmsg)

if plot_opt:
    plots_folder = output_name + '_storm_plots'
    plots_path = os.path.join(output_path, plots_folder)
    if not os.path.exists(plots_path):
        os.makedirs(plots_path, exist_ok=True)
else:
    plots_path = None

# get all the storm dates for naming
# extract all storm start dates (as date objects) from storm_data.
all_storm_dates = [storm_data[i]['start'].date() for i in range(len(storm_data))]
storm_name_dates = sf.rename_repeating_dates(all_storm_dates)
# change all - to _
storm_name_dates = [s.replace('-', '_') for s in storm_name_dates]

# initialize storm record
storm_record = []
storm_profiles = {}
storm_raw_profiles = {}
for i in range(N_storms):
    StormIDX = i  # 0-based index
    # get the name (w/ date) for the storm
    storm_id_name = f"{output_name}_{storm_name_dates[i]}"
    # print(storm_id_name)
    # extract the storm profile
    iD_Mag, iD_time, R_fit, t_fit, tip_idx, cum_rain, duration_min = sf.separate_profiler(StormIDX, storm_data,
                                                                                          tip_datetime, tip_depth,
                                                                                          plot_int)

    start_time_abs = storm_data[StormIDX]['start']
    peakiD_all = []

    # return the raw data
    # cumulative time in hours
    dataset_name = storm_id_name  # set a dataset name for the dict
    if tip_idx is not None and len(tip_idx) > 0:
        cumulative_time_hours = ((tip_datetime[tip_idx] - tip_datetime[tip_idx].iloc[0]).dt.total_seconds() / 3600.0)
        storm_raw_profiles[dataset_name] = {f'TBRG Time Stamp': tip_datetime[tip_idx],  # win_range,
                                            f'Cumulative Storm Time (hours)':
                                                np.round(cumulative_time_hours, 2),  # win_range,
                                            f'Cumulative Rainfall ({tip_units})':
                                                np.round(cum_rain, 2)}

    for interval in I_intervals*60:  # Convert hours back to minutes for intensity intervals
        # calculate the peak intensity
        peakiDs = sf.separate_peak_intensity(start_time_abs, t_fit, R_fit, interval)
        # peakids =intensity_interval, peakiD_Mag, peakiD_datetime, peakiD_time_relative
        peakiD_all.append(peakiDs) # log the peak ids for each interval

        # optionally log the storm profile data
        if data_opt and plot_int==interval and ~np.isnan(peakiDs[1]):
            # cumulative time in hours
            cumulative_time_hours = (tip_datetime[tip_idx] - tip_datetime[tip_idx].iloc[0]).dt.total_seconds() / 3600.0
            peak_dt_str = peakiDs[2].strftime('%Y-%m-%d %H:%M:%S')
            # store the profile storm profile data
            dataset_name = storm_id_name
            # store the profile storm profile data
            storm_meta_data = {f'Storm ID:': f'{storm_id_name}',
                               f'Start Date & Time:': f'{start_time_abs}',
                               f'Storm Duration (hrs):': f'{np.round(duration_min / 60, 2)}',
                               f'Depth ({tip_units}):': f'{np.round(len(tip_idx) * tip_mag, 2)}',
                               f'Peak {int(interval)}-min Intensity ({tip_units}/hr):': f'{round(peakiDs[1], 2)}',
                               f'Peak Intensity Date and Time:': f'{peak_dt_str}',
                               f'Number of Tips': f'{len(tip_idx)}'}

            storm_profiles[dataset_name] = {f'Cumulative Storm Time (hours)': t_fit,
                                            # interpolated time range since start of storm
                                            f'{plot_int}-min Intensity ({tip_units}/hr)': R_fit,
                                            f'Storm Metadata': storm_meta_data}

        # optionally plot the storm profile and peak intensity
        if plot_opt and plot_int==interval and ~np.isnan(peakiDs[1]):
            peak_dt_str = peakiDs[2].strftime('%Y-%m-%d %H:%M:%S')
            fig_title = (f'{output_name}\n'
                         f'Storm ID:{storm_id_name}\n'  # int(storms_in[i])
                         f'Start Date & Time: {start_time_abs}\n'
                         f'Depth ({tip_units}): {np.round(len(tip_idx)*tip_mag, 2)}\n'
                         f'Peak {int(interval)}-min Intensity ({tip_units}/hr): {round(peakiDs[1], 2)}\n'
                         f'Peak Intensity Date and Time:{peak_dt_str}\n'
                         )

            sf.separate_profile_plots(interval, tip_units, peakiDs[1], peakiDs[3], t_fit, R_fit,tip_idx, iD_time, iD_Mag,
                                      fig_title, plots_path, storm_id_name, plt_ext)


    # Combine storm data and peak intensity results.
    combined_record = storm_data[StormIDX].copy()
    combined_record['StormID'] = storm_id_name
    for idx, interval in enumerate(I_intervals*60):
        key_intensity = f'Peak_i{int(interval)}'
        key_time = f'Peak_i{int(interval)}_time'
        combined_record[key_intensity] = peakiD_all[idx][1]
        combined_record[key_time] = peakiD_all[idx][2]
    storm_record.append(combined_record)

# build header for output files
if tip_type == 'Cumulative Tips':  # if cumulative tips then no logging interval
    logging_interval = 'N/A'

# if min duration is not provided write N/A to header
if not min_duration_TF:
    min_duration = 'N/A'

# if min depth is not provided write N/A to header
if not min_depth_TF:
    min_depth = 'N/A'

# build header for output files
header_parameters = {
    'Dataset ID:': f'{output_name}',
    'Record Start Date:': f'{start_date}',
    'Record End Date:': f'{end_date}',
    'Tipping Bucket Record Type:': f'{tip_type}',
    'Tip Magnitude:': f'{tip_mag}',
    'Tip Units:': f'{tip_units}',
    'Logging Interval (min):': f'{logging_interval}',
    'Fixed MIT Selection Criterion:': f'{storm_gap_type_name}',
    'Minimum Inter-Event Time (hours):': f'{np.round(Fixed_MIT, 2)}',
    'Total Number of Storms in Record:': f'{total_storms}',
    'Number of Storms Suppressed:': f'{suppressed_storms}',
    f'Minimum Storm Depth ({tip_units}):': f'{min_depth}',
    f'Minimum Storm Duration (hrs):': f'{min_duration}',
    'Record Separated On:': f'{datetime.now().date()}',
    'Data Input File:': f'{filename}'
    }
# if storm_gap_type == 'RTTC':
#     # header_parameters.update({
#     #     'Flow Distance (km):': f'{flow_dist}',
#     #     'Relief (degrees):': f'{relief}',
#     #     'Bankfull Depth (m):': f'{BF_depth}',
#     #     'Manning\'s n (s/m^(1/3))': f'{n}'
#     # })
#

n_storms_warning = (
    "*Note: The ‘Number of Storms in Record’ column includes all partitioned storm events, including those less "
    "than the (optional) minimum depth criterion.")
header_parameters.update({
    n_storms_warning: ' '
})

# create output spreadsheets

# first output the ISC results
# if optimized output the fitting parameters to a file
if storm_gap_type == 'ISC':
    # will likely need some rebuilding for new output structures
    sf.output_fitting_parameters_to_file(software_metadata, header_parameters, CV_IET, mean_IET,std_IET,
                                         ISC_testintervals, StormNumsRec, output_name, gap_plots_path, input_ext)

#% Creating final output tables and plots
print('finalizing outputs')

# build output dataframe
output = pd.DataFrame(storm_record)

# rename fields for Excel/csv outputs
# Rename columns: # Note the separate outputs function requires these names
output.rename(columns={
    'start': 'Start',
    'end': 'End',
    'duration': 'Duration',
    'magnitude': 'Depth',
    'intensity_avg': 'Average_Intensity',
}, inplace=True)

# Check Results Before Writing Outputs
# Basic storm data plus peak intensities for each intensity interval.
columns = ['StormID', 'Start', 'End', 'Duration', 'Depth', 'Average_Intensity'] + \
          [f'Peak_i{int(60 * I_int)}' for I_int in I_intervals] + \
          [f'Peak_i{int(60 * I_int)}_time' for I_int in I_intervals]

# Define units for each column (for header purposes).
units = ['Unique Identifier', 'date_time', 'date_time', 'hours', tip_units, tip_units + '/hr'] + \
        [tip_units + '/hr'] * len(I_intervals) + ['date_time'] * len(I_intervals)

# output = pd.DataFrame(storm_record, columns=columns)
output=output.reindex(columns=columns)


# check that all values are not nan
if output[f'Peak_i{int(60 * I_intervals[0])}'].isnull().all(): # np.all(np.isnan(output[f'Peak_i{int(60 * I_intervals[0])}'])):
    errmsg = 'Rainfall Intensity Interval Greater Than All Storm Durations\n'
    raise ValueError(errmsg)
else:
    errmsg = None

# create final outputs
errmsg = sf.separate_outputs(output, storm_profiles, storm_raw_profiles, tip_units,
                                 I_intervals, data_opt, header_parameters, output_path,
                                 output_name, plot_int, plt_ext, plot_start_date, plot_end_date,
                                 software_metadata, columns, units, input_ext)

# update progress bar
print ('complete')

