# %% import required packages
import PySimpleGUI as sg
import numpy as np
from datetime import datetime
from functions.build_SEPARATE_layout import build_SEPARATE_layout
import  functions.SEPARATE_utilities as su
import functions.SEPARATE_FUNCTIONS as sf
import pandas as pd
import os
from scipy import stats


# https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
# todo turn main on for distro
# def main():
# %% setup gui parameters -- most of this occurs in the build_separate_layout function
# Set up the color schemes, font sizes, and other toggles for the gui
resize = True  # allow the user to resize the window
clean_variables = False
# import the layout from build_SEPARTAE_layout.py
layout, background_color, help_messages = build_SEPARATE_layout()

# Create the window
window = sg.Window('SEPARATE v1.0', layout, resizable=resize, background_color=background_color, finalize=True)

# software_metadata = ['SEPARATE - Summary Storm Event Output Table', 'Version 1.0 (03/01/2025)',
#                      'License/Copyright Details', 'Requested reference: Murphy & David (2024), Journal, etc.',
#                      'Published DOI', 'https://github.com/WatershedsWildfireResearchCollaborative/SEPARATE']
software_metadata = ['SEPARATE - Summary Storm Event Output Table', 'Version 1.0 (03/01/2025)',
                     'Licensed under the MIT License.']
# %% Running the GUI loop
while True:
    event, args = window.read()

    # Exit the program if the window is closed or Exit button is pressed
    if event == sg.WINDOW_CLOSED:
        break
    # display help messages when info button is clicked
    if event in help_messages:
        sg.popup(help_messages[event], title='Info',font=("Arial", 12),text_color="black", background_color="white")

    # ------------------------------------Begin with Processing-----------------------------------------------------

    if event == 'Separate Storms':

        # ..........Check user inputs to ensure correct format and required fields...........
        # copy args from the window to a dictionary
        input_args = args # copy the sg derived args dict to a new dictionary
        dtype_args =input_args.copy() # copy the input args dict to a new dictionary and update with data type

        # convert all numerical strings to float
        input_args = su.convert_strings_to_floats(input_args)
        # change any empty strings to None
        input_args = su.clean_input_dict(input_args)
        # ....................Load in user inputs to variables...................
        # update the progress bar with 5 progress
        window['PBAR'].update(5)
        # Set the input file paths
        filename = input_args['input_file']  # input file
        dtype_args['input_file'] = 'str'  # set file type to string

        # optionally deifne sheet name
        sheetname = input_args['sheet_name']
        dtype_args['sheet_name'] = 'str'  # set sheet type to string

        # tipping and logging data
        tip_type = input_args['Tip_Record_Type']  # Set tip record type
        dtype_args['Tip_Record_Type'] = 'str'  # set tip type to string

        tip_mag = input_args['tip_mag']  # set the magnitude of each tip
        dtype_args['tip_mag'] = 'float'  # set tip magnitude to float

        tip_units = input_args['units']  # units for each tip
        dtype_args['units'] = 'str'  # set tip units to string

        # storm gap partitioning data
        # storm gap type
        storm_gap_type_name = input_args['Storm_Gap_Type']  # set the storm gap type
        dtype_args['Storm_Gap_Type'] = 'str'  # set storm gap type to str

        # if user defined storm gap set value
        storm_gap = input_args['fixed_mit']  # set the storm gap interval
        dtype_args['fixed_mit'] = 'float'  # set storm gap to float

        # if statistically independent storm gap set value
        isc_time = input_args['isc_interval']  # max inter-event time
        dtype_args['isc_interval'] = 'float'  # set isc time to float

        # # flow path length
        # flow_dist = input_args['flow_path_len']
        # dtype_args['flow_path_len'] = 'float'
        #
        # # River Slope
        # relief = input_args['watershed_relief']
        # dtype_args['relief'] = 'float'

        # # Bankfull Depth
        # BF_depth = input_args['depth']
        # dtype_args['depth'] = 'float'
        #
        # # Manning's n
        # n = input_args['n_coeff']
        # dtype_args['n_coeff'] = 'float'

        # min storm depth boolean
        min_depth_TF = input_args['min_depth_bool']
        dtype_args['min_depth_bool'] = 'bool' # set min depth boolean to bool

        # minimum storm depth
        min_depth = input_args['min_depth']
        dtype_args['min_depth'] = 'float'

        # min storm duration boolean
        min_duration_TF = input_args['min_duration_bool']
        dtype_args['min_duration_bool'] = 'bool' # set min duration boolean to bool

        # minimum storm duration
        min_duration = input_args['min_duration']
        dtype_args['min_duration'] = 'float'

        # output options
        output_path = input_args['output_path']  # output folder
        dtype_args['output_path'] = 'str'  # set output path to string

        output_name = input_args['output_name']
        dtype_args['output_name'] = 'str'  # set output name to string

        plt_ext = input_args['plt_ext'] # plotting output extension
        dtype_args['plt_ext'] = 'str' # set plotting extension to string

        plot_start_date = input_args['plt_start_date'] # plotting start date
        dtype_args['plt_start_date'] = 'str' # set plotting start date to string

        plot_end_date = input_args['plt_end_date'] #
        dtype_args['plt_end_date'] = 'str' # set plotting end date to string

        data_opt = input_args['data_opt']  # data from each storm
        dtype_args['data_opt'] = 'bool'  # set data opt to bool

        plot_opt = input_args['plot_opt']  # output plotting boolean
        dtype_args['plot_opt'] = 'bool'  # set plot opt to bool

        plot_int = input_args['plot_int']  # intervals to plot
        dtype_args['plot_int'] = 'float'  # set plotting interval to float

        # user_int = input_args['user_interval']  # user defined interval
        # dtype_args['user_interval'] = 'float'  # set userdefined interval to float

        # ....................Adjust naming conventions and inputs...................
        # Adjusting some parameter names to make them shorter
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
                # display warning if isc time is greater than 48 hours
                sg.popup_no_wait(isc_warning, title="Warning",text_color='black', background_color='white',
                         button_color=('black', 'lightblue'))

        else:
            storm_gap_type = 'ISC'
            print('Storm gap type not valid. Defaulting to Statistically Independent Storms')
            # print('Turn this into a warning message')

        # if minimum depth is not selected default the value to 0
        if not min_depth_TF:
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
                sg.popup_error(error_msg_dates, title='Invalid Dates', text_color='black',
                               background_color='white', button_color=('black', 'lightblue'))
                tf_date = False

        if plot_end_date:
            try:
                datetime.strptime(plot_end_date, '%Y-%m-%d').date()
            except:
                error_msg_dates = "Input date formats can not be interpreted please input date as YYYY-MM-DD "
                sg.popup_error(error_msg_dates, title='Invalid Dates', text_color='black',
                               background_color='white', button_color=('black', 'lightblue'))
                tf_date = False
        # # .................... User Input Error checking....................
        # check if the gui has been given all required parameters
        # future improvement here of returning the missing field names
        required_fields = su.check_for_required_fields(input_args)
        tf_fields, missing_fields = su.is_gui_filled(input_args, required_fields)
        if not tf_fields:  # if missing fields throw error window
            error_msg_fields = "There are required fields not filled out."
            sg.popup_error(error_msg_fields, title='Missing Values', text_color='black',
                           background_color='white', button_color=('black', 'lightblue'))
            print(missing_fields)
            tf_fields = False

        # check if inputs are correctly formatted as sting, float, or bool for required fields
        tf_type = False
        if tf_fields:
            tf_type, error_msg = su.check_input_type(input_args, required_fields, dtype_args)
            if not tf_type:  # if not strings throw error window
                sg.popup_error(error_msg, title='Input Type Error', text_color='black',
                               background_color='white', button_color=('black', 'lightblue'))



        #  ................................Execute SEPARATE algorithm...........................................
        if tf_type and tf_fields and tf_date:
            try:
                errmsg = None

                # Read-in Data & Process TBRG Data
                tip_datetime, tip_depth, logging_interval, start_date, end_date = sf.separate_preprocessing(filename,
                                                                                                            sheetname,
                                                                                                            tip_type,
                                                                                                            tip_mag)

                # update progress bar
                window['PBAR'].update(10)

                # get minimum time between storms in hours
                if storm_gap_type == 'ISC':
                    isc_t_max = isc_time  # maximum duration to look over for finding minimum inter-event time

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
                    Fixed_MIT, CV_IET, mean_IET, std_IET, ISC_testintervals, StormNumsRec = sf.separate_ISC(
                        tip_datetime, tip_depth, isc_t_max, min_depth, min_duration,
                        gap_plots_path, output_name, plt_ext)

                elif storm_gap_type == 'RTTC':
                    # note this is not actively included in separate and will be available in future releases
                    inter_event_interval = ''
                    gap_plots_path = ''  # dummy value
                    storm_gap = ''
                    Fixed_MIT = 0  # calculate travel time Solyom & Tucker (2004), doi:10.1029/2003JF000032
                    # Tt_max = sf.calculate_Tt_max(flow_dist, relief, BF_depth, n)
                    # Fixed_MIT = Tt_max

                elif storm_gap_type == 'UDM':
                    Fixed_MIT = storm_gap
                    gap_plots_path = ''  # dummy value
                    inter_event_interval = ''

                else:
                    Fixed_MIT = 0
                    errmsg = 'Storm gap type not valid'
                    sg.popup_error(errmsg, title='Error', text_color='black', background_color='white',
                                   button_color=('black', 'lightblue'))
                    raise ValueError(errmsg)

                # separate storms

                # identifying breaks in storms
                storms, interevent_times = sf.separate_storms(tip_datetime, tip_depth, Fixed_MIT)

                # filter for additional criteria
                storm_data, filtered_interevent_times, N_nofilter, N_suppressed = sf.separate_filter(storms,
                                                                                                     interevent_times,
                                                                                                     min_depth,
                                                                                                     min_duration)
                total_storms = N_nofilter # total number of storms
                suppressed_storms = N_suppressed # number of suppressed storms
                N_storms = total_storms - suppressed_storms # number of storms after filtering
                window['PBAR'].update(40)

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
                window['PBAR'].update(60)

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
                    iD_Mag, iD_time, R_fit, t_fit, tip_idx, cum_rain, duration_min = sf.separate_profiler(StormIDX,
                                                                                                          storm_data,
                                                                                                          tip_datetime,
                                                                                                          tip_depth,
                                                                                                          plot_int)

                    start_time_abs = storm_data[StormIDX]['start']
                    peakiD_all = []

                    for interval in I_intervals * 60:  # Convert hours back to minutes for intensity intervals
                        # calculate the peak intensity
                        peakiDs = sf.separate_peak_intensity(start_time_abs, t_fit, R_fit, interval)
                        # peakids =intensity_interval, peakiD_Mag, peakiD_datetime, peakiD_time_relative
                        peakiD_all.append(peakiDs)  # log the peak ids for each interval

                        # optionally log the storm profile data
                        if data_opt and plot_int == interval and ~np.isnan(peakiDs[1]):
                            # cumulative time in hours
                            cumulative_time_hours = (tip_datetime[tip_idx] - tip_datetime[tip_idx].iloc[
                                0]).dt.total_seconds() / 3600.0
                            peak_dt_str = peakiDs[2].strftime('%Y-%m-%d %H:%M:%S')
                            # store the profile storm profile data
                            dataset_name = storm_id_name
                            storm_meta_data = {f'Storm ID:': f'{storm_id_name}',
                                               f'Start Date & Time:': f'{start_time_abs}',
                                               f'Storm Duration (hrs):': f'{np.round(duration_min / 60, 2)}',
                                               f'Storm Magnitude ({tip_units}):': f'{np.round(len(tip_idx) * tip_mag, 2)}',
                                               f'Peak {int(interval)}-min Intensity ({tip_units}/hr):': f'{round(peakiDs[1], 2)}',
                                               f'Peak Intensity Date and Time:': f'{peak_dt_str}',
                                               f'Number of Tips': f'{len(tip_idx)}'}

                            storm_profiles[dataset_name] = {f'Cumulative Storm Time (hours)': np.round(iD_time/60,2),
                                                            # interpolated time range since start of storm
                                                            f'{plot_int}-min Intensity ({tip_units}/hr)': np.round(iD_Mag,2),
                                                            f'Storm Metadata': storm_meta_data}
                            # # return the raw data
                            storm_raw_profiles[dataset_name] = {f'TBRG Time Stamp': tip_datetime[tip_idx],  # win_range,
                                                                f'Cumulative Storm Time (hours)': np.round(
                                                                    cumulative_time_hours, 2),  # win_range,
                                                                f'Cumulative Rainfall ({tip_units})': cum_rain}

                        # optionally plot the storm profile and peak intensity
                        if plot_opt and plot_int == interval and ~np.isnan(peakiDs[1]):
                            peak_dt_str = peakiDs[2].strftime('%Y-%m-%d %H:%M:%S')
                            fig_title = (f'{output_name}\n'
                                         f'Storm ID:{storm_id_name}\n'  # int(storms_in[i])
                                         f'Start Date & Time: {start_time_abs}\n'
                                         f'Storm Magnitude ({tip_units}): {np.round(len(tip_idx) * tip_mag, 2)}\n'
                                         f'Peak {int(interval)}-min Intensity ({tip_units}/hr): {round(peakiDs[1], 2)}\n'
                                         f'Peak Intensity Date and Time:{peak_dt_str}\n'
                                         )
                            sf.separate_profile_plots(interval, tip_units, peakiDs[1], peakiDs[3], t_fit, R_fit,
                                                      tip_idx, iD_time, iD_Mag, fig_title, plots_path, storm_id_name,
                                                      plt_ext)

                    # Combine storm data and peak intensity results.
                    combined_record = storm_data[StormIDX].copy()
                    combined_record['StormID'] = storm_id_name
                    for idx, interval in enumerate(I_intervals * 60):
                        key_intensity = f'Peak_i{int(interval)}'
                        key_time = f'Peak_i{int(interval)}_time'
                        combined_record[key_intensity] = peakiD_all[idx][1]
                        combined_record[key_time] = peakiD_all[idx][2]
                    storm_record.append(combined_record)

                # build header for output files
                if tip_type == 'Cumulative Tips': # if cumulative tips then no logging interval
                    logging_interval='N/A'

                header_parameters = {
                    # 'Dataset ID:': f'{output_name}',
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

                # n_storms_warning = (
                #     "*Note: The ‘Number of Storms in Record’ column includes all partitioned storm events, including those less "
                #     "than the (optional) minimum depth criterion.")
                # header_parameters.update({
                #     n_storms_warning: ' '
                # })


                # % Creating final output tables and plots
                window['PBAR'].update(90)
                print('finalizing outputs')
                # first output the ISC results
                # if optimized output the fitting parameters to a file
                if storm_gap_type == 'ISC':
                    # will likely need some rebuilding for new output structures
                    sf.output_fitting_parameters_to_file(software_metadata, header_parameters, CV_IET, mean_IET,
                                                         std_IET,ISC_testintervals, StormNumsRec,
                                                          output_name, gap_plots_path)

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


                # Define columns for the summary table.
                # Basic storm data plus peak intensities for each intensity interval.
                columns = ['StormID', 'Start', 'End', 'Duration', 'Magnitude', 'Storm_Intensity'] + \
                          [f'Peak_i{int(60 * I_int)}' for I_int in I_intervals] + \
                          [f'Peak_i{int(60 * I_int)}_time' for I_int in I_intervals]

                # Define units for each column (for header purposes).
                units = ['Unique Identifier', 'date_time', 'date_time', 'hours', tip_units, tip_units + '/hr'] + \
                        [tip_units + '/hr'] * len(I_intervals) + ['date_time'] * len(I_intervals)

                # output = pd.DataFrame(storm_record, columns=columns)
                output = output.reindex(columns=columns)

                # check that all values are not nan
                if output[
                    f'Peak_i{int(60 * I_intervals[0])}'].isnull().all():  # np.all(np.isnan(output[f'Peak_i{int(60 * I_intervals[0])}'])):
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
                print('complete')

                # update progress bar
                window['PBAR'].update(100)

                # optionally clean out variables
                if clean_variables:
                    # List of variables to keep (do not clear)
                    keep_vars = ["sg", "np", "datetime", "pd", "os", "stats",
                                 "su", "sf", "build_SEPARATE_layout", "clean_variables",
                                 "window", "event", "args", "layout", "background_color",
                                 "help_messages", "resize", "software_metadata"]

                    # Delete all non-essential variables
                    for var in list(globals().keys()):
                        if var not in keep_vars:
                            del globals()[var]

                    print("Cleaned up simulation variables, GUI remains intact.")
                sg.popup('Complete!', title='Complete', text_color='black', background_color='white',
                         button_color=('black', 'lightblue'))
            except:
                window['PBAR'].update(0)
                if errmsg:  # caused a defined error occurred
                    sg.popup_error(errmsg, title='Error', text_color='black', background_color='white',
                                   button_color=('black', 'lightblue'))
                else:  # an undefined error occurred
                    sg.popup('If you did not receive an error message before this.\nSomething unexpected happened! Please contact developers for help',
                             title='Something unexpected')

# if __name__ == "__main__":
#     main()
