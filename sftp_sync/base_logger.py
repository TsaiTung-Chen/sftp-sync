#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 1 22:25:31 2022

@author: tungchentsai
"""

import os
import time
import json

from watchdog.events import (EVENT_TYPE_DELETED, 
                             EVENT_TYPE_MOVED, 
                             EVENT_TYPE_MODIFIED)


END_OF_RECORD = ',\n'
LENGTH_OF_EOR = len(END_OF_RECORD)

DELETED = 'deleted'
MOVED = 'moved'
MODIFIED = 'modified'

event_type_mapping = {
    EVENT_TYPE_DELETED: DELETED, 
    EVENT_TYPE_MOVED: MOVED, 
    EVENT_TYPE_MODIFIED: MODIFIED
}


class BaseLogger:
    END_OF_RECORD = END_OF_RECORD
    LENGTH_OF_EOR = LENGTH_OF_EOR
    
    DELETED = DELETED
    MOVED = MOVED
    MODIFIED = MODIFIED
    
    sftp_sync_folder = '.sftp-sync'
    filename = None
    
    def __init__(self, home_path):
        if self.filename is None:
            raise NotImplementedError
        
        log_path = os.path.join(home_path, self.sftp_sync_folder, self.filename)
        contents = self.load(log_path)
        
        self._home_path = home_path
        self._log_path = log_path
        self._contents = contents
    
    @property
    def home_path(self):
        return self._home_path
    
    @property
    def log_path(self):
        return self._log_path
    
    @property
    def contents(self):
        return self._contents
    
    @classmethod
    def convert_event_type(event_type):
        return convert_event_type(event_type)
    
    @classmethod
    def current_epoch_time(cls):
        return current_time()
    
    @classmethod
    def format_time(cls, epoch_time):
        return format_time(epoch_time)
	
    def load(self, log_path):
        if os.path.isfile(log_path):
            return load_log(log_path)
        
        log_folder = os.path.dirname(log_path)
        if not os.path.isdir(log_folder):
            os.makedirs(log_folder, exist_ok=True)
        open(log_path, 'w').close()  # create an empty log file
        
        return dict()  # an empty dictionary
    
    def get_record(self, path, default=None):
        return self.contents.get(path, default)
    
    def _make_record(self, *args, **kwargs):
        raise NotImplementedError()
        return dict()
    
    def _update(self, record):
        previous_length = len(self.contents)
        self.contents._update(record)
        
        return len(self.contents) == previous_length  # been overwritten or not
    
    def log(self, *args, **kwargs):  # main
        record = self._make_record(*args, **kwargs)
        overwrite = self._update(record)
        
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


def convert_event_type(event_type):
    if event_type in event_type_mapping:
        return event_type_mapping[event_type]
    raise ValueError(f"Unrecognized event type: {event_type}. "
                     f"Must be one of {list(event_type_mapping.keys())}")


def current_time():
    return time.time()


def format_time(epoch_time):
    time_format = "%Y-%m-%d_%H:%M:%S"
    structured_time = time.localtime(epoch_time)
    
    return time.strftime(time_format, structured_time)


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
    for path, value in log.items():
        record = {path: value}
        json_string = json.dumps(record, ensure_ascii=False)
        truncated_json_string = json_string[1:-1]
        list_of_strings.append(truncated_json_string)
    log_string = END_OF_RECORD.join(list_of_strings) + END_OF_RECORD
    
    with open(fpath, mode=mode, encoding='utf-8') as file:
#        file.truncate(0)  # delete the original contents
#        file.seek(0)  # move the cursor to the beginning
        file.write(log_string)

