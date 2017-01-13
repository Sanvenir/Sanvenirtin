#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from cx_Freeze import setup, Executable
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
	'build': {'build_exe' : 'sanvenirtin/build'},
    'build_exe': {
		'build_exe' : 'sanvenirtin',
		'include_files': ('res', 'sav')
    },
}

executables = [
    Executable('scene.py', base=base, targetName = "scene.exe")
]

setup(name='Scene',
      version='1.02',
      description='Game test',
      options=options,
      executables=executables
      )
