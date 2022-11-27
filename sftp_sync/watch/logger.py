#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 1 22:25:31 2022

@author: tungchentsai
"""

from ..base_logger import BaseLogger


class WatchLogger(BaseLogger):
    filename = 'watch.log'
    
    def _make_record(self, event):
        event_type = self.convert_event_type(event.event_type)
        epoch_time = self.current_epoch_time()
        formatted_time = self.format_time(epoch_time)
        
        if event_type == self.DELETED:
            return {
                event.src_path: {
                    "event": event_type, 
                    "time": epoch_time, 
                    "localtime": formatted_time
                }
            }
        """#TODO
        elif event_type == self.MOVED:
            return {
                event.dest_path: {
                    "event": event_type, 
                    "time": epoch_time, 
                    "localtime": formatted_time, 
                    "source": event.src_path
                }
            }
        """
        raise ValueError(f"Unrecognized event type: {event_type}")

