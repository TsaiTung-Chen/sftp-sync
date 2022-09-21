#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

from watchdog.observers import Observer


class IndicativeObserver(Observer):
    def start(self):
        super().start()
        print('Now start watching events occurring on the monitored ' \
              'location:')
        
        for watch, handlers in self._handlers.items():
            assert len(handlers) == 1, handlers
            delete_event_handler = list(handlers)[0]
            
            print(
                f'{watch.path}\n' \
                f'recursively: {watch.is_recursive}\n' \
                f'log path: {delete_event_handler.log_path}\n' \
                f'patterns: {delete_event_handler.patterns}\n' \
                f'ignore patterns: {delete_event_handler.ignore_patterns}\n' \
                f'case sensitive: {delete_event_handler.case_sensitive}'
            )

