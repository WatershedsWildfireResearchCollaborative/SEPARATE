# 🛠 Building and Packaging SEPARATE on macOS

This guide documents the full process for setting up the SEPARATE GUI tool on a clean Mac system, bundling it into a `.app`, and packaging it as a `.dmg` installer.

---

##  Environment Setup

1. **Install Homebrew** (if not already):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3.11 (Homebrew version):**
   ```bash
   brew install python@3.11
   ```

3. **Install tkinter support** (required, not bundled with Homebrew Python):
   ```bash
   brew install python-tk@3.11
   ```

4. **Create and activate a virtual environment:**
   ```bash
   python3.11 -m venv separate_mac
   source separate_mac/bin/activate
   ```

5. **Install Python dependencies:**
PySimpleGui.whl is currently provided in the build_installer folder

   ```bash
   pip install -r requirements.txt
   pip install path/to/PySimpleGUI.whl
   ```

---

##  Run SEPARATE GUI

Verify everything works:
```bash
python SEPARATE_GUI.py
```
If the app opens and runs successfully, you're ready to bundle it.

---

## Build `.app` with PyInstaller

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Generate a spec file:**
   ```bash
   pyi-makespec --windowed --icon=images/icon.icns SEPARATE_GUI.py
   ```

3. **Edit the `.spec` file:** 
   [or copy the separate_mac.spec file contents into the new spec file]
   - Add the `images/` and `functions/` folders to `datas`
   - Add `matplotlib` backends and `functions` submodules to `hiddenimports`
   - Add a `BUNDLE(...)` section at the bottom
   - Use `Path(".").resolve()` instead of `__file__`

4. **Build the app:**
   ```bash
   pyinstaller SEPARATE_GUI.spec
   ```

---

##  Package as `.dmg`

1. **Install `create-dmg`:**
   ```bash
   brew install create-dmg
   ```

2. **Run `create-dmg`:**
   ```bash
   create-dmg \
     --volname "SEPARATE" \
     --window-pos 200 120 \
     --window-size 600 400 \
     --icon-size 100 \
     --icon "SEPARATE_GUI.app" 175 190 \
     --app-drop-link 425 190 \
     SEPARATE.dmg \
     dist/
   ```


---

## Output Summary

- Final `.app` is located at: `dist/SEPARATE_GUI.app`
- Final `.dmg` is located at: `dist/SEPARATE.dmg`

These are the only files you need to distribute the Mac version of SEPARATE.
