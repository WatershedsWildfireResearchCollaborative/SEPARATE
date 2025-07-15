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

date: 10 April 2025
bibliography: paper.bib
---

# Summary
Here, we present SEPARATE: an open-source, GUI-based software package designed to provide users with a fast, reliable, and automated means to post-process tipping bucket rain gauge (TBRG) records. SEPARATE stands for 'Storm Event Partitioning And Rainfall Analytics for Tipping-bucket rain gauge data Evaluation'. The software identifies and partitions storm events using the widely accepted fixed minimum inter-event time (MIT) method [@restrepo:1982; @dunkerley:2008; @staley:2013], analyzes rainfall metrics for each storm, and provides organized outputs with metadata and visualization options.

![Application logo designed by B. Murphy. This logo will appear in a user’s Start Menu, Taskbar (if pinned), and Desktop Shortcut.\label{fig:figure1}](Figure1.png){ width=50% }

The complete open-source code is included as part of this publication, but our Python-based tool has also been packaged into a convenient GUI-based application for both Microsoft Windows and macOS users. The downloadable installer includes all dependencies, allowing SEPARATE to be installed and run without any additional installations. The GUI was developed using PySimpleGUI v4.60.4 [@b:2024], compiled with PyInstaller v6.3.0 [@pyinstaller:2024], and packaged using Inno Setup v6.2.2 [@inno:2023] for Windows and create-dmg for macOS [@ createdmg:2024].

![When using the installer for Windows or MacOS, SEPARATE runs as a stand-alone desktop application with the graphical user interface (GUI) shown here. All data inputs and parameter selection are managed through drop-down menus, checkboxes, etc., and the tool is initialized by clicking 'Separate Storms'. A progress bar and pop-up window allow users to know when their analysis is complete.\label{fig:figure2}](Figure2.png){ width=60% }

During installation (52 MB for Windows; 163 MB for Mac), users select a directory and optionally add a shortcut to their Desktop (\autoref{fig:figure1}). Upon launching the application, users are presented with a GUI organized into three sections (Inputs, Partitioning Criteria, and Output Options) with data entry boxes, buttons, checkboxes, and drop-down menus (\autoref{fig:figure2}). SEPARATE requires no programming environment to run and provides a step-by-step process to input rainfall records and then select all needed parameters. If any required inputs are missing or conflicting options are selected, error messages will appear. Tooltip buttons in the GUI open pop-ups with explanations, and a detailed instruction manual (.pdf) is included with the download. Additional methodological details are provided in a supplementary file.


# Statement of Need
Accurate characterization of rainfall data is essential in environmental research. Assessing characteristics of independent rainfall events ("storms") is critical for many applications, including but not limited to the evaluation of rainfall-runoff thresholds [@kean:2011; @staley:2013], hydroclimatic dynamics [@slater:2021; @canham:2025], sediment transport [@dick:1997; @delong:2018], soil erosion [@robichaud:2008; @dunkerley:2019], watershed sediment dynamics [@murphy:2019], natural hazards [@cannon:2010; @gartner:2014; @peres:2014; @staley:2017; @mcguire:2021; @rengers:2024], landscape evolution [@tucker:2000], and water resource management [@ward:2011]. Storm metrics of interest vary by application but often include time of arrival, duration, magnitude, or peak rainfall rates [@collar:2025]. While some regions have high-fidelity rainfall data, this is not true worldwide. Even in areas with more robust data coverage, remote sensing techniques, such as radar, perform poorly in steep, complex terrain. Yet, high-gradient landscapes are the focus for lots of hydrogeomorphic research, especially natural hazards. Consequently, ground-based instrumentation is still heavily relied upon [@segoni:2018].

The tipping bucket rain gauge (TBRG) remains one of the most widely used instruments, given its simplicity, ruggedness, affordability, and ability to provide continuous rainfall records. However, TBRG’s raw timestamped records must be post-processed to derive meaningful meteorological data. Most TBRG systems include only basic software for launching and downloading data, rarely offering post-processing features, and especially not for storm separation or analysis. Third-party software is also limited. Some open-access options offer event-based rainfall analysis, such as the EPA Storm Water Management Model (SWMM; [@rossman:2015]) or NetSTORM [@heineman:2004], however they are often embedded within larger software packages, making them difficult to operationalize for storm separation alone. Open-source programmatic tools also exist for TBRG processing, such as the USGS Rainmaker R package [@corsi:2023], but these options represent a barrier to entry to anyone without programming experience. 

A review by Segoni et al. of 107 recent landslide studies indirectly revealed how software limitations may be critically affecting research quality and reproducibility [@segoni:2018]. While nearly 80% of studies relied on rain gauges, none reportedly used existing software to analyze their rainfall data. The majority relied on manual processing and extraction and another 20% developed purpose-built (but largely unpublished) scripts. One reviewed study even noted how manual rainfall data processing “is a hard and time-consuming activity” [@giannecchini:2016]. Troublingly, Segoni et al. also reported that 13% of studies relied on “expert judgement” alone to analyze rainfall records. Further, Dunkerley [@dunkerley:2008] (in a different review) noted that few researchers provide any basis for selected parameters when separating storms in continuous rainfall records. Without accessible, easy-to-use software, researchers and practitioners who often rely heavily on rainfall data, but may not have specific expertise in hydrometrics, often appear to be relying on manual, custom, undocumented, and/or subjective methods for analyzing rain gauge data. SEPARATE was designed to help fill and address this critical gap.


# References