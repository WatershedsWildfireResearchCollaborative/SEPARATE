# Building the SEPARATE Windows Executable & Installer

This document describes how to build the **SEPARATE** Windows executable (`SEPARATE.exe`) and the optional Windows installer (`SEPARATE_setup.exe`).  


---

## 1. Overview

The SEPARATE Windows distribution is produced in two stages:

1. **Build the executable** using PyInstaller  
2. **Package it into a Windows installer** using Inno Setup  

Because of a known incompatibility between **SciPy**, **PyInstaller**, and **Python 3.12**, the Windows build **must** use **Python 3.11.x**.

The executable bundles Python internally — **users do not need Python installed**.

---

## 2. Required Repository Structure

Ensure the following files and directories exist in folder:
Note if starting with the GitHub build_installer\win folder, you will need to copy the SEPARATE_GUI.py and functions and images folders into the directory.

```
SEPARATE/
│
├── SEPARATE_GUI.py            # Main GUI entry point
├── functions/                 # Core SEPARATE processing code
├── images/                    # Application icons and image assets
│
├── SEPARATE.spec              # PyInstaller spec file
├── separate_inno.iss          # Inno Setup installer script
├── requirements.txt
├── LICENSE.txt

```

The spec and Inno scripts assume this layout.

---

## 3. Create the Windows Build Environment (Python 3.11)

### 3.1 Install Python 3.11  
Install **Python 3.11.9 (64-bit)** from python.org.

Confirm availability:

```powershell
py -3.11 --version
```

---

### 3.2 Create a clean virtual environment

Create the build-only environment:

```powershell
py -3.11 -m venv .venv-separate-exe
.\.venv-separate-exe\Scripts\activate
```

---

### 3.3 Optionally Upgrade pip

```powershell
python -m pip install --upgrade pip
```

---

### 3.4 Install the Windows EXE build requirements

```powershell
pip install -r requirements.txt
```

Ensure this file includes:

```
matplotlib==3.8.2
numpy==1.26.3
pandas==2.1.4
scipy==1.11.4
openpyxl==3.1.2
pywin32==306
pyinstaller==6.3.0
ghostscript==0.7
jaraco.functools
jaraco.context
jaraco.text
platformdirs
```

---

### 3.5 Install PySimpleGUI from its wheel

```powershell
pip install PySimpleGUI-4.60.5-py3-none-any.whl
```

---

### 3.6 Verify the environment

```powershell
python -c "import PySimpleGUI, numpy, pandas, matplotlib, scipy, openpyxl, win32api; print('Environment OK')"
```

---

### 3.7 Verify SEPARATE runs normally

```powershell
python SEPARATE_GUI.py
```

The GUI should launch successfully.

---

## 4. Build the Windows Executable with PyInstaller


### 4.1 Ensure `SEPARATE.spec` references the correct entry script

Inside the `.spec` file:

```python
a = Analysis(
    ['SEPARATE_GUI.py'],
    ...
)
```

---

### 4.2 Build the executable

```powershell
pyinstaller SEPARATE.spec --clean
```

This creates:

```
dist/
    SEPARATE/
        SEPARATE.exe
        (DLLs and support files)
```

---

### 4.3 Test the executable

```powershell
cd dist\SEPARATE
.\SEPARATE.exe
```

The GUI should open and operate normally.

---

## 5. Build the Windows Installer (Optional)

The installer is created using **Inno Setup**.

### 5.1 Open the installer script

File: `separate_inno.iss`


---

### 5.2 Confirm required paths

Ensure entries like these point to real files:

```ini
LicenseFile=...\LICENSE.txt
SetupIconFile=...\images\icon.ico
Source: "...\dist\SEPARATE\*"; DestDir: "{app}"
```

---


### 5.3 Build the installer

In **Inno Setup**:

```
File → Open → separate_inno.iss
Build → Compile
```

Output will appear as:

```
SEPARATE_setup.exe
```

in the directory specified by:

```ini
OutputDir=...
```

---

### 5.5 Test the installer

1. Run `SEPARATE_setup.exe`  
2. Install SEPARATE  
3. Confirm:
   - Start Menu shortcut works  
   - Desktop icon (if selected) works  
   - Application launches correctly  

---



## 6. Troubleshooting Notes

### **SciPy error: `NameError: 'obj' is not defined`**

Occurs when building with **Python 3.12**.  
Fix: Use **Python 3.11** for building the exe.

---

### **ModuleNotFoundError: jaraco / platformdirs**

Occurs because setuptools attempts to import optional modules during freezing.

Fix: Include these in the requirements file:

```
jaraco.functools
jaraco.context
jaraco.text
platformdirs
```

---

### **Missing icons / images**

Ensure:

```
images/icon.ico
```

exists and is referenced in both:

- `SEPARATE.spec`
- `separate_inno.iss`

---

## 7. Summary

To build SEPARATE for Windows:

1. Use **Python 3.11**
2. Create `.venv-separate-exe`
3. Install build dependencies
4. Run PyInstaller via `SEPARATE.spec`
5. Optionally package with Inno Setup

