#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 22:25:31 2022

@author: tungchentsai
"""

import json


END_OF_RECORD = ',\n'
LENGTH_OF_EOR = len(END_OF_RECORD)


def dump_record(record, fpath, mode='a'):
    """
    The example contents of an output file:
    "/event/source/path": {"is_directory": false, "time": 0, "localtime": "1970-01-01_08:00:00"}
    
    
    """
    
    json_string = json.dumps(record, ensure_ascii=False)
    truncated_json_string = json_string[1:-1] + END_OF_RECORD
    
    with open(fpath, mode=mode, encoding='utf-8') as file:
        file.write(truncated_json_string)


def load_log(fpath):
    """
    The example contents of an input file:
    "/event/source/path": {"is_directory": false, "time": 0, "localtime": "1970-01-01_08:00:00"}
    "/event/source/path": {"is_directory": ture, "time": 0, "localtime": "1970-01-01_08:00:00"}
    
    
    """
    
    with open(fpath, 'r', encoding='utf-8') as file:
        log_string = file.read()
    log_string = log_string[:-LENGTH_OF_EOR]
    json_string = log_string.join(['{', '}'])
    
    return json.loads(json_string)


def dump_log(log, fpath, mode='w'):
    """
    The example contents of an output file:
    "/event/source/path": {"is_directory": false, "time": 0, "localtime": "1970-01-01_08:00:00"}
    "/event/source/path": {"is_directory": ture, "time": 0, "localtime": "1970-01-01_08:00:00"}
    
    
    """
    
    list_of_strings = []
    for key, value in log.items():
        record = {key: value}
        json_string = json.dumps(record, ensure_ascii=False)
        truncated_json_string = json_string[1:-1]
        list_of_strings.append(truncated_json_string)
    log_string = END_OF_RECORD.join(list_of_strings) + END_OF_RECORD
    
    with open(fpath, mode=mode, encoding='utf-8') as file:
        file.truncate(0)  # delete the original contents
        file.seek(0)  # move the cursor to the beginning
        file.write(log_string)

