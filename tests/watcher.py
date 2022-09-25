#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

WATCH_PATH = r"~/Documents/GitHub/sftp-sync/tests/test_folder/"
IGNORE_PATTERNS = ['.DS_Store', '.ds_store']

import os


def import_module():
    global Watcher
    
    original_working_directory = os.getcwd()
    try:
        os.chdir(r"..")  # parent directory of sftp_sync package
        print(f'Working directory was changed to {os.getcwd()}')
        from sftp_sync.watchdog_utils.watcher import Watcher
    finally:
        os.chdir(original_working_directory)
        print(f'Working directory was changed back to {os.getcwd()}')


if __name__ == "__main__":
    import_module()
    
    watcher = Watcher(WATCH_PATH, ignore_patterns=IGNORE_PATTERNS)
    watcher.watch()

