#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 1 22:25:31 2022

@author: tungchentsai
"""

import os
import time
import json


END_OF_RECORD = ',\n'
LENGTH_OF_EOR = len(END_OF_RECORD)

DELETED = 'deleted'
MOVED = 'moved'
MODIFIED = 'modified'


class BaseLogger:
    def __init__(self, log_path):
        log_path = os.path.realpath(os.path.expanduser(log_path))
        contents = self.fetch_log(log_path)
        
        self._log_path = log_path
        self._contents = contents
    
    @property
    def log_path(self):
        return self._log_path
    
    @property
    def contents(self):
        return self._contents
	
    def fetch_log(self, log_path):
        if os.path.isfile(log_path):
            return load_log(log_path)
        
        log_folder = os.path.dirname(log_path)
        if not os.path.isdir(log_folder):
            os.makedirs(log_folder, exist_ok=True)
        open(log_path, 'w').close()  # create an empty log file
        
        return dict()  # an empty dictionary
    
    def current_epoch_time(self):
        return time.time()
    
    def current_formatted_time(self, epoch_time):
        time_format = "%Y-%m-%d_%H:%M:%S"
        structured_time = time.localtime(epoch_time)
        
        return time.strftime(time_format, structured_time)
    
    def get_record(self, key, default=None):
        return self.contents.get(key, default)
    
    def make_record(self, *args, **kwargs):
        raise NotImplementedError()
        return dict()
    
    def update_log(self, record):
        previous_length = len(self.contents)
        self.contents.update(record)
        current_length = len(self.contents)
        overwrite = (previous_length == current_length)
        
        return overwrite
    
    def log(self, *args, **kwargs):
        record = self.make_record(*args, **kwargs)
        overwrite = self.update_log(record)
        
        # update log file
        if overwrite:
            self.dump(self.log_path)
        else:
            self.dump_record(record, fpath=self.log_path)
        
        return record
    
    def dump_record(self, record, fpath, mode='a'):
        dump_record(record, fpath, mode=mode)
    
    def dump(self, fpath, mode='w'):
        dump_log(self.contents, fpath, mode=mode)



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
    log_string = END_OF_RECORD.join(list_of_strings) + \
        END_OF_RECORD
    
    with open(fpath, mode=mode, encoding='utf-8') as file:
        file.truncate(0)  # delete the original contents
        file.seek(0)  # move the cursor to the beginning
        file.write(log_string)

