#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 17:47:43 2022

@author: tungchentsai
"""

from ..base_logger import BaseLogger
from ..watch.logger import WatchLogger


class LocalLogger(BaseLogger):
    filename = WatchLogger.filename
    
    def get_rmtime(self, path, default=None):
        record = self.get_record(path, default=None)
        if record is not None and record.get('event', None) == self.DELETED:
            return record['time']
        return default
    
#TODO    def get_mvtime(self, path, default=None):
#        record = self.get_record(path, default=None)
#        if record is not None and record.get('event', None) == self.MOVED:
#            return record['time']
#        return default


class RemoteLogger(BaseLogger):
    filename = 'remote.log'
    
    def get_rmtime(self, path, default=None):
        record = self.get_record(path, default=None)
        if record is not None and record.get('event', None) == self.DELETED:
            return record['time']
        return default
    
#TODO    def get_mvtime(self, path, default=None):
#        record = self.get_record(path, default=None)
#        if record is not None and record.get('event', None) == self.MOVED:
#            return record['time']
#        return default
    
    def get_mdtime(self, path, default=None):
        record = self.get_record(path, default=None)
        if record is not None and record.get('event', None) == self.MODIFIED:
            return record['time']
        return default
    
    def _make_record(self, event):
        if event.event_type in {self.DELETED, self.MODIFIED}:
            return {
                event.src_path: {
                    "event": event.event_type, 
                    "time": event.time, 
                    "localtime": event.formatted_time
                }
            }
        """#TODO
        elif event.event_type == self.MOVED:
            return {
                event.dest_path: {
                    "event": event.event_type, 
                    "time": event.time, 
                    "localtime": event.formatted_time, 
                    "source": event.src_path
                }
            }
        """
        raise ValueError(f"Unrecognized event type: {event.event_type}")

