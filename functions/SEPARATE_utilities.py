def is_numeric(value):
    """
    Check if a value is numeric (i.e. can be converted to a float).

    Args:
        value: The value to be checked.

    Returns:
        bool: True if the value is numeric, False otherwise.
    """
    try:
        # Attempt to convert the value to a float
        float(value)
        return True
    except ValueError:
        # If the conversion fails, the value is not numeric
        return False

def convert_strings_to_floats(input_dict):
    """
    Convert string values in a dictionary to floats.

    This function iterates over all values in a dictionary and if a value is a string,
    it attempts to convert the value to a float.  If the conversion fails (i.e. the
    string does not represent a valid number), the value is left unchanged.

    Args:
        input_dict (dict): The input dictionary to be converted.

    Returns:
        None. The input dictionary is modified in-place.
    """
    for key, value in input_dict.items():
        if isinstance(value, str):
            try:
                # Attempt to convert the string to a float
                input_dict[key] = float(value)
            except ValueError:
                # If the conversion fails, leave the value unchanged
                pass
    return input_dict


def clean_input_dict(input_dict):
    """
    Clean a dictionary by replacing empty strings or strings containing only spaces with None.

    Args:
        input_dict (dict): The input dictionary to be cleaned.

    Returns:
        dict: The cleaned dictionary with empty strings replaced by None.
    """
    for key, value in input_dict.items():
        if isinstance(value, str) and value.strip() == "":
            input_dict[key] = None
    return input_dict


def is_gui_filled(values, required_fields):
    """
    Check if all required values are in the GUI.

    This function takes a dictionary of GUI values and a list of required fields as input.
    It checks if all the required fields are present in the GUI values and if they are not
    empty or None. If any of the required fields are missing, it returns False and a list
    of the missing fields. If all the required fields are present and not empty, it returns
    True and an empty list.

    Parameters
    ----------
    values : dict
        A dictionary of GUI values.
    required_fields : list
        A list of required fields.

    Returns
    -------
    tuple
        A tuple containing a boolean indicating if all required fields are present
        and a list of any missing fields.

    Notes
    -----
    This function is used to check if all required fields are present in the GUI values.
    It is used to prevent errors from occurring when the program is run with incomplete
    data.
    """
    missing_fields = []
    field_bool = True
    for field in required_fields:
        if values[field] == '' or values[field] is None:
            missing_fields.append(field)
            field_bool = False
    return field_bool, missing_fields


def check_numerical_values(values_to_check):
    """
    Checks if all values in the input list are numbers.

    Parameters
    ----------
    values_to_check : list
        A list of values to check. Each value should be in the form of [value, 'Val_name'].

    Returns
    -------
    tuple
        A tuple containing a boolean indicating if all values are numbers and a string
        containing the names of the values that are not numbers.
    """
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
    """
    Compile a list of required fields based on the inputs provided. Some fields are always optional
    and some fields are only required if certain options are chosen.

    Parameters
    ----------
    args : dict
        A dictionary of all the inputs provided by the user.

    Returns
    -------
    required_fields : list
        A list of the required fields.
    """
    # compile required field list
    all_fields = list(args.keys())  # get all fields in dict

    # build list of non_required field
    # these four user defined fields are always optional
    remove_fields = ['sheet_name', 'plt_end_date', 'plt_start_date']

    # if not plotting no need to input a plot init fild
    if not args['plot_opt']:  # if not using optional plotting fields in dict
        # add plot_int remove required variable plot int
        remove_fields.append('plot_int')

    # if using UDM, then remove the following fields
    if args['Storm_Gap_Type'] == 'User-Defined MIT (UDM)':
        # these fields are not required when using UDM
        mit_fields_to_remove = ['flow_path_len','flow_path_len','watershed_relief','slope','depth','n_coeff','isc_interval']
        remove_fields.extend(mit_fields_to_remove)

    # if using RTTC, then remove the following fields
    if args['Storm_Gap_Type'] == 'Travel Time Criterion (TTC)':
        # these fields are not required when using RTTC
        rttc_fields_to_remove = ['fixed_mit','isc_interval']
        remove_fields.extend(rttc_fields_to_remove)

    # if using ISC, then remove the following fields
    if args['Storm_Gap_Type'] == 'Independent Storms Criterion (ISC)':
        # these fields are not required when using ISC
        ic_fields_to_remove = ['fixed_mit','watershed_relief','flow_path_len','slope','depth','n_coeff']
        remove_fields.extend(ic_fields_to_remove)

    # if not using minimum depth, then remove the field
    if not args['min_depth_bool']:
        remove_fields.append('min_depth')

    # if not using minimum duration, then remove the field
    if not args['min_duration_bool']:
        remove_fields.append('min_duration')

    # remove the unneeded fields from required fields
    required_fields = [x for x in all_fields if x not in remove_fields]
    return required_fields



def check_input_type(input_args, required_fields, dtype_args):
    """
    Check that all required fields are the correct data type.

    Parameters
    ----------
    input_args : dict
        A dictionary of all the inputs provided by the user.
    required_fields : list
        A list of the required fields.
    dtype_args : dict
        A dictionary of the required data types for each field.

    Returns
    -------
    tf_type : bool
        True if all the required fields have the correct data type, False otherwise.
    error_message : str
        An error message if the data types are incorrect.
    """
    # Validate input data types against expected types
    incorrect_values = []
    for field in required_fields:
        data_type = dtype_args[field]
        value = input_args[field]
        # Check data type for each field and append to incorrect_values if mismatched
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

    # Create error message if any incorrect values were found
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

# def validate_tip_type (tip_datetime, tip_type):
#     logging_interval = tip_datetime.diff().dt.total_seconds() / 60


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