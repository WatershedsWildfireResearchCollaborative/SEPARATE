# SEPARATE

<p align="center">
  <img src="images/header.png" alt="SEPARATE Banner" width="600"/>
</p>

## Overview
**Storm Event Partitioning And Rainfall Analytics for Tipping-bucket rain gauge data Evaluation (SEPARATE)**

SEPARATE is an open-source, GUI-based software package that provides users with a fast, reliable, and automated method to post-process tipping bucket rain gauge (TBRG) data. It enables the identification and partitioning of independent storm events and calculates key rainfall metrics like storm duration, magnitude, and intensity. SEPARATE supports both user-defined and statistical (independent storm criterion) approaches to event separation, while offering a range of tabular and graphical output options.

The software is distributed both as:
- A **standalone executable** (no Python installation needed)
- A **source code version** with environment files for Python users

 SEPARATE was developed using PySimpleGUI, compiled into a standalone executable with PyInstaller, and packaged using Inno Setup for distribution.

## Download & Installation

SEPARATE can be used in two ways:

---

### Option 1: Precompiled Installer (Recommended)

Precompiled installers are available for both **Windows** and **macOS**, and include all required dependencies. No separate Python installation is needed.

**Steps:**

1. Download the appropriate installer for your operating system [here](https://usu.box.com/v/SEPARATE-download):
   - `SEPARATE_Windows.exe` for **Windows**  
   - `SEPARATE_macOS.dmg` for **macOS**

2. Run the installer:
   - On **Windows**, double-click `SEPARATE_Windows.exe` and follow the prompts.
   - On **macOS**, open the `SEPARATE_macOS.dmg` file, then **drag `SEPARATE_GUI.app` into your Applications folder** when prompted.

3. Launch SEPARATE to begin.

> ⚠️ **macOS note:** The application is not code-signed. You may need to bypass Gatekeeper the first time you run it (e.g., right-click → Open).  
> ⚠️ **Windows note:** Some antivirus software (including Windows Defender) may warn about unsigned installers. If you downloaded SEPARATE from our official link, you can safely ignore the warning and proceed with installation.


---

###  Option 2: Run from Source Code

If you prefer to run the Python source code, you can use either  a **Conda environment** or a **virtualenv with pip**..

#### Option 2A: Using Conda 

1. Clone or download the repository.
2. Open **Anaconda Prompt** and navigate to the folder.
3. Create the environment:
    ```bash
    conda env create -f envs/SEPARATE.yml
    ```

4. Activate the environment or add the evironment to you prefered IDE
    ```bash
    conda activate SEPARATE
    ```
5. Run the code either in your IDE or from the terminal with:
    ```bash
    python SEPARATE_GUI.py
    ```

#### Option 2B: Using pip + venv

1. Clone or download the repository.

2. Open **Command Prompt** or **PowerShell** and navigate to the project folder.

3. Create and activate a virtual environment:

    ```bash
    python -m venv separate_env
    .\separate_env\Scripts\activate
    ```

4. Install required packages:

    ```bash
    pip install -r envs/requirements.txt
    ```

5. **Install PySimpleGUI v4.60.5 manually**  
   This version is no longer hosted on PyPI, so you’ll need to install it from the wheel file included in the repository.

   **Steps:**
   1. Unzip the archive `build_installer/PySimpleGUI-4.60.5-main.zip`
   2. Navigate to the unzipped folder (it should contain a `.whl` file)
   3. From that folder, run:

   ```bash
   pip install PySimpleGUI-4.60.5-py3-none-any.whl
   ```

    > Note: You can also install from a direct GitHub clone or file path if preferred.

6. Run the tool:

    ```bash
    python SEPARATE_GUI.py
    ```

## Documentation

- [User Manual (PDF)](SEPARATE-User-Manual-Version1.0.pdf)
- [Manuscript (JOSS submission)](paper/paper.md)
- Supplementary Material in `supplementary/`

## Example Datasets

To help users get started quickly, we include two example datasets in the [`Example_Datasets`](Example_Datasets/) folder:

| Filename                             | Description                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------|
| `FixedInterval_TBRG_Example.xlsx`    | Example dataset logged at regular intervals using fixed time steps.      |
| `CumulativeTips_TBRG_Example.xlsx`   | Example dataset with cumulative tip logging style (e.g., HOBO loggers).  |

Each file contains two columns:
1. **Timestamp** in the format `MM/DD/YY HH:MM:SS`
2. **Rainfall Value** — either:
   - Cumulative tip count (`Cumulative Tips` format), or
   - Rainfall per interval (`Fixed Interval` format)

Both are preformatted to match SEPARATE’s input requirements. You can use these files to test the interface, explore SEPARATE’s options, or verify that your installation is working correctly. In the Example_Datasets/Ouputs folder, you can find the results from each of these runs below, using a 15-min. storm intensity for plotting.


<div align="center">
  <img src="images/fixed_example.png" alt="Fixed Interval Input Example" width="500"/>
  <br>
  <em>Figure: Fixed interval usage example.</em>
</div>

<br>

<div align="center">
  <img src="images/tips_example.png" alt="Cumulative Tips Input Example" width="500"/>
  <br>
  <em>Figure: Cumulative tips usage example.</em>
</div>



### Recommended Citation

Murphy & David, JOSS, 2025, submitted

### License Information 
MIT License

Copyright (c) 2025 Murphy Watershed Lab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Legal Disclaimer

SEPARATE is an open-source software package developed by the Murphy Watershed Science Lab to assist with rainfall data processing and storm event analysis. It is distributed in the hope that it will be useful for research, education, and resource management, but **without any warranty**.

The developers make no claims regarding the accuracy, completeness, or performance of the software. Users are solely responsible for any results generated and should independently validate outputs before applying them to engineering, policy, or hazard assessment decisions.

### Contributing
We welcome suggestions, improvements, and feedback to help improve SEPARATE.

If you are considering a significant code contribution, we encourage you to contact the developers first. This helps avoid duplicate efforts and ensures alignment with the project’s goals.

For smaller contributions or bug reports, feel free to create an issue or fork the repository and submit a pull request. All contributions are welcome.


