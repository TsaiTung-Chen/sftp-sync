#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

class Watcher:
    def __init__(self, 
                 watch_path, 
                 ignore_patterns=[], 
                 case_sensitive=True, 
                 recursive=True, 
                 log_folder=None):
        import os
        from .observer import IndicativeObserver
        from .event_handler import DelMovEventHandler
        
        log_folder = log_folder or os.path.join(watch_path, '.sftp-sync')
        
        event_handler = DelMovEventHandler(log_folder, 
                                           patterns=['*'], 
                                           ignore_patterns=ignore_patterns, 
                                           case_sensitive=case_sensitive)
        observer = IndicativeObserver()
        observer.schedule(event_handler, watch_path, recursive=recursive)
        
        self.observer = observer
    
    def watch(self):
        self.observer.start()
        try:
            while True:
                user_input = input('Input Q to stop watching:\n')
                if user_input.upper() == 'Q':
                    break
        finally:
            self.observer.stop()
            self.observer.join()
            print('Stopped watching.')

