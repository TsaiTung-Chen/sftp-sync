#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 22:54:22 2022

@author: tungchentsai
"""

from .file_systems import LocalFileSystem, RemoteFileSystem
from .loggers import LocalLogger, RemoteLogger
from .queue import Queue


class Synchronizer:
    def __init__(self, host, port=22, username='', password=None, slash=r'/'):
        local_fs = LocalFileSystem()
        remote_fs = RemoteFileSystem(host,
                                     port=port,
                                     username=username,
                                     password=password,
                                     slash=slash)
        local_fs.set_remote_file_system(remote_fs)
        remote_fs.set_local_file_system(local_fs)
        
        self._local_fs = local_fs
        self._remote_fs = remote_fs
        self._queue = Queue()
        self._remote_log_path = None
    
    @property
    def local_fs(self):
        return self._local_fs
    
    @property
    def remote_fs(self):
        return self._remote_fs
    
    @property
    def queue(self):
        return self._queue
    
    @property
    def remote_log_path(self):
        return self._remote_log_path
    
    def set_remote_log_path(self, path):
        self._remote_log_path = path
    
    def _compare_file(self, pathA, pathB, fsA, fsB):
        mdtimeA = fsA.get_mdtime(pathA)
        mdtimeB = fsB.get_mdtime(pathB, default=-1)
        rmtimeB = fsB.get_rmtime(pathB, default=-1)
        
        if mdtimeB == mdtimeA:
            return
        elif rmtimeB > mdtimeA:  # if `pathB` was removed later
            self.queue.up(fsA.remove, (pathA,), time=rmtimeB)
            return
        elif mdtimeB > mdtimeA:  # if `pathA` is older
            self.queue.up(fsB.transfer,
                          (pathB, pathA),
                          {"overwrite": True},
                          time=mdtimeB)
            return
        # if `pathB` does not exist or `pathA` is newer
        self.queue.up(fsA.transfer,
                      (pathA, pathB),
                      {"overwrite": True},
                      time=mdtimeA)
    
    def _compare_dir(self, dirA, dirB, fsA, fsB, 
                     mode='skip', skip=[], _root=True):
        if _root and (mode == 'skip') and (dirA in skip or dirB in skip):
            return skip
        
        mdtimeA = fsA.get_mdtime(dirA)
        rmtimeB = fsB.get_rmtime(dirB, default=0)
        
        if rmtimeB > mdtimeA:  # if `dirB` was removed later
            self.queue.up(fsA.remove,
                          (dirA,),
                          {"recursively": True},
                          time=rmtimeB)
            return skip
        
        if fsB.exists(dirB) or not fsB.S_ISDIR(fsB.stat(dirB).st_mode):
            self.queue.up(fsB.mkdir, (dirB,), time=mdtimeA)
        
        for entryA, attrA in self.list_attr(dirA):  # walk through entries
            entryA = fsA.join(dirA, entryA)
            entryB = fsB.join(dirB, entryA)
            
            if (mode == 'skip') and (entryA in skip or entryB in skip):
                continue
            
            modeA = attrA.st_mode
            if fsA.S_ISDIR(modeA):  # if it's a folder
                self._compare_dir(
                    entryA, entryB, fsA, fsB, mode=mode, skip=skip, _root=False)
                continue
            elif fsA.S_ISREG(modeA):  # if it's a file
                self._compare_file(entryA, entryB, fsA, fsB)
                if mode == 'mark':
                    skip.append(entryB)
                continue
            raise TypeError(f'{entryA} should be a folder or file.')
        
        if mode == 'mark':
            skip.append(dirB)
        
        return skip
    
    def compare(self, local, remote, print_fn=None, idx_print=None) -> Queue:
        if not self.local_fs.S_ISDIR(
                self.local_fs.stat(local).st_mode):
            raise ValueError(f"`local` ({local}) must be a folder path")
        if not self.remote_fs.S_ISDIR(
                self.remote_fs.stat(remote).st_mode):
            raise ValueError(f"`remote` ({remote}) must be a folder path")
        
        local = self.local_fs.normpath(local)
        remote = self.remote_fs.normpath(remote)
        
        local_logger, remote_logger = self._get_loggers(local, remote)
        self.local_fs.set_logger(local_logger)
        self.remote_fs.set_logger(remote_logger)
        
        # Walk through the local directory
        skip = self._compare_dir(
            local,
            remote,
            self.local_fs,
            self.remote_fs,
            mode='mark'
        )
        
        # Walk through the remote directory and skip entries which have been
        # compared before
        self._compare_dir(
            remote,
            local,
            self.remote_fs,
            self.local_fs,
            skip=skip
        )
        
        if print_fn is not None:
            self.queue.print(idx_print=idx_print, print_fn=print_fn)
        
        return self.queue
    
    def sync(self, print_fn=None):  #TODO multithread
        print_fn = print_fn or (lambda *msg: None)
        
        # Run all operations
        for op, i, text in self.queue.generator():
            print_fn(text)
            op()
            self.remote_fs.logger.log(op.get_event(persective='remote'))
        print_fn('[All operations completed]')
        
        # Upload the temporary remote log to update the log file on the cloud
        self.local_fs.transfer(
            self.remote_fs.logger.log_path,
            self.remote_log_path,
            overwrite=True
        )
        print_fn('[Log file updated]')
    
    def _get_logger(self, local, remote):
        # Download the remote log file on the SFTP server
        remote_log = self.remote_fs.join(remote,
                                         RemoteLogger.sftp_sync_folder,
                                         RemoteLogger.filename)
        remote_log_on_local = self.local_fs.join(local,
                                                 RemoteLogger.sftp_sync_folder,
                                                 RemoteLogger.filename)
        self.remote_fs.download(remote_log, remote_log_on_local, overwrite=True)
        self.set_remote_log_path(remote_log)
        
        # Initiate the loggers with local path. Both the local and remote log
        # files will be saved in the local folder (.sftp-sync).
        # PS. After syncing, the remote log file will be uploaded to the server
        return LocalLogger(local), RemoteLogger(local)

