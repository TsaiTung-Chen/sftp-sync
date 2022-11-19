#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

ABS_WATCH_PATH = r"~/Documents/GitHub/sftp-sync/tests/test_folder/"
IGNORE_PATTERNS = ['.DS_Store', '.ds_store']

import os


def run_module(module_name, *args):
    arguments = ' '.join(args)
    command = f'python -m {module_name} {arguments}'
    
    original_working_directory = os.getcwd()
    try:
        os.chdir(r"..")  # parent directory of sftp_sync package
        print(f'Working directory was changed to {os.getcwd()}')
        os.system(command)
    finally:
        os.chdir(original_working_directory)
        print(f'Working directory was changed back to {os.getcwd()}')


if __name__ == "__main__":
    watch_module = 'watch'
    watch_path = os.path.realpath(os.path.expanduser(ABS_WATCH_PATH))
    
    run_module(watch_module, watch_path, *IGNORE_PATTERNS)

