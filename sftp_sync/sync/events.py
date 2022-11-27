#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 23:47:09 2022

@author: tungchentsai
"""

from ..base_logger import DELETED, MOVED, MODIFIED, format_time



class BaseEvent:
    def __init__(self, src_path, time):
        self._src_path = src_path
        self._time = time
    
    @property
    def src_path(self):
        return self._src_path
    
    @property
    def time(self):
        return self._time
    
    @property
    def formatted_time(self):
        return format_time(self.time)
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return ', '.join([
            f"<{self.__class__.__name__}: event_type={self.event_type}",
            f"src_path={repr(self.src_path)}",
            f"time={self.formatted_time}>"
        ])


class DeletedEvent(BaseEvent):
    @classmethod
    @property
    def event_type(cls):
        return DELETED


class ModifiedEvent(BaseEvent):
    @classmethod
    @property
    def event_type(cls):
        return MODIFIED


class MovedEvent(BaseEvent):
    @classmethod
    @property
    def event_type(cls):
        return MOVED
    
    def __init__(self, src_path, dest_path, time):
        super().__init__(src_path, time=time)
        self._dest_path = dest_path
    
    @property
    def dest_path(self):
        return self._dest_path
    
    def __repr__(self):
        return ', '.join([
            f"<{self.__class__.__name__}: event_type={self.event_type}",
            f"src_path={repr(self.src_path)}",
            f"dest_path={repr(self.dest_path)}",
            f"time={self.formatted_time}>"
        ])


class NoneEvent(BaseEvent):
    @classmethod
    @property
    def event_type(cls):
        return 'none'
    
    def __init__(self):
        pass
    
    def __repr__(self):
        return f'<{self.__class__.__name__}: event_type={self.event_type}>'

