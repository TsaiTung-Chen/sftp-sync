#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 22:54:22 2022

@author: tungchentsai
"""

from . import events
from .file_systems import LocalFileSystem, RemoteFileSystem


class Queue(list):  # a list of `Operation`s
    def __init__(self, iterable=[]):
        super().__init__(iterable)
    
    def __add__(self, x):
        return self.from_iterable(super().__add__(x))
    
    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.from_iterable(super().__getitem__(i))
        return super().__getitem__(i)
    
    @classmethod
    def from_iterable(cls, iterable):
        return cls(iterable)
    
    @classmethod  # remove parent method: `append`
    @property
    def append(cls):
        raise AttributeError(
            f"type object '{cls.__qualname__}' has no attribute 'append'")
    
    @property
    def human_readable(self):
        n_ops = len(self)
        n_digits = len(str(n_ops))
        
        for i, op in enumerate(self, 1):
            yield f'|{self._zero_leading(i, n_ops, n_digits)}/{n_ops} {op}'
    
    def copy(self):
        return self.from_iterable(self)
    
    def _zero_leading(self, i, n_ops, n_digits):
        return ('{:0' + str(n_digits) + 'd}').format(i)
    
    def up(self, func, args, kwargs, time):
        super().append(Operation(func, args, kwargs, time=time, queue=self))
    
    def generator(self):
        # Operations in `self` will be removed once they are completed
        replica = self.copy()  # copy for static iteration
        
        for i, (op, text) in enumerate(zip(replica, replica.human_readable)):
            yield op, i, text
    
    def print(self, index_or_slice=None, print_fn=print) -> str:
        index_or_slice = index_or_slice or slice(len(self))
        human_readable = '\n'.join( self[index_or_slice].human_readable )
        
        print_fn(human_readable)
        
        return human_readable


class Operation:
    def __init__(self, func, args, kwargs, time:float, queue:Queue):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._time = time
        self._queue = queue
    
    @property
    def func(self):
        return self._func
    
    @property
    def args(self):
        return self._args
    
    @property
    def kwargs(self):
        return self._kwargs
    
    @property
    def time(self):
        return self._time
    
    @property
    def queue(self):
        return self._queue
    
    def __str__(self):
        kw_str = ' '.join([ f'{k}={v}' for k, v in self.kwargs.items() ])
        fs, func_name = self._parse()
        
        if func_name == 'transfer':
            if fs == 'local':
                return f'UPLOAD  | {self.args[0]} --> {self.args[1]} {kw_str}'
            return f'DOWNLOAD| {self.args[0]} --> {self.args[1]} {kw_str}'
        elif func_name == 'remove':
            return f'REMOVE  | {self.args[0]} {kw_str}'
        return f'MAKEDIR | {self.args[0]} {kw_str}'  # mkdir
    
    def __call__(self):
        try:
            self.func(*self.args, **self.kwargs)
            self.queue.remove(self)
            return
        except BaseException as e:
            e.args = (f'{e}\n[Operation failed]',)
            raise e
    
    def _parse(self):
        def _raise_unknown():
            raise TypeError(f"Unknown function: {self.func}")
        
        func_name = self.func.__name__
        fs = type(self.func.__self__)
        assert fs in {LocalFileSystem, RemoteFileSystem}, _raise_unknown()
        fs = 'local' if fs is LocalFileSystem else 'remote'
        
        if func_name == 'remove':
            assert len(self.args) == 1, f'{self.func}  {self.args}'
        elif func_name == 'mkdir':
            assert len(self.args) == 1, f'{self.func}  {self.args}'
        elif func_name == 'transfer':
            assert len(self.args) == 2, f'{self.func}  {self.args}'
        else:
            _raise_unknown()
        
        return fs, func_name
    
    def get_event(self, perspective):
        assert perspective in {'local', 'remote'}, repr(perspective)
        fs, func_name = self._parse()
        
        if perspective == fs:
            if func_name == 'mkdir':
                return events.ModifiedEvent(self.args[0], time=self.time)
            elif func_name == 'remove':
                return events.DeletedEvent(self.args[0], time=self.time)
            return events.NoneEvent()  # transfer
        if func_name == 'transfer':
            return events.ModifiedEvent(self.args[1], time=self.time)
        return events.NoneEvent()  # mkdir or remove

