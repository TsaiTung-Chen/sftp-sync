#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

import os
import time
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_DELETED

from .ino import dump_record, load_log, dump_log


class DelMovEventHandler(PatternMatchingEventHandler):
    def __init__(self, 
                 log_folder, 
                 patterns=['*'], 
                 ignore_patterns=[], 
                 ignore_directories=False, 
                 case_sensitive=True):
        log_folder = os.path.realpath(os.path.expanduser(log_folder))
        log_path = os.path.join(log_folder, 'watch.log')
        log = self.fetch_log(log_path)
        
        if isinstance(ignore_patterns, str):
            ignore_patterns = [ignore_patterns]
        else:
            ignore_patterns = list(ignore_patterns)
        log_files = os.path.join(log_folder, '*')
        ignore_patterns += [log_folder, log_files]  # ignore log folder & files
        
        self._log_folder = log_folder
        self._log_path = log_path
        self._log = log
        
        super().__init__(patterns=patterns, 
                         ignore_patterns=ignore_patterns, 
                         ignore_directories=ignore_directories, 
                         case_sensitive=case_sensitive)
    
    @property
    def log_folder(self):
        return self._log_folder
    
    @property
    def log_path(self):
        return self._log_path
    
    @property
    def log(self):
        return self._log
    
    def get_epoch_time(self):
        return time.time()
    
    def get_formatted_time(self, epoch_time):
        time_format = "%Y-%m-%d_%H:%M:%S"
        structured_time = time.localtime(epoch_time)
        
        return time.strftime(time_format, structured_time)
    
    def make_record(self, event):
        event_type = event.event_type
        epoch_time = self.get_epoch_time()
        formatted_time = self.get_formatted_time(epoch_time)
        
        if event_type == EVENT_TYPE_DELETED:
            return {
                event.src_path: {
                    "event": event_type, 
                    "is_dir": event.is_directory, 
                    "time": epoch_time, 
                    "localtime": formatted_time
                }
            }
        
        # EVENT_TYPE_MOVED
        return {
            event.dest_path: {
                "event": event_type, 
                "is_dir": event.is_directory, 
                "time": epoch_time, 
                "localtime": formatted_time, 
                "source": event.src_path
            }
        }
    
    def update_log(self, record):
        previous_length = len(self.log)
        self._log.update(record)
        current_length = len(self.log)
        overwrote = (previous_length == current_length)
        
        return overwrote
    
    def fetch_log(self, log_path):
        if os.path.isfile(log_path):
            return load_log(log_path)
        
        log_folder = os.path.dirname(log_path)
        if not os.path.isdir(log_folder):
            os.makedirs(log_folder, exist_ok=True)
        open(log_path, 'w').close()  # create an empty log file
        
        return dict()  # an empty dictionary
    
    def write_down(self, event):
        record = self.make_record(event)
        overwrote = self.update_log(record)
        
        if overwrote:
            dump_log(self.log, self.log_path)
        else:
            dump_record(record, fpath=self.log_path)
    
    def on_deleted(self, event):
        self.write_down(event)
    
    def on_moved(self, event):
        self.write_down(event)

