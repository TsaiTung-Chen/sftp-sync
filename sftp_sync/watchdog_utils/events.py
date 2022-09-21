#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

import os
import time
from watchdog.events import PatternMatchingEventHandler


class DeleteEventHandler(PatternMatchingEventHandler):
    def __init__(self, log_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log_path = log_path

    @property
    def log_path(self):
        return self._log_path
    
    def on_deleted(self, event):
        what = 'directory' if event.is_directory else 'file'
        print("!!")
        print(f'Deleted {what}: {event.src_path}')
        return
        
