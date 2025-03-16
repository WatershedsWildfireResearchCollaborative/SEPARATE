def is_numeric(value):
    # states whether the input value is numeric or not
    try:
        float(value)
        return True
    except ValueError:
        return False

def convert_strings_to_floats(input_dict):
    """
    Convert string values in a dictionary to floats.
    Args:
        input_dict (dict): The input dictionary to be converted.
    Returns:
        None. The input dictionary is modified in-place.
    """
    for key, value in input_dict.items():
        if isinstance(value, str):
            try:
                input_dict[key] = float(value)
            except ValueError:
                pass
    return input_dict


def clean_input_dict(input_dict):
    """
    Clean a dictionary by replacing empty string values and only spaces containing only spaces with None.
    Args:
        input_dict (dict): The input dictionary to be cleaned.
    Returns:
        None. The input dictionary is modified in-place.
    """
    for key, value in input_dict.items():
        if isinstance(value, str) and value.strip() == "":
            input_dict[key] = None
    return input_dict

def is_gui_filled(values, required_fields):
    # check if all required values are in the GUI
    missing_fields = []
    field_bool = True
    for field in required_fields:
        if values[field] == '' or values[field] is None:
            missing_fields.append(field)
            field_bool = False
    return field_bool, missing_fields


def check_numerical_values(values_to_check):
    # input a list of in the form of [[value,'Val_name']....[valueN,'Val_nameN']]
    # the function will check in the input value is a number and if it is not it will rerun string with all the
    # names in the gui that are not values as a sting to be used a message in an error window
    tf_is_number = True
    error_val_msg = 'Please enter valid numerical values in:\n'
    for input_Vars in values_to_check:
        value = input_Vars[0]
        value_name = input_Vars[1]
        if not is_numeric(value):
            value_name = str(value_name) + '\n'
            error_val_msg = error_val_msg + value_name
            tf_is_number = False
    return tf_is_number, error_val_msg


def check_for_required_fields(args):
    # compile required field list
    all_fields = list(args.keys())  # get all fields in dict

    # build list of non_required field
    # these four user defined fields are always optional
    remove_fields = ['sheet_name', 'plt_end_date', 'plt_start_date']

    # if not plotting no need to input a plot init fild
    if not args['plot_opt']:  # if not using optional plotting fields in dict
        # add plot_int remove required variable plot int
        remove_fields.append('plot_int')

    if args['Storm_Gap_Type'] == 'User-Defined MIT (UDM)':
        mit_fields_to_remove = ['flow_path_len','flow_path_len','watershed_relief','slope','depth','n_coeff','isc_interval']
        remove_fields.extend(mit_fields_to_remove)

    if args['Storm_Gap_Type'] == 'Travel Time Criterion (TTC)':
        rttc_fields_to_remove = ['fixed_mit','isc_interval']
        remove_fields.extend(rttc_fields_to_remove)

    if args['Storm_Gap_Type'] == 'Independent Storms Criterion (ISC)':
        ic_fields_to_remove = ['fixed_mit','watershed_relief','flow_path_len','slope','depth','n_coeff']
        remove_fields.extend(ic_fields_to_remove)

    if not args['min_depth_bool']:
        remove_fields.append('min_depth')

    if not args['min_duration_bool']:
        remove_fields.append('min_duration')
    # remove the unneeded fields from required fields
    required_fields = [x for x in all_fields if x not in remove_fields]
    return required_fields




def check_input_type(input_args, required_fields, dtype_args):
    incorrect_values = []
    for field in required_fields:
        data_type = dtype_args[field]
        value = input_args[field]
        if data_type == 'str':
            if not isinstance(value, str):
                incorrect_values.append((field, value))
        elif data_type == 'int':
            if not isinstance(value, int):
                incorrect_values.append((field, value))
        elif data_type == 'float':
            if not isinstance(value, (int, float)):
                incorrect_values.append((field, value))
        elif data_type == 'bool':
            if not isinstance(value, bool):
                incorrect_values.append((field, value))

    if incorrect_values:
        # print('incorrect_values')
        tf_type = False
        error_message = ""
        for i, (field, value) in enumerate(incorrect_values):
            error_message += f"Invalid input data types for {i + 1}: "
            error_message += f"{field}={value}\n"
    else:
        tf_type = True
        error_message = None

    return tf_type, error_message


#
# if tf_fields:  # now check if all numerical inputs are numerical
#     check_vals = [[tip_mag, 'Rainfall Magnitude in Each Tip']]
#     if storm_gap_type == 'Fixed Minimum Inter-event Time (MIT)':  # if optimized storm gap value not required
#         check_vals.append([storm_gap, "Max Temporal Gap Allowed Between Storms"])
#     if user_int != '' or None:
#         check_vals.append([user_int, "User Defined Storm Interval"])
#     # check if all input values are numeric
#     tf_number, error_msg = check_numerical_values(check_vals)
#
#     if not tf_number:  # raise the error message
#         sg.popup_error(error_msg, title='Numerical Value Input Error', text_color='black',
#                        background_color='white', button_color=('black', 'lightblue'))
#