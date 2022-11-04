#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 22:54:22 2022

@author: tungchentsai
"""

import functools


class Synchronizer:
    def __init__(self, local_file_system, remote_file_system):
        self._local_file_system = local_file_system
        self._remote_file_system = remote_file_system
        self._queue = []
        self._queue_str = []
    
    @property
    def local_file_system(self):
        return self._local_file_system
    
    @property
    def remote_file_system(self):
        return self._remote_file_system
    
    @property
    def queue(self):
        return self._queue
    
    @property
    def queue_str(self):
        return self._queue_str
    
    def queue_up(self, func, *args, **kwargs):
        wrapper = functools.partial(func, *args, **kwargs)
        self.queue.append(wrapper)
    
    def sync_file(self, pathA, pathB, fsA, fsB, skip=[], mark=False):
        mdtimeA = fsA.get_mdtime(pathA)
        rmtimeB = fsB.get_rmtime(pathB, 0)
        
        if mark:
            skip.append(pathB)  # skip `pathB` after `sync_file` method
        
        if rmtimeB > mdtimeA:  # if pathB was removed later
            self.queue_str.append(f'rm {pathA}')
            self.queue_up(fsA.rm, pathA)
            return
        elif not fsB.exists(pathB) or mdtimeA > fsB.get_mdtime(pathB):
            # if `pathB` does not exist or `pathA` is newer
            self.queue_str.append(f'ps {pathA} --> {pathB}')
            self.queue_up(fsA.push, pathA, pathB, overwrite=True)
            return
        elif mdtimeA < fsB.get_mdtime(pathB):
            # if `pathA` is older
            self.queue_str.append(f'ps {pathB} --> {pathA}')
            self.queue_up(fsB.push, pathB, pathA, overwrite=True)
    
    def sync_dir(self, dirA, dirB, fsA, fsB, skip=[], mark=False):
        mdtimeA = fsA.get_mdtime(dirA)
        rmtimeB = fsB.get_rmtime(dirB, 0)
        
        if rmtimeB > mdtimeA:  # if `dirB` was removed later
            self.queue_str.append(f'rm {dirA}')
            self.queue_up(fsA.rm, dirA)
            if mark:
                skip.append(dirB)
            return
        elif not fsB.exists(dirB) or fsB.S_ISREG(fsB.stat(dirB).st_mode):
            # if `dirB` does not exist or is a regular file
            self.queue_str.append(f'ps {dirA} --> {dirB}')
            self.queue_up(fsA.push, dirA, dirB)
            if mark:
                skip.append(dirB)
            return
        
        for itemA in dirA:  # walk through items under the folder `dirA`
            pathA = fsA.join(dirA, itemA)
            pathB = fsB.join(dirB, itemA)
            modeA = fsA.stat(pathA).st_mode
            if fsA.S_ISDIR(modeA):  # if it's a folder
                self.sync_dir(pathA, pathB, fsA, fsB, skip, mark)
                continue
            elif fsA.S_ISREG(modeA):  # if it's a file
                self.sync_file(pathA, pathB, fsA, fsB, skip, mark)
                continue
            raise TypeError(f'{pathA} should be a folder or file.')
    
    def compare(self, local, remote):
        skip = self.sync_dir(
            local, 
            remote, 
            self.local_file_system, 
            self.remote_file_system, 
            mark=True
        )
        self.sync_dir(
            remote, 
            local, 
            self.remote_file_system, 
            self.local_file_system, 
            skip=skip, 
        )
        pass
    
    def start(self):
        pass


class Queue(list):
    def __init__(self, iterable=None):
        self._actions = list()
        
        if iterable:
            super().__init__(iterable)
        else:
            super().__init__()
    
    def _append(self, obj):  # rename => private method
        super().append(obj)
    
    @classmethod
    @property
    def append(cls):  # remove parent method: `append`
        raise AttributeError(
            f"type object {cls.__qualname__} has no attribute 'append'")
    
    @property
    def actions(self):
        return self._actions
    
    def up(self, func, *args, **kwargs):
        wrapper = functools.partial(func, *args, **kwargs)
        self._append(wrapper)
        
        action = self._convert_to_action(func, args, kwargs)
        self.actions.append(action)
    
    def _convert_to_action(self, func, args, kwargs):
        func_name = func.__name__
        kwargs_str = self._convert_kwargs(kwargs)
        
        if func_name == 'rm':
            args_str = self._convert_args(args)
            return f'rm {args_str} {kwargs_str}'
        elif func_name == 'mv':
            args_str = self._convert_args(args[2:])
            return f'mv {args[0]} --> {args[1]} {args_str} {kwargs_str}'
        elif func_name == 'push':
            args_str = self._convert_args(args[2:])
            return f'ps {args[0]} --> {args[1]} {args_str} {kwargs_str}'
        raise TypeError(f"Unknown function {func}")
    
    def _convert_args(self, args):
        return ' '.join(map(str, args))
    
    def _convert_kwargs(self, kwargs):
        return ' '.join([ f'{k}={v}' for k, v in kwargs.items() ])


