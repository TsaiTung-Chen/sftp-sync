#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:15:08 2022

@author: tungchentsai
"""

FILE_PATH = r"~/Documents/GitHub/sftp-sync/tests/temp.txt"


LOG = {
       "file path 1": {"is_directory": True, "hooks_left": ['device_01']}, 
       "file path 2": {"is_directory": False, "hooks_left": ['device_02']}
}

import os


def import_module():
    global dump_jsonline, load_jsonlines
    
    original_working_directory = os.getcwd()
    try:
        os.chdir(r"..")  # parent directory of sftp_sync package
        print(f'Working directory was changed to {os.getcwd()}')
        from sftp_sync.utils.ino import dump_jsonline, load_jsonlines
    finally:
        os.chdir(original_working_directory)
        print(f'Working directory was changed back to {os.getcwd()}')


if __name__ == '__main__':
    import_module()
    
    fpath = os.path.realpath(os.path.expanduser(FILE_PATH))
    
    dump_jsonline(LOG, fpath)
    jsonlist = load_jsonlines(fpath)
    
    print(jsonlist)

