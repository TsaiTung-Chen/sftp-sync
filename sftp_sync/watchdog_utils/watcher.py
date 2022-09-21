#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

class Watcher:
    def __init__(self, watch_path, ignore_patterns=[]):
        import os
        from .observers import IndicativeObserver
        from .events import DeleteEventHandler
        
        watch_path = os.path.realpath(os.path.expanduser(watch_path))
        
        log_path = os.path.join(watch_path, '.sftp-sync', 'log.txt')
        ignore_patterns.append(os.path.dirname(log_path))
        
        event_handler = DeleteEventHandler(log_path=log_path, 
                                           patterns=['*'], 
                                           ignore_patterns=ignore_patterns, 
                                           case_sensitive=True)
        observer = IndicativeObserver()
        observer.schedule(event_handler, watch_path, recursive=True)
        
        self._observer = observer
    
    @property
    def observer(self):
        return self._observer
    
    def watch(self):
        import time
        
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

