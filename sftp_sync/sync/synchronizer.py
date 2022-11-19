#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 22:54:22 2022

@author: tungchentsai
"""

import functools

from .file_systems import LocalFileSystem, RemoteFileSystem


class Queue(list):  # a list of functions
    def __init__(self, iterable=[]):
        super().__init__(iterable)
    
    def __add__(self, x):
        return self.from_iterable(super().__add__(x))
    
    def __getitem__(self, i):
        queue_list = super().__getitem__(i)
        
        if isinstance(queue_list, list):
            return self.from_iterable(queue_list)
        return queue_list
    
    @classmethod
    def from_iterable(cls, iterable):
        return cls(iterable)
    
    @classmethod
    def _raise_attribute_error(cls, attr):
        raise AttributeError(
            f"type object '{cls.__qualname__}' has no attribute '{attr}'")
    
    @classmethod  # remove parent method: `append`
    @property
    def append(cls): cls._raise_attribute_error('append')
    
    @classmethod
    @property
    def copy(cls): cls._raise_attribute_error('copy')
    
    @property
    def human_readable(self):
        n_ops = len(self)
        n_digits = len(str(n_ops))
        
        return [f'|{self._zero_leading(i, n_ops, n_digits)}/{n_ops} '
                f'{self._convert_to_text(op)}' for i, op in enumerate(self, 1)]
    
    def _zero_leading(self, i, n_ops, n_digits):
        return ('{:0' + str(n_digits) + 'd}').format(i)
    
    def up(self, func, *args, **kwargs):
        wrapper = functools.partial(func, *args, **kwargs)
        super().append(wrapper)
    
    def run(self, remove_completed=True, print_fn=None):
        def _run_operations():
            nonlocal i
            for i, (op, text) in enumerate(zip(self, self.human_readable), 1):
                print_fn(text)
                try:
                    op()
                    continue
                except BaseException as e:
                    i -= 1  # numbers of op to remove from the queue
                    err_msg = '\n'.join([str(e),
                                         '[Operation failed]:',
                                         self.human_readable[i]])
                    e.args = (err_msg,)
                    raise e
        
        if print_fn is None:
            print_fn = lambda *args, **kwargs: None
        
        i = 0
        try:
            _run_operations()
        finally:
            if remove_completed:
                self[:] = self[i:]
        
        print_fn(f'[All {i} operations completed]')
    
    def print(self, index_or_slice=None, print_fn=print) -> str:
        if index_or_slice is None:
            human_readable = self.human_readable
        else:
            human_readable = self[index_or_slice].human_readable
        human_readable = '\n'.join(human_readable)
        
        print_fn(human_readable)
        
        return human_readable
    
    def _convert_to_text(self, operation):
        def _remove():
            assert len(args) == 1, f'{operation.func}  {args}'
            return ' '.join([f'REMOVE  | {args[0]}', kw_str])
        
        def _mkdir():
            assert len(args) == 1, f'{operation.func}  {args}'
            return ' '.join([f'MAKEDIR | {args[0]}', kw_str])
        
        def _rename():
            assert len(args) == 2, f'{operation.func}  {args}'
            return ' '.join([f'MOVE    | {args[0]} --> {args[1]}', kw_str])
        
        def _transfer():
            assert len(args) == 2, f'{operation.func}  {args}'
            if isinstance(operation.func.__self__, LocalFileSystem):
                return ' '.join([f'UPLOAD  | {args[0]} --> {args[1]}', kw_str])
            elif isinstance(operation.func.__self__, RemoteFileSystem):
                return ' '.join([f'DOWNLOAD| {args[0]} --> {args[1]}', kw_str])
            raise TypeError(f"Unknown function: {operation.func}")
        
        def _others():
            raise TypeError(f"Unknown function: {operation.func}")
        
        func_name = operation.func.__name__
        args = operation.args
        kw_str = ' '.join([ f'{k}={v}' for k, v in operation.keywords.items() ])
        
        return {"remove": _remove,
                "mkdir": _mkdir,
                "rename": _rename,
                "transfer": _transfer}.get(func_name, _others)()


class Synchronizer:
    def __init__(self, local_file_system, remote_file_system):
        self._local_file_system = local_file_system
        self._remote_file_system = remote_file_system
        self._queue = Queue()
    
    @property
    def local_file_system(self):
        return self._local_file_system
    
    @property
    def remote_file_system(self):
        return self._remote_file_system
    
    @property
    def queue(self):
        return self._queue
    
    def sync_file(self, pathA, pathB, fsA, fsB):
        mdtimeA = fsA.get_mdtime(pathA)
        mdtimeB = fsB.get_mdtime(pathB, default=-1)
        rmtimeB = fsB.get_rmtime(pathB, default=-1)
        
        if mdtimeB == mdtimeA:
            return
        elif rmtimeB > mdtimeA:  # if `pathB` was removed later
            self.queue.up(fsA.remove, pathA)
            return
        elif mdtimeB > mdtimeA:  # if `pathA` is older
            self.queue.up(fsB.transfer, pathB, pathA, overwrite=True)
            return
        # if `pathB` does not exist or `pathA` is newer
        self.queue.up(fsA.transfer, pathA, pathB, overwrite=True)
    
    def sync_dir(self, dirA, dirB, fsA, fsB, mode='skip', skip=[], _root=True):
        if _root and (mode == 'skip') and (dirA in skip or dirB in skip):
            return skip
        
        mdtimeA = fsA.get_mdtime(dirA)
        rmtimeB = fsB.get_rmtime(dirB, default=0)
        
        if rmtimeB > mdtimeA:  # if `dirB` was removed later
            self.queue.up(fsA.remove, dirA, recursively=True)
            return skip
        
        if fsB.exists(dirB) or not fsB.S_ISDIR(fsB.stat(dirB).st_mode):
            self.queue.up(fsB.mkdir, dirB)
        
        for entryA, attrA in self.list_attr(dirA):  # walk through entries
            entryA = fsA.join(dirA, entryA)
            entryB = fsB.join(dirB, entryA)
            
            if (mode == 'skip') and (entryA in skip or entryB in skip):
                continue
            
            modeA = attrA.st_mode
            if fsA.S_ISDIR(modeA):  # if it's a folder
                self.sync_dir(
                    entryA, entryB, fsA, fsB, mode=mode, skip=skip, _root=False)
                if mode == 'mark':
                    skip.append(entryB)
                continue
            elif fsA.S_ISREG(modeA):  # if it's a file
                self.sync_file(entryA, entryB, fsA, fsB)
                if mode == 'mark':
                    skip.append(entryB)
                continue
            raise TypeError(f'{entryA} should be a folder or file.')
        
        skip.append(dirB)
        
        return skip
    
    def compare(self, local, remote, print_fn=None, idx_print=None) -> Queue:
        if not self.local_file_system.S_ISDIR(
                self.local_file_system.stat(local).st_mode):
            raise ValueError(f"`local` ({local}) must be a folder path")
        if not self.remote_file_system.S_ISDIR(
                self.remote_file_system.stat(remote).st_mode):
            raise ValueError(f"`remote` ({remote}) must be a folder path")
        
        local = self.local_file_system.normpath(local)
        remote = self.remote_file_system.normpath(remote)
        
        skip = self.sync_dir(
            local,
            remote,
            self.local_file_system,
            self.remote_file_system,
            mode='mark'
        )
        self.sync_dir(
            remote,
            local,
            self.remote_file_system,
            self.local_file_system,
            skip=skip
        )
        
        if print_fn is not None:
            self.queue.print(idx_print=idx_print, print_fn=print_fn)
        
        return self.queue
    
    def start(self, remove_completed=True, print_fn=None):  #TODO multithread
        self.queue.run(remove_completed=remove_completed, print_fn=print_fn)

