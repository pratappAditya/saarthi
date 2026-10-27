"""
Saarthi Windows Desktop Application Standalone Installer Setup Wizard.
Presents a clean Windows installation GUI to extract Saarthi binaries, create
shortcuts, register uninstaller, and launch the application.
"""

import os
import sys
import shutil
import zipfile
import winreg
import logging
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("SaarthiInstaller")

APP_NAME = "Saarthi"
APP_VERSION = "1.0.0-beta.1"
PUBLISHER = "Saarthi AI Team"
DEFAULT_INSTALL_DIR = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\Public"), "Programs", "Saarthi")

def create_windows_shortcut(target_exe: str, shortcut_path: str, description: str = "Saarthi AI Career Companion"):
    """Creates a Windows .lnk shortcut using VBScript fallback with clean quote escaping."""
    target_clean = os.path.abspath(target_exe).replace('"', '""')
    workdir_clean = os.path.dirname(os.path.abspath(target_exe)).replace('"', '""')
    shortcut_clean = os.path.abspath(shortcut_path).replace('"', '""')
    vbs_script = f"""Set WshShell = CreateObject("WScript.Shell")
Set shortcut = WshShell.CreateShortcut("{shortcut_clean}")
shortcut.TargetPath = "{target_clean}"
shortcut.WorkingDirectory = "{workdir_clean}"
shortcut.Description = "{description}"
shortcut.Save
"""
    vbs_path = os.path.join(os.environ.get("TEMP", "C:\\Temp"), f"create_shortcut_{os.getpid()}.vbs")
    try:
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_script)
        subprocess.run(["cscript", "//Nologo", vbs_path], check=True, capture_output=True)
    except Exception as e:
        logger.warning(f"Shortcut creation notice: {e}")
    finally:
        if os.path.exists(vbs_path):
            try:
                os.remove(vbs_path)
            except Exception:
                pass

def create_uninstaller_script(install_dir: str) -> str:
    """Creates a clean uninstallation script preserving user databases in %LOCALAPPDATA%\\Saarthi by default."""
    uninstaller_path = os.path.join(install_dir, "uninstall.bat")
    bat_content = f"""@echo off
setlocal
echo ========================================================
echo   Saarthi AI Career Companion — Uninstallation Wizard
echo ========================================================
echo.

REM 1. Remove Desktop and Start Menu Shortcuts
set "DESK_LNK=%USERPROFILE%\\Desktop\\Saarthi.lnk"
if exist "%DESK_LNK%" del /f /q "%DESK_LNK%" >nul 2>&1
set "START_LNK=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Saarthi.lnk"
if exist "%START_LNK%" del /f /q "%START_LNK%" >nul 2>&1

REM 2. Remove Windows Registry Uninstall Entry
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Saarthi" /f >nul 2>&1

REM 3. Handle User Personal Data
if "%1"=="--delete-data" (
    echo [ACTION] Removing personal data and SQLite databases in %LOCALAPPDATA%\\Saarthi...
    if exist "%LOCALAPPDATA%\\Saarthi" rmdir /s /q "%LOCALAPPDATA%\\Saarthi"
) else (
    echo [PRESERVED] User personal data and SQLite databases in %LOCALAPPDATA%\\Saarthi preserved.
    echo To wipe user data, re-run uninstaller with: uninstall.bat --delete-data
)

REM 4. Self-deleting removal of application binaries directory
echo [ACTION] Removing application binaries from {install_dir}...
cd \\
start /b "" cmd /c "timeout /t 1 /nobreak >nul & rmdir /s /q \\"{install_dir}\\""
echo Saarthi uninstalled successfully.
"""
    with open(uninstaller_path, "w", encoding="utf-8") as f:
        f.write(bat_content)
    return uninstaller_path

def register_uninstall(install_dir: str):
    """Registers Saarthi in Windows Registry Add/Remove Programs."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Saarthi"
    uninstaller_path = os.path.join(install_dir, "uninstall.bat")
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, f"Saarthi (v{APP_VERSION})")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, os.path.join(install_dir, "Saarthi.exe"))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_path}"')
    except Exception as e:
        logger.warning(f"Uninstall registry notice: {e}")

def extract_and_install(target_dir: str, create_desktop: bool = True, create_start: bool = True, progress_cb=None) -> str:
    """Extracts payload and registers application."""
    os.makedirs(target_dir, exist_ok=True)
    meipass = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    payload_zip = os.path.join(meipass, "payload.zip")
    if not os.path.exists(payload_zip):
        payload_zip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payload.zip")

    if os.path.exists(payload_zip):
        with zipfile.ZipFile(payload_zip, 'r') as zf:
            members = zf.infolist()
            total = len(members)
            for idx, member in enumerate(members):
                zf.extract(member, target_dir)
                if progress_cb and idx % 25 == 0:
                    progress_cb(int((idx / total) * 85))
    else:
        # Fallback to dev dist/Saarthi
        dev_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist", "Saarthi")
        if os.path.exists(dev_dist):
            shutil.copytree(dev_dist, target_dir, dirs_exist_ok=True)
        else:
            raise FileNotFoundError("Could not locate Saarthi package payload.zip.")

    if progress_cb:
        progress_cb(90)

    target_exe = os.path.join(target_dir, "Saarthi.exe")
    create_uninstaller_script(target_dir)
    register_uninstall(target_dir)

    if create_desktop:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(desktop):
            create_windows_shortcut(target_exe, os.path.join(desktop, "Saarthi.lnk"))

    if create_start:
        start_menu = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
        if os.path.exists(start_menu):
            create_windows_shortcut(target_exe, os.path.join(start_menu, "Saarthi.lnk"))

    if progress_cb:
        progress_cb(100)

    return target_exe

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION} Setup")
        self.root.geometry("560x380")
        self.root.resizable(False, False)

        # Style
        style = ttk.Style()
        style.theme_use("clam")

        # Header Frame
        header_frame = tk.Frame(root, bg="#0F172A", height=70)
        header_frame.pack(fill="x", side="top")
        
        title_label = tk.Label(header_frame, text=f"Install {APP_NAME}", font=("Segoe UI", 16, "bold"), fg="#38BDF8", bg="#0F172A")
        title_label.pack(anchor="w", padx=20, pady=(12, 2))
        
        subtitle_label = tk.Label(header_frame, text=f"Local-First AI Career Operating System (v{APP_VERSION})", font=("Segoe UI", 9), fg="#94A3B8", bg="#0F172A")
        subtitle_label.pack(anchor="w", padx=20)

        # Content Frame
        content_frame = tk.Frame(root, padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        desc_label = tk.Label(content_frame, text="Select destination folder for Saarthi installation:", font=("Segoe UI", 10))
        desc_label.pack(anchor="w", pady=(0, 8))

        # Path Selection
        path_frame = tk.Frame(content_frame)
        path_frame.pack(fill="x", pady=5)

        self.path_var = tk.StringVar(value=DEFAULT_INSTALL_DIR)
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, font=("Segoe UI", 9))
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_folder)
        browse_btn.pack(side="right")

        # Options
        self.desktop_icon_var = tk.BooleanVar(value=True)
        desktop_chk = ttk.Checkbutton(content_frame, text="Create a Desktop shortcut", variable=self.desktop_icon_var)
        desktop_chk.pack(anchor="w", pady=(15, 5))

        self.start_menu_var = tk.BooleanVar(value=True)
        start_chk = ttk.Checkbutton(content_frame, text="Create a Start Menu shortcut", variable=self.start_menu_var)
        start_chk.pack(anchor="w", pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(content_frame, mode="determinate")
        self.progress.pack(fill="x", pady=(20, 5))
        self.status_var = tk.StringVar(value="Ready to install.")
        self.status_label = tk.Label(content_frame, textvariable=self.status_var, font=("Segoe UI", 9, "italic"), fg="#64748B")
        self.status_label.pack(anchor="w")

        # Footer Frame
        footer_frame = tk.Frame(root, bg="#F1F5F9", height=50)
        footer_frame.pack(fill="x", side="bottom")

        self.install_btn = ttk.Button(footer_frame, text="Install", command=self.start_installation)
        self.install_btn.pack(side="right", padx=20, pady=10)

        cancel_btn = ttk.Button(footer_frame, text="Cancel", command=root.quit)
        cancel_btn.pack(side="right", padx=(0, 10), pady=10)

    def browse_folder(self):
        selected = filedialog.askdirectory(initialdir=self.path_var.get())
        if selected:
            self.path_var.set(os.path.normpath(selected))

    def update_progress(self, val: int):
        self.progress["value"] = val
        self.root.update()

    def start_installation(self):
        target_dir = os.path.normpath(self.path_var.get())
        self.install_btn.config(state="disabled")
        self.status_var.set("Extracting Saarthi bundle...")
        self.root.update()

        try:
            target_exe = extract_and_install(
                target_dir,
                create_desktop=self.desktop_icon_var.get(),
                create_start=self.start_menu_var.get(),
                progress_cb=self.update_progress
            )

            self.status_var.set("Installation complete!")
            self.root.update()

            ans = messagebox.askyesno("Saarthi Setup", "Installation completed successfully!\n\nWould you like to launch Saarthi now?")
            if ans and os.path.exists(target_exe):
                subprocess.Popen([target_exe], cwd=target_dir)

            self.root.quit()

        except Exception as e:
            logger.error(f"Installation failed: {e}", exc_info=True)
            messagebox.showerror("Saarthi Setup Error", f"Installation failed:\n{e}")
            self.install_btn.config(state="normal")

def main():
    # Silent / Unattended Installation Mode
    args = sys.argv[1:]
    is_silent = any(arg.upper() in ("/S", "/SILENT", "--SILENT") for arg in args)
    
    target_dir = DEFAULT_INSTALL_DIR
    for arg in args:
        if arg.startswith("--dir="):
            target_dir = os.path.normpath(arg.split("=", 1)[1].strip('"'))
        elif arg.startswith("/DIR="):
            target_dir = os.path.normpath(arg.split("=", 1)[1].strip('"'))

    if is_silent:
        logger.info(f"Executing silent installation to {target_dir}...")
        try:
            exe_path = extract_and_install(target_dir, create_desktop=True, create_start=True)
            print(f"INSTALL_SUCCESS: Saarthi installed successfully to {target_dir}")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Silent installation failed: {e}", exc_info=True)
            print(f"INSTALL_ERROR: {e}")
            sys.exit(1)

    # Graphical Wizard Mode
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
