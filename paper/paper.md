---
title: "SEPARATE: Storm Event Partitioning And Rainfall Analytics for Tipping-bucket rain gauge data Evaluation"
tags:
  - Python
  - meteorology
  - hydrology
  - geomorphology
  - rainfall analysis
  - rain gauge
  - pluviograph
authors:
  - name: Brendan P. Murphy
    orcid: 0000-0001-8025-1253
    equal-contrib: true
    corresponding: true
    affiliation: 1
  - name: Scott R. David
    orcid: 0000-0003-2708-4251
    equal-contrib: true
    affiliation: 2
affiliations:
  - name: School of Environmental Science, Simon Fraser University, Canada
    index: 1
  - name: Department of Watershed Sciences, Utah State University, United States of America
    index: 2

date: 2025-04-10
bibliography: paper.bib
---

# Summary
Here, we present SEPARATE – an open-source, GUI-based software package designed to provide users with a fast, reliable, and automated means to post-process tipping bucket rain gauge (TBRG) records. SEPARATE is an acronym, which stands for ‘Storm Event Partitioning And Rainfall Analytics for Tipping-bucket rain gauge data Evaluation’. In brief, the software provides users with multiple options and criteria for identifying storm events, then partitions events within the rainfall record using the most common and widely-accepted fixed minimum inter-event time (MIT) method [@restrepo:1982; @dunkerley:2008; @staley:2013], analyzes rainfall metrics within each storm, and provides users with organized data outputs detailing all identified storm events, as well as important metadata and options for data visualization.

![Logo designed by the first author for the SEPARATE application, representing profiles of cumulative rainfall and rainfall intensity as appears in the graphical storm outputs. This logo will appear in user’s Start Menu, Taskbar (if pinned), and for the Desktop Shortcut.\label{fig:figure1}](Figures/Figure1.png){ width=50% }

We have included the complete open-source code as part of this publication, but our Python-based software tool has more importantly been developed and packaged into a convenient GUI-based application for Microsoft Windows users. The executable file bundles together all necessary dependencies, allowing it to be installed and run as a standalone desktop application with a user-friendly interface that does not require any additional Python installations. The graphical user interface was developed using the open-source PySimpleGUI v4.60.4 [@b:2024], compiled into an executable using PyInstaller v6.3.0 [@pyinstaller:2024], and finally packaged into an installer using Inno Setup v6.2.2 [@inno:2023].

During the installation process, users will be prompted to select a directory for the installation (51.9 MB) and provided the option to add a shortcut to their desktop (\autoref{fig:figure1}). Upon opening the application, users are presented with a graphical user interface (GUI) organized into three sections (Inputs, Partitioning Criteria, and Output Options) that include a series of data entry boxes, buttons, checkboxes, drop-down menus, etc. (\autoref{fig:figure2}). This interface requires no programmatic environments and provides users with a simple, step-by-step layout to input unprocessed rainfall records, as well as to select all required, conditional, and optional analytical parameters. If any required parameters are missing or conflicting options are selected, then users should receive error messages when they attempt to run the analysis.

The GUI for SEPARATE also includes tooltip buttons, which when clicked, prompt pop-up windows that provide users with brief explanations about the associated input parameter or option. There is also a comprehensive instruction manual (.pdf) available for download with the executable, and for users wanting to understand more about the methodologies behind SEPARATE, we have included detailed information in a supplement.

![When installed using the provided executable file, SEPARATE can be run as a stand-alone application using the graphical user interface (GUI) shown here. Once all required data inputs and selections are made with the user-friendly drop-down menus, checkboxes, etc., then users can initialize their data analysis by clicking the ‘Separate Storms’ button at the bottom of the GUI. A progress bar is provided for reference at the bottom of the GUI (though in most test cases SEPARATE completed analysis in a few seconds, and a pop-up window should appear to inform users when their analysis is complete.)](Figures/Figure2.png){#fig:figure2 width=90% height=60%}



# Statement of Need
The accurate characterization of rainfall data is essential for the study of both hydrology and geomorphology. In particular, assessing the characteristics of independent rainfall events, i.e. “storms”, is critical for a wide range of research and resource management applications. Examples include but are not limited to the evaluation of rainfall-runoff thresholds [@kean:2011; @staley:2013], hydroclimatic dynamics [@slater:2021; @canham:2025], sediment entrainment and transport [@dick:1997; @delong:2018], soil erosion [@dunkerley:2019], watershed sediment dynamics [@murphy:2019], natural hazards [@cannon:2010; @gartner:2014; @peres:2014; @staley:2017; @segoni:2018; @mcguire:2021; @rengers:2024], landscape evolution [@tucker:2000], and water resource management [@ward:2011]. The storm characteristics of interest will vary depending on the particular application but could include metrics such as their time of arrival, duration, magnitude, and/or peak rainfall rate.

While some regions have access to high-fidelity rainfall data collected through ground-based and remotely sensing methods, this is not the case in much of the world. Even in countries or regions with more robust and high-resolution data coverage, remote sensing techniques, such as radar, often perform poorly wherever there is steep and variable topography, such as mountainous or canyon-carved terrain. High-gradient landscapes such as these are a predominant focus for hydrogeomorphic research though, especially for natural hazards. Consequently, the use of ground-based instrumentation for collecting rainfall data remains one of the most relied upon approaches [@segoni:2018].

There are a number of options for making ground-based rainfall measurements, but the tipping bucket rain gauge (TBRG) is among the most widely used, given its relative simplicity, ruggedness, affordability, and ability to provide continuous rainfall records of high temporal resolution. While models vary in detail, TBRGs fundamentally operate by funneling rainfall into small buckets positioned on either end of a fulcrum, which will tip and empty once a calibrated volume is reached. The resulting tip then positions the other bucket under the funnel and triggers an electronic switch that generates a record of the date and time; these data are typically saved to an attached battery-powered datalogger. The resulting record of bucket tips provides critical information about the cumulative-, event-, and rate-based characteristics of rainfall that occurred. However, these raw records of timestamped tips must first be accurately post-processed into meaningful meteorological metrics.

Most commercially available TBRG come with basic software to launch the attached datalogger, download data, and visualize records, but rarely, if ever, does this software provide users with post-processing capabilities, and particularly not for separating or analyzing storm metrics from continuous rainfall records. Third-party software options designed specifically for this task are also limited. There are some open-access software options that have capabilities for conducting event-based rainfall analysis, such as the EPA Storm Water Management Model (SWMM; [@rossman:2015]) or NetSTORM [@heineman:2004]. However, the functionality offered for event-based rainfall analysis can often be limited. Further, identifying these as possible tools for the task or operationalizing them for that purpose can be challenging, as they are only included as “add-ons” within software packages designed to perform more complex modeling or analysis. Alternatively, there are some open-access programmatic tools developed specifically for processing rain gauge data. One example is the USGS Rainmaker R package [@corsi:2023]. While options such as Rainmaker may work for some users, we highlight that they also represent a barrier to those without programming experience. Ultimately, the current software options for analyzing TBRG data present a number of obstacles to access and adoption, and recent work suggests that researchers and practitioners who rely heavily on rainfall data, but may not have a background specifically in hydrometrics, often resort to either manually analyzing TBRG data or develop custom, purpose-built scripts or macros.

Revealing the potential impact of this software gap on research of critical socioeconomic importance, Segoni et al. conducted a review of 107 recent landslide studies [@segoni:2018]. The authors found that nearly 80% of reviewed studies relied on rain gauges to assess rainfall controls on the occurrence of natural hazards, yet apparently none used existing software to analyze their rainfall records. Instead, the majority reportedly relied on manual data processing and extraction to determine rainfall parameters, and some 20% developed purpose-built scripts (though few, if any, published their code as best we could find). Independent of the analytical approach, most studies separated storms and analyzed rainfall data by either calculating rainfall totals over fixed durations (e.g., daily rainfall) or by using a fixed inter-event time (i.e., rainless periods). Calling attention to the challenges presented by an absence of good software options, one study even noted that this manual data processing “is a hard and time consuming activity” [@giannecchini:2016]. Yet perhaps the most troubling finding by Segoni et al. [@segoni:2018] was that 13% of the peer-reviewed studies reported relied on “expert judgement” alone to analyze rainfall records. Compounding these findings, Dunkerley [@dunkerley:2008] (as part of a different review) reported that when researchers separate storms in continuous rainfall records, they rarely provide any basis for their selected parameters. Together, these methodological reviews serve to highlight how without simple, easy to use software, there has been a preponderance (and apparent acceptance) of manual, subjective, and under-documented methods for the identification, separation, and analysis of rainfall data, particularly in natural hazards research.

# References