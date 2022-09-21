#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

WATCH_PATH = r"~/Documents/GitHub/sftp-sync/tests/test_folder/"
IGNORE_PATTERNS = ['.DS_Store', '.ds_store']



if __name__ == "__main__":
    import os
    
#    original_working_directory = os.getcwd()
    try:
#        os.chdir(r"..")
#        print(f'Working directory was changed to {os.getcwd()}')
        
        watch_module = 'sftp_sync.watch'
        ignore_patterns = ' '.join(IGNORE_PATTERNS)
        os.system(f"python -m {watch_module} {WATCH_PATH} {ignore_patterns}")
    finally:
#        os.chdir(original_working_directory)
        pass

