from cx_Freeze import setup, Executable
import sys

# ----------------------------------------------------------
# Base Setup
base = None
if sys.platform == 'win32':
    base = 'WIN32GUI'

# ----------------------------------------------------------
# Application name
name = 'Kml'

# ----------------------------------------------------------
# Version
version = '0.0.1'

# ----------------------------------------------------------
# Icon
icon = 'icon.ico'

# ----------------------------------------------------------
# Description
description = 'View, Manage, download and stay up to date on your manga library.'

# ----------------------------------------------------------
# Description
executables = [Executable('kml.py', base=base, icon=icon)]

# ----------------------------------------------------------
# Packages
# packages = ['sqlite3']
packages = []

# ----------------------------------------------------------
# Include Files
include_files = ['icon.ico', 'kml/ui/main_window.ui']

# -----------------------------------------------------------
# Options Setup

options = {
    'build_exe': {
        'packages': packages,
        'include_files': include_files
    }
}

setup(name=name, version=version, options=options, description=description, executables=executables)

