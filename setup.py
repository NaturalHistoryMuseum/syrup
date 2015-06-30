#!/usr/bin/env python
import os
import sys

import syrup

# Generic setup data used for both the distutils setup and the cx_Freeze setup.
# win32.extra_packages and win32.include_files indicate extra packages/files
# that are not automatically detected by cx_Freeze. If running into problems,
# try including the whole of numpy/scipy.

setup_data = {
    'name': 'syrup',
    'version': syrup.__version__,
    'author': 'Lawrence Hudson',
    'author_email': 'l.hudson@nhm.ac.uk',
    'url': 'https://github.com/NaturalHistoryMuseum/syrup/',
    'description': syrup.__doc__,
    'packages': ['syrup'],
    'test_suite': 'syrup.tests',
    'install_requires' : open('requirements.txt').readlines(),
    'entry_points': {
        'console_scripts': [
            'syrup = syrup.app:launch'
        ]
    },
    'win32': {
        'executables': [
            {
                'script': 'syrup.py',
                'targetName': 'syrup.exe',
                'icon': 'data/syrup.ico',
                'base': 'Win32GUI',
                'shortcutName': 'Syrup', # See http://stackoverflow.com/a/15736406
                'shortcutDir': 'ProgramMenuFolder'
            },
        ],
        'include_files': [
            ('{site_packages}/numpy', 'numpy'),
        ],
        'extra_packages': [],
        'excludes': ['Tkinter', 'ttk', 'Tkconstants', 'tcl',
                     'future.moves'    # Errors from urllib otherwise
                    ]
    }
}


def distutils_setup():
    """disttutils setup"""
    from distutils.core import setup

    setup(
        name=setup_data['name'],
        version=setup_data['version'],
        packages=setup_data['packages'],
        author=setup_data['author'],
        author_email=setup_data['author_email'],
        url=setup_data['url'],
    )

def cx_setup():
    """cx_Freeze setup. Used for building Windows installers"""
    from cx_Freeze import setup, Executable
    from distutils.sysconfig import get_python_lib

    # Set path to include files
    site_packages = get_python_lib()
    include_files = []
    for i in setup_data['win32']['include_files']:
        include_files.append((
            i[0].format(site_packages=site_packages),
            i[1]
        ))

    # Setup
    setup(
        name=setup_data['name'],
        version=setup_data['version'],
        options={
            'build_exe': {
                'packages': setup_data['packages'] + setup_data['win32']['extra_packages'],
                'excludes': setup_data['win32']['excludes'],
                'include_files': include_files,
                'icon': 'data/syrup.ico'
            },
            'bdist_msi': {
                'upgrade_code': '{fe2ed61d-cd5e-45bb-9d16-146f725e522f}'
            }
        },
        executables=[Executable(**i) for i in setup_data['win32']['executables']]
    )


# User cx_Freeze to build Windows installers, and distutils otherwise.
if 'bdist_msi' in sys.argv:
    cx_setup()
else:
    distutils_setup()
