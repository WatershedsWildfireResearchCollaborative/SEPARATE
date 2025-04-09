# %% import required packages
import PySimpleGUI as sg
import numpy as np
from datetime import datetime
from functions.build_SEPARATE_layout import build_SEPARATE_layout
import functions.SEPARATE_utilities as su
import functions.SEPARATE_FUNCTIONS as sf
import pandas as pd
import os



software_metadata = ['SEPARATE - Summary Storm Event Output Table', 'Version 1.0 (03/01/2025)',
                     'Licensed under the MIT License.']
# ....................Load in user inputs to variables...................
# update the progress bar with 5 progress
# Set the input file paths
filename = r'C:\Users\Scott\Desktop\McDougall_South_Summer2024_Cleaned.xlsx'  # input file
# filename = r'C:\Users\Scott\Desktop\syn_cum.xlsx'  # input file
# optionally define sheet name
sheetname = ''

# tipping and logging data
tip_type = 'Cumulative Tips'  # Set tip record type
# tip_type = 'Fixed Interval'  # Set tip record type

tip_mag = 0.2  # set the magnitude of each tip

tip_units = 'mm'

# storm gap partitioning data
# storm gap type
storm_gap_type_name = 'Independent Storms Criterion (ISC)'  # set the storm gap type

# if user defined storm gap set value
storm_gap = ''  # set the storm gap interval

# if statistically independent storm gap set value
isc_time = 48  # max inter-event time

# min storm depth boolean
min_depth_TF = False
# minimum storm depth
min_depth = 0.2

# min storm duration boolean
min_duration_TF = False
# minimum storm duration
min_duration = 0.5

# output options
output_path = r'C:\Users\Scott\Desktop\debug'

output_name = 'hist'

plt_ext = '.png'

plot_start_date = ''

plot_end_date = ''

data_opt = True

plot_opt = True

plot_int = 15

# ....................Adjust naming conventions and inputs...................
# Adjust some parameter names to make them shorter
if storm_gap_type_name == 'User-Defined MIT (UDM)':
    storm_gap_type = 'UDM'
elif storm_gap_type_name == 'Travel Time Criterion (TTC)':
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
    #     sg.popup_no_wait(isc_warning, title="Warning",text_color='black', background_color='white',
    #              button_color=('black', 'lightblue'))

else:
    storm_gap_type = 'ISC'
    print('Storm gap type not valid. Defaulting to Statistically Independent Storms')
    # print('Turn this into a warning message')

# if minimum depth is not selected default the value to 0
if not min_depth_TF :
    min_depth = None

# if minimum duration is not selected default the value to 0
if not min_duration_TF:
    min_duration = None

# if providing a start and end date for the final plots then check the format is correct
tf_date = True
if plot_start_date:
    try:
        datetime.strptime(plot_start_date, '%Y-%m-%d').date()
    except:
        error_msg_dates = "Input date formats can not be interpreted please input date as YYYY-MM-DD "
        # sg.popup_error(error_msg_dates, title='Invalid Dates', text_color='black',
        #                background_color='white', button_color=('black', 'lightblue'))
        tf_date = False

if plot_end_date:
    try:
        datetime.strptime(plot_end_date, '%Y-%m-%d').date()
    except:
        error_msg_dates = "Input date formats can not be interpreted please input date as YYYY-MM-DD "
        # sg.popup_error(error_msg_dates, title='Invalid Dates', text_color='black',
        #                background_color='white', button_color=('black', 'lightblue'))
        tf_date = False



#%%  ................................Execute SEPARATE algorithm...........................................

# load in data from excel or csv
#Read-in Data & Process TBRG Data
tip_datetime, tip_depth, logging_interval, start_date, end_date = sf.separate_preprocessing(filename, sheetname, tip_type, tip_mag)

# df, c = sf.load_data(filename, sheetname)
# # filename =r'C:\Users\Scott\Desktop\High_Data_Rainstorm.xlsx'
#
# # Assuming df is your DataFrame and c[0] is the column of interest
# df[c[0]] = pd.to_datetime(df[c[0]], errors='coerce')
#
# # Create Timestamp Record of Tips:
# timestamp_date, cum_rainfall, errmsg = sf.create_time_stamp_record(df, c, tip_type, tip_mag)



# update progress bar


# get minimum time between storms in hours
if storm_gap_type == 'ISC':
    isc_t_max =  isc_time # maximum duration to look over for finding minimum inter-event time

    # Check for extreme inter-event intervals
    if isc_t_max > 500:
        ic_error = (
            "IC Upper Limit Error: Testing inter-event intervals greater than 500 hours are "
            "not currently allowed in SEPARATE. Reduce the time of your upper limit."
        )
        sg.popup_error(ic_error, title='Error', text_color='black', background_color='white',
                       button_color=('black', 'lightblue'))

    if isc_t_max <= 1:
        low_ic_error = (
            "IC Upper Limit Error: Testing inter-event intervals less than or equal to 1 hour are "
            "not currently allowed in SEPARATE. Increase the time of your upper limit."
        )
        sg.popup_error(low_ic_error, title='Error', text_color='black', background_color='white',
                       button_color=('black', 'lightblue'))

    # create folder for output plot
    gap_plots_folder = output_name + '_ISC_analysis'
    gap_plots_path = os.path.join(output_path, gap_plots_folder)
    if not os.path.exists(gap_plots_path):
        os.makedirs(gap_plots_path, exist_ok=True)


    # compute storm gap using optimized method
    Fixed_MIT, CV_IET, mean_IET, std_IET, ISC_testintervals, StormNumsRec= sf.separate_ISC(tip_datetime, tip_depth, isc_t_max, min_depth, min_duration,
                           gap_plots_path, output_name, plt_ext)

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
storm_data, filtered_interevent_times, N_nofilter, N_suppressed  = sf.separate_filter(storms,
                                                                                               interevent_times,
                                                                                               min_depth,
                                                                                               min_duration)
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
    sg.popup_error(errmsg, title='Error', text_color='black', background_color='white',
                   button_color=('black', 'lightblue'))
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
    iD_Mag, iD_time, R_fit, t_fit, tip_idx, cum_rain, duration_min = sf.separate_profiler(StormIDX, storm_data, tip_datetime, tip_depth, plot_int)

    start_time_abs = storm_data[StormIDX]['start']
    peakiD_all = []



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
            storm_meta_data = {f'Storm ID:': f'{storm_id_name}',
                                   f'Start Date & Time:': f'{start_time_abs}',
                                   f'Storm Duration (hrs):': f'{np.round(duration_min/60, 2)}',
                                   f'Storm Magnitude ({tip_units}):': f'{np.round(len(tip_idx)*tip_mag, 2)}',
                                   f'Peak {int(interval)}-min Intensity ({tip_units}/hr):': f'{round(peakiDs[1], 2)}',
                                   f'Peak Intensity Date and Time:': f'{peak_dt_str}',
                                   f'Number of Tips': f'{len(tip_idx)}'}

            storm_profiles[dataset_name] = {f'Cumulative Storm Time (hours)': t_fit,
                                            # interpolated time range since start of storm
                                            f'{plot_int}-min Intensity ({tip_units}/hr)': R_fit,
                                            f'Storm Metadata': storm_meta_data}
            # # return the raw data
            storm_raw_profiles[dataset_name] = {f'TBRG Time Stamp': tip_datetime[tip_idx],  # win_range,
                                                f'Cumulative Storm Time (hours)': np.round(cumulative_time_hours,2),  # win_range,
                                                f'Cumulative Rainfall ({tip_units})': cum_rain}

        # optionally plot the storm profile and peak intensity
        if plot_opt and plot_int==interval and ~np.isnan(peakiDs[1]):
            peak_dt_str = peakiDs[2].strftime('%Y-%m-%d %H:%M:%S')
            fig_title = (f'{output_name}\n'
                         f'Storm ID:{storm_id_name}\n'  # int(storms_in[i])
                         f'Start Date & Time: {start_time_abs}\n'
                         f'Storm Magnitude ({tip_units}): {np.round(len(tip_idx)*tip_mag, 2)}\n'
                         f'Peak {int(interval)}-min Intensity ({tip_units}/hr): {round(peakiDs[1], 2)}\n'
                         f'Peak Intensity Date and Time:{peak_dt_str}\n'
                         )
            sf.separate_profile_plots(interval, tip_units, peakiDs[1], peakiDs[3], t_fit, R_fit,tip_idx, iD_time, iD_Mag, fig_title, plots_path, storm_id_name, plt_ext)


    # Combine storm data and peak intensity results.
    combined_record = storm_data[StormIDX].copy()
    combined_record['StormID'] = storm_id_name
    for idx, interval in enumerate(I_intervals*60):
        key_intensity = f'Peak_i{int(interval)}'
        key_time = f'Peak_i{int(interval)}_time'
        combined_record[key_intensity] = peakiD_all[idx][1]
        combined_record[key_time] = peakiD_all[idx][2]
    storm_record.append(combined_record)


# Generate output excel file
# build header for output files
header_parameters = {
    'Dataset ID:': f'{output_name}',
    'Record Start Date:': f'{start_date}',
    'Record End Date:': f'{end_date}',
    'Tipping Bucket Record Type:': f'{tip_type}',
    'Tip Magnitude:': f'{tip_mag}',
    'Tip Units:': f'{tip_units}',
    'Logging Interval (min):': f'{logging_interval}', # should make this only included it fixed logging interval
    'Fixed MIT Selection Criterion:': f'{storm_gap_type_name}',
    'Minimum Inter-Event Time (hours):': f'{np.round(Fixed_MIT, 2)}',
    'Number of Storms in Record:': f'{total_storms}',
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
                                         ISC_testintervals, StormNumsRec, output_name, gap_plots_path)

#% Creating final output tables and plots
print('finalizing outputs')

# build output dataframe
output = pd.DataFrame(storm_record)

# rename fields for excel outputs
# 2. Rename columns:
output.rename(columns={
    'start': 'Start',
    'end': 'End',
    'duration': 'Duration',
    'magnitude': 'Magnitude',
    'intensity_avg': 'Storm_Intensity',
    # ... etc. ...
}, inplace=True)

# Check Results Before Writing Outputs
columns = ['StormID', 'Start', 'End', 'Duration', 'Magnitude', 'Storm_Intensity'] + [
    f'Peak_i{int(60 * I_int)}' for I_int in I_intervals] + [
              f'Peak_i{int(60 * I_int)}_time' for I_int in I_intervals]
# Define units for each column (for header purposes).

units = ['Unique Identifier', 'date_time', 'date_time', 'hours', tip_units, tip_units + '/hr'] + \
        [tip_units + '/hr'] * len(I_intervals) + ['date_time'] * len(I_intervals)
# output = pd.DataFrame(storm_record, columns=columns)
output=output.reindex(columns=columns)


# check that all values are not nan
if output[f'Peak_i{int(60 * I_intervals[0])}'].isnull().all(): # np.all(np.isnan(output[f'Peak_i{int(60 * I_intervals[0])}'])):
    errmsg = 'Rainfall Intensity Interval Greater Than All Storm Durations\n'
    sg.popup_error(errmsg, title='Error', text_color='black', background_color='white',
                   button_color=('black', 'lightblue'))
    # raise ValueError(errmsg)
else:
    errmsg = None

# create final outputs
errmsg = sf.separate_outputs(output, storm_profiles, storm_raw_profiles, tip_units,
                                 I_intervals, data_opt, header_parameters, output_path,
                                 output_name, plot_int, plt_ext, plot_start_date, plot_end_date,
                                 software_metadata, columns, units)

# update progress bar
print ('complete')

