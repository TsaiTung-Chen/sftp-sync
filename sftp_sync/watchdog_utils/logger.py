#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 1 22:25:31 2022

@author: tungchentsai
"""

from watchdog.events import EVENT_TYPE_DELETED

from ..utils.base_logger import BaseLogger


class WatchdogLogger(BaseLogger):
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

