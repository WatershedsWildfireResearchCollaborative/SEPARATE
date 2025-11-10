def build_help_dialogue():
    # this function assembles al the text for the help dialogue boxes

    # input data helps
    helpmsg1 = """
*Required

File Path of the rainfall record data (.xlsx or .csv files only)

See SEPARATE manual for input file formatting instructions.

"""
    helpmsg2 = """
Optional

If input data is from an Excel file that contains multiple tabs or sheets, input the name of the Excel sheet containing the rainfall record (case sensitive). If no sheet name is entered, SEPARATE will attempt to extract data from the first sheet by default.

"""

    helpmsg3 = """
*Required

Enter the equivalent rainfall depth of each TBRG tip (model specific) then specify units in drop-down menu (mm, cm, or inches)
"""

    helpmsg4 = """
*Required

Select the criterion used to determine and assign the fixed MIT for storm event identification and separation.

See SEPARATE manual for more details about each method.

"""

    helpmsg5 = """
Conditional - Required

If User-Defined MIT is selected, enter the fixed MIT value (in hours) to use for storm event identification and separation. 
"""

    helpmsg6 = """
Conditional - Optional

If Statistically Independent Storms criterion is selected, set the maximum inter-event interval (in hours) to be used for testing. As a default, SEPARATE will evaluate intervals up to a maximum 48-hours. Users may adjust this value within the range of 24 to 500 hours. 

"""

    helpmsg7 = """
Conditional - Required 

If Maximum Distance Travel Time criterion is selected, then users must enter information about watershed of interest including:
Longest flow path distance (planar) in the watershed, in kilometers
Watershed relief (maximum elevation minus minimum elevation), in meters
Peak flow depth, in meters
Manning coefficient representative of longest flow path, in seconds per meters^(2/3); default value is set to 0.035, representative of a natural stream with low roughness.

See SEPARATE manual for more details.
"""

    helpmsg8 = """
Optional

Users can suppress any storm events with either a total rainfall depth or duration that does not exceed entered threshold values (in tip units and hours, respectively). For example, “storms” recording only a single tip.

For UDM and MDTT criterion, this will not influence analysis, but suppressed storms will not be included in the output summary table or storm profile analysis (if selected). For SIS criterion, additional criteria will influence calculations of the mean and standard deviation of inter-event time and potentially affect the identified fixed MIT value.

See SEPARATE manual for more details.

"""

    helpmsg9 = """
*Required

Enter an identifying name for the output results. This name will be used for the outputs folder as well as the prefix for all  
"""

    helpmsg10 = """
Optional

SEPARATE outputs include a timeseries plot of events displaying both the magnitude of individual events and the cumulative rainfall over the rainfall record. Enter an alternate start date, end date, or both (within the timeframe of the rainfall record) to adjust the x-axis range of displayed events and associated cumulative rainfall. Dates must be entered using the format: YYYY-MM-DD.
"""

    helpmsg11 = """
Optional

Tabular and graphical profiles of the cumulative rainfall and rainfall intensity through each storm can be optionally included as outputs.
 
For tabular outputs – data tables for each storm will be included in the output summary Excel file as separate sheets (or “tabs”) named according to their storm ID (found in the summary event table).

For graphical outputs – annotated storm profile plots for each storm will be saved as image files in a subfolder within the output directory. Image files are named based on the associated storm ID.

See SEPARATE manual for more details.
"""

    helpmsg12 = """
Conditional - Required

If either tabular or graphical event profile options are selected, then users must select the interval over which rainfall intensity will be calculated and plotted over the course of each storm event. Options include standard sub-hourly to hourly intervals of 5-, 10-, 15-, 30-, and 60-minutes.
"""

    helpmsg13 = """
Conditional - Required
    
When enabled, the Independence Storm Criterion (ISC) is computed using the excess-time formulation of inter-event gaps.

This means each dry interval between storms is reduced by the trial interval (τ) before calculating the coefficient of variation (CV):
Excess IET = Observed IET − τ

This approach corrects for bias introduced when only dry periods longer than τ are analyzed, and often yields a more consistent CV ≈ 1 threshold for independent storms.

Uncheck this option to use the raw inter-event times instead
    """

    # compile the help messages into a single structure
    help_messages = {
        'info1': helpmsg1,
        'info2': helpmsg2,
        'info3': helpmsg3,
        'info4': helpmsg4,
        'info5': helpmsg5,
        'info6': helpmsg6,
        'info7': helpmsg7,
        'info8': helpmsg8,
        'info9': helpmsg9,
        'info10': helpmsg10,
        'info11': helpmsg11,
        'info12': helpmsg12,
        'info13': helpmsg13,
    }
    return help_messages