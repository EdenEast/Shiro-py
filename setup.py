from cx_Freeze import setup, Executable
import sys

# ----------------------------------------------------------
# Base Setup
base = None
if sys.platform == 'win32':
    base = 'WIN32GUI'

# ----------------------------------------------------------
# Application name
name = 'Shiro'

# ----------------------------------------------------------
# Version
version = '1.0.3'

# ----------------------------------------------------------
# Icon
icon = 'icon.ico'

# ----------------------------------------------------------
# Description
description = 'View, Manage, download and stay up to date on your manga library.'

# ----------------------------------------------------------
# Description
executables = [Executable('shiro.py', base=base, icon=icon)]

# ----------------------------------------------------------
# Packages
# packages = ['sqlite3']
packages = []

# ----------------------------------------------------------
# Include Files
include_files = [icon, 'shiro/ui/main_window.ui']

# -----------------------------------------------------------
# Options Setup

options = {
    'build_exe': {
        'packages': packages,
        'include_files': include_files
    }
}

setup(name=name, version=version, options=options, description=description, executables=executables)

