#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

import os
from watchdog.events import PatternMatchingEventHandler

from .logger import MonitorLogger


class DeleteMoveEventHandler(PatternMatchingEventHandler):
    def __init__(self, 
                 log_folder, 
                 patterns=['*'], 
                 ignore_patterns=[], 
                 ignore_directories=False, 
                 case_sensitive=True):
        log_folder = os.path.realpath(os.path.expanduser(log_folder))
        log_path = os.path.join(log_folder, 'watch.log')
        logger = MonitorLogger(log_path)
        
        if isinstance(ignore_patterns, str):
            ignore_patterns = [ignore_patterns]
        else:
            ignore_patterns = list(ignore_patterns)
        log_files = os.path.join(log_folder, '*')
        ignore_patterns += [log_folder, log_files]  # ignore log folder & files
        
        super().__init__(patterns=patterns, 
                         ignore_patterns=ignore_patterns, 
                         ignore_directories=ignore_directories, 
                         case_sensitive=case_sensitive)
        
        self._log_folder = log_folder
        self._log_path = log_path
        self._logger = logger
    
    @property
    def log_folder(self):
        return self._log_folder
    
    @property
    def log_path(self):
        return self._log_path
    
    @property
    def logger(self):
        return self._logger
    
    def on_deleted(self, event):
        self.logger.log(event)
    
#TODO    def on_moved(self, event):
#        self.logger.log(event)

