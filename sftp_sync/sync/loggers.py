#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 17:47:43 2022

@author: tungchentsai
"""

from ..utils.base_logger import BaseLogger, DELETED, MOVED, MODIFIED


class LocalLogger(BaseLogger):
    def get_rmtime(self, key, default=None):
        record = self.get_record(key, default=None)
        if record is not None and record.get('event', None) == DELETED:
            return record['time']
        return default
    
#TODO    def get_mvtime(self, key, default=None):
#        record = self.get_record(key, default=None)
#        if record is not None and record.get('event', None) == MOVED:
#            return record['time']
#        return default


class RemoteLogger(LocalLogger):
    def get_rmtime(self, key, default=None):
        record = self.get_record(key, default=None)
        if record is not None and record.get('event', None) == DELETED:
            return record['time']
        return default
    
#TODO    def get_mvtime(self, key, default=None):
#        record = self.get_record(key, default=None)
#        if record is not None and record.get('event', None) == MOVED:
#            return record['time']
#        return default
    
    def get_mdtime(self, key, default=None):
        record = self.get_record(key, default=None)
        if record is not None and record.get('event', None) == MODIFIED:
            return record['time']
        return default
    
    def make_record(self, *args, **kwargs):
        pass

