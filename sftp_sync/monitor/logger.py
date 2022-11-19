#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 1 22:25:31 2022

@author: tungchentsai
"""

from watchdog.events import (EVENT_TYPE_DELETED, 
                             EVENT_TYPE_MOVED, 
                             EVENT_TYPE_MODIFIED)

from ..base_logger import BaseLogger, DELETED, MOVED, MODIFIED


event_type_mapping = {
    EVENT_TYPE_DELETED: DELETED, 
    EVENT_TYPE_MOVED: MOVED, 
    EVENT_TYPE_MODIFIED: MODIFIED
}


class MonitorLogger(BaseLogger):
    event_type_mapping = event_type_mapping
    
    def _make_record(self, event):
        event_type = convert_event_type(event.event_type)
        epoch_time = self.current_epoch_time()
        formatted_time = self.current_formatted_time(epoch_time)
        
        if event_type == DELETED:
            return {
                event.src_path: {
                    "event": event_type, 
                    "time": epoch_time, 
                    "localtime": formatted_time
                }
            }
        
        # MOVED
        return {
            event.dest_path: {
                "event": event_type, 
                "time": epoch_time, 
                "localtime": formatted_time, 
                "source": event.src_path
            }
        }


def convert_event_type(event_type):
    return event_type_mapping[event_type]

