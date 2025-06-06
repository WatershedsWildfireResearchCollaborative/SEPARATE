import PySimpleGUI as sg
import os
import sys
from functions.build_help_dialogue import build_help_dialogue


# helper function taken from here
# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):  # fixes paths for pyintaller
    """Fixes paths for PyInstaller; otherwise returns absolute path."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def build_SEPARATE_layout():
    # Fonts and Colors
    # header_font = ("Arial", 16, "bold")
    section_header_font = ("Arial", 16, "bold")
    label_font = ("Arial", 14,"bold")
    input_font = ("Arial", 14)
    input_text_color = "black"
    header_color = "black"
    background_color = "white"
    text_color = "blue"
    box_color = "lightgrey"
    button_bg = "lightblue"
    dropdown_color = button_bg
    button_color = (input_text_color, button_bg)
    help_color = 'white'
    help_width = 0
    button_font = ('Arial', 14, 'bold')


    help_messages = build_help_dialogue()

    # set path for info button log
    info_button = resource_path(os.path.join("images/info_button.png"))

    pad1 =((30, 0), (0, 0))
    pad2 =((60, 0), (0, 0))
    pad3 = ((60, 0), (5, 0))


    #%% Header
    header_path = resource_path(os.path.join("images/header.png"))
    gui_header = [
        [sg.Image(header_path, pad=((0, 0), (0, 10)))]
    ]

    #%% Inputs Section
    # Build inputs header
    inputs_header = [
        [sg.Text("Inputs", font=section_header_font, background_color=background_color, text_color=header_color)],
        [sg.HorizontalSeparator(color="black")]
    ]

    # LEFT COLUMN: Labels
    # Give each sg.Text a fixed size=(X,1) so they align
    # Also use justification='right' to align text to the right edge
    left_col = [
        [sg.Text("*Rainfall Record Data", size=(20, 1), justification='right',
                 font=label_font, background_color=background_color, text_color=text_color)],
        [sg.Text("Excel Sheet Name", size=(20, 1), justification='right',
                 font=label_font, background_color=background_color, text_color=text_color)],
        [sg.Text("* Rainfall Record Type", size=(20, 1), justification='right',
                 font=label_font, background_color=background_color, text_color=text_color)],
        [sg.Text("* Tip Magnitude", size=(20, 1), justification='right',
                 font=label_font, background_color=background_color, text_color=text_color)]
    ]

    # RIGHT COLUMN: Buttons & Fields
    # Match the rows in the same order so they align horizontally
    right_col = [
        # 1) Rainfall Record Data
        [
            sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info1'),
            sg.InputText(key="input_file", size=(25, 1), font=input_font,
                         background_color=box_color, text_color="black"),
            sg.FileBrowse(button_color=button_color, file_types=(("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")))
        ],
        # 2) Excel Sheet Name
        [
            sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info2'),
            sg.InputText(key="sheet_name", size=(25, 1), font=input_font,
                         background_color=box_color, text_color="black")
        ],
        # 3) Rainfall Record Type
        [
            sg.Combo(["Cumulative Tips", "Fixed Interval"], key="Tip_Record_Type",
                     font=input_font, button_background_color=button_bg, background_color=box_color, readonly=True,
                     size=(26, 1))  # <–– Match size to align with InputText above
        ],
        # 4) Tip Magnitude & Units
        [
            sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info3'),
            sg.InputText(key="tip_mag", size=(10, 1), font=input_font,
                         background_color=box_color, text_color="black"),
            sg.Text("Tip Units", font=label_font, background_color=background_color, text_color=text_color),
            sg.Combo(["mm", "cm", "in"], key="units", font=input_font, readonly=True,
                     button_background_color=button_bg, size=(5, 1),background_color=box_color)
        ]
    ]

    # assemble inputs section
    inputs_section = [
        *inputs_header,
        [
            sg.Column(left_col, background_color=background_color, vertical_alignment='top'),
            sg.Column(right_col, background_color=background_color, vertical_alignment='top')
        ]
    ]

    #%% Build Partition Criteria Section

    partition_header = [
        [sg.Text("Partitioning Criteria",
                 font=section_header_font,
                 background_color=background_color,
                 text_color=header_color)],
        [sg.HorizontalSeparator(color="black")]
    ]

    mit_header = [
        [
            sg.Text("* Criterion for Fixed Minimum Inter-event Time (MIT) Selection",
                    background_color=background_color,
                    text_color=text_color,
                    justification='center',
                    font=label_font ),
            sg.Button(image_filename=info_button,
                      button_color=('white', 'white'),
                      border_width=0,
                      key='info4')
        ],
        [
            sg.Combo(
                ["User-Defined MIT (UDM)", "Independent Storms Criterion (ISC)"],#, "Travel Time Criterion (TTC)"
                key="Storm_Gap_Type",
                font=input_font,
                size=(30, 1),
                readonly=True,
                background_color=box_color,
                button_background_color=button_bg,
                pad=pad1  # <-- 30 px left indent
            )
        ]
    ]


    left_col = [
        #1
        [
        sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info5',pad=pad1),
            sg.Text("For User-Defined MIT",background_color=background_color, font=label_font ,
                text_color=text_color)

          ],
        #2
        [sg.Text("Fixed Minimum Inter-event Time",background_color=background_color, font=label_font,
                 text_color=header_color, size=(35, 1), pad=pad2)
        ],
        #3
        [
        sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info6', pad=pad1),
        sg.Text("For Statistically Independent Storms", background_color=background_color, font=label_font ,
                    text_color=text_color),
         ],
        #4
        [sg.Text("Maximum Inter-event Test Interval",background_color=background_color, font=label_font,
                         text_color=header_color, size=(35, 1), pad=pad2)],
        #5
        # [
        # sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info7',pad=pad1),
        # sg.Text("For Maximum Distance Travel Time", background_color=background_color, font=("Arial", 12, "bold"),
        #         text_color=text_color),
        #  ],
        # #6
        # [sg.Text("Longest Flow Path (planar)", background_color=background_color, font=label_font,
        #                  text_color=header_color, size=(35, 1), pad=pad3)],
        # #7
        # [sg.Text("Watershed Relief", background_color=background_color, font=label_font,
        #                  text_color=header_color, size=(35, 1), pad=pad3)],
        # #8
        # [sg.Text("Outlet Bankfull Depth", background_color=background_color, font=label_font,
        #                 text_color=header_color, size=(35, 1), pad=pad3)],
        # #9
        # [sg.Text("Manning’s Coefficient", background_color=background_color, font=label_font,
        #                  text_color=header_color, size=(35, 1), pad=pad3)],
    ]

    right_col = [
        #1
        [sg.Text("",background_color=background_color, size=(5, 1)) ], # make small gap

        #2
        [sg.InputText(key="fixed_mit", size=(8, 1), font=input_font, background_color=box_color, text_color="black"),
            sg.Text("hours", font=label_font, text_color=header_color, background_color=background_color)
        ],
        #3
        [sg.Text("",background_color=background_color, size=(5, 1)) ], # make small gap
        #4
        [sg.InputText(key="isc_interval", size=(8, 1), font=input_font, background_color=box_color,
                         text_color="black", default_text="48"),
            sg.Text("hours", font=label_font, text_color=header_color, background_color=background_color)
        ],
        # #5
        # [sg.Text("", background_color=background_color, size=(5, 1))],  # make small gap
        #
        # # 6) Longest Flow Path
        # [
        #     sg.InputText(key="flow_path_len", size=(8, 1), font=input_font, background_color=box_color,
        #                  text_color="black"),
        #     sg.Text("km", font=label_font, text_color=header_color, background_color=background_color)
        # ],
        # # 8) Watershed Relief
        # [
        #     sg.InputText(key="watershed_relief", size=(8, 1), font=input_font, background_color=box_color,
        #                  text_color="black"),
        #     sg.Text("m", font=label_font, text_color=header_color, background_color=background_color)
        # ],
        # # 9) Outlet Bankfull Depth
        # [
        #     sg.InputText(key="depth", size=(8, 1), font=input_font, background_color=box_color, text_color="black"),
        #     sg.Text("m", font=label_font, text_color=header_color, background_color=background_color)
        # ],
        # # 10) Manning’s Coefficient
        # [
        #     sg.InputText(key="n_coeff", size=(8, 1), font=input_font, background_color=box_color, text_color="black",
        #                  default_text="0.035"),
        #     sg.Text("s/m^(2/3)", font=label_font, text_color=header_color, background_color=background_color)
        # ],
    ]


    additional_header = [
        [
            sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info8'),

            sg.Text("Additional Exclusion Criteria", background_color=background_color, font=label_font,
                 text_color=text_color),
         ],
        ]


    left_col2 = [
        [sg.Checkbox("Minimum Event Rainfall Depth", key="min_depth_bool", default=True,
                     font=label_font, size=(35, 1), text_color=header_color, background_color=background_color,pad=pad1)],
        [sg.Checkbox("Minimum Event Duration", key="min_duration_bool", default=True,
                     font=label_font, size=(35, 1), text_color=header_color, background_color=background_color,pad=pad1)],
    ]

    right_col2 = [
        # 12) Minimum Event Rainfall Depth => input
        [
            sg.InputText(key="min_depth", size=(8, 1), font=input_font, background_color=box_color, text_color="black"),
            sg.Text("tip units", font=label_font, text_color=header_color, background_color=background_color)
        ],
        # 13) Minimum Event Duration => input
        [
            sg.InputText(key="min_duration", size=(8, 1), font=input_font, background_color=box_color,
                         text_color="black"  ),
            sg.Text("hours", font=label_font, text_color=header_color, background_color=background_color)
        ],
    ]

    # Combine columns into a single section
    partition_section = [
        *partition_header,
        *mit_header,
        [
            sg.Column(left_col, background_color=background_color, vertical_alignment='top'),
            sg.Column(right_col, background_color=background_color, vertical_alignment='top')
        ],
        *additional_header,
        [
            sg.Column(left_col2, background_color=background_color, vertical_alignment='top'),
            sg.Column(right_col2, background_color=background_color, vertical_alignment='top')]

    ]

    # %% Build Output Section

    output_header = [
        [sg.Text("Output Options",
                 font=section_header_font,
                 background_color=background_color,
                 text_color=header_color)],
        [sg.HorizontalSeparator(color="black")]
    ]

    # LEFT COLUMN: Labels and sub-labels
    left_col = [
        #1
        [sg.Text("*Output Directory", size=(25, 1), font=label_font, text_color=text_color,
                 background_color=background_color)],
        #2
        [sg.Text("*Outputs Prefix", size=(25, 1), font=label_font, text_color=text_color,
                 background_color=background_color)],
        #3
        [sg.Text("", size=(25, 1), font=label_font, text_color=text_color,
                     background_color=background_color)],
        #4
        [sg.Text("*Image File Format", size=(25, 1), font=label_font, text_color=text_color,
                 background_color=background_color)],
    ]


    right_col = [
        # 1 Output Directory
        [sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info9'),
         sg.InputText(key="output_path", size=(25, 1), font=input_font, background_color=box_color, text_color="black"),
         sg.FolderBrowse(button_color=button_color)],

        # 2 Outputs Prefix
        [sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info10'),
         sg.InputText(key="output_name", size=(25, 1), font=input_font, background_color=box_color,
                      text_color="black")],
        #3
        [sg.Text("", size=(25, 1), font=label_font, text_color=text_color,
                 background_color=background_color)],
        #4  Image File Format
        [
         sg.Combo([".png", ".eps", ".jpg", ".pdf"],
                  key="plt_ext", size=(10, 1), font=input_font, readonly=True,background_color=box_color,
                  button_background_color=button_bg, default_value=".png")],
    ]

    timeseries_header = [
        [sg.Text("", size=(35, 1), font=label_font, text_color=text_color, background_color=background_color)],
        [sg.Text("Rainfall Record Timeseries Date Range ", font=label_font,
                 text_color=text_color, background_color=background_color),
         sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info11')
         ],

        [sg.Text("Start Date", font=label_font, background_color=background_color, text_color=header_color, pad=pad1),
         sg.InputText(key="plt_start_date", size=(12, 1), font=input_font, background_color=box_color,
                      text_color="black"),
         sg.Text("End Date", font=label_font, background_color=background_color, text_color=header_color),
         sg.InputText(key="plt_end_date", size=(12, 1), font=input_font, background_color=box_color,
                      text_color="black")],

    ]

    event_profiling_header = [
        [sg.Text("", size=(35, 1), font=label_font, text_color=text_color, background_color=background_color)],
        [sg.Text("Separated Storm Event Profiling (all storms) ", font=label_font,
             text_color=text_color, background_color=background_color),
        sg.Button(image_filename=info_button, button_color=('white', 'white'), border_width=0, key='info12')],

        [sg.Checkbox("Include Tabular Storm Event Data", key="data_opt", default=True, font=label_font,
                 text_color=header_color, background_color=background_color)],

        [sg.Checkbox("Include Graphical Storm Event Profiles", key="plot_opt", default=True, font=label_font,
                 text_color=header_color, background_color=background_color)],

        [sg.Text("Intensity Interval for Storm Profiles", size=(25, 1), font=label_font, text_color=header_color,
                 background_color=background_color),
        sg.Combo([5, 10, 15, 30, 60], key="plot_int", size=(5, 1), font=input_font, readonly=True,
                  button_background_color=button_bg, default_value=15, background_color=box_color),
         sg.Text("minutes", font=label_font, background_color=background_color, text_color=header_color)]
    ]



    output_section = [
        *output_header,
        [sg.Column(left_col, vertical_alignment='top', background_color=background_color),
            sg.Column(right_col, vertical_alignment='top', background_color=background_color)],
        *timeseries_header,
        *event_profiling_header
    ]

    #%% execute separator
    # execution
    blank_text = [[sg.Text('', font=label_font, background_color=background_color,
                           text_color=text_color)]]
    partition_data = [[sg.Column([[sg.Button('Separate Storms', button_color=button_color, size=(13, 2),
                                            font=button_font)]], justification='center')]] #, pad=(10,10)
    progress_text = [[sg.Text('Partitioning Progress:', font=label_font, background_color=background_color,
                             text_color=text_color)]]
    progress_bar = [[sg.ProgressBar(100, orientation='h', expand_x=True, size=(20, 20), key='PBAR')]]

    execution_section=[
        *blank_text,
        *partition_data,
        *progress_text,
        *progress_bar
    ]

    #%% Assemble Layout

    # Combine Everything
    layout = (
            gui_header +
            inputs_section +
            partition_section  +
            output_section +
            execution_section
    )

# %% set up window aand scrolling
    # Wrap in a scrollable Column if the layout is tall
    screen_width, screen_height = sg.Window.get_screen_size()
    disp_width = min(screen_width, 800)
    disp_height = int(screen_height * 0.85)

    column = sg.Column(layout,
                       scrollable=True,
                       expand_x=True,
                       expand_y=True,
                       vertical_scroll_only=False,
                       size=(disp_width, disp_height),
                       background_color=background_color)

    final_layout = [[column]]
    return final_layout, background_color, help_messages
