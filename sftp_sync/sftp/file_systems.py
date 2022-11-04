#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 17:47:43 2022

@author: tungchentsai
"""

import os
import shutil
import paramiko


class BaseFileSystem:
    def __init__(self, logger):
        self._logger = logger
    
    @property
    def logger(self):
        return self._logger
    
    def get_rmtime(self, path, default=None):
        return self.logger.get_rmtime(path, default=default)
    
    def get_mdtime(self, path, default=None):
        raise NotImplementedError()
    
#TODO    @staticmethod
#    def get_mvtime(path, default=None):
#        raise NotImplementedError()
    
    def join(self, *args):
        raise NotImplementedError()
    
    def exists(self, path):
        raise NotImplementedError()
    
    def stat(self, path):
        raise NotImplementedError()
    
    def lstat(self, path):
        raise NotImplementedError()
    
    def S_ISDIR(self, mode):
        return os.path.stat.S_ISDIR(mode)
    
    def S_ISREG(self, mode):
        return os.path.stat.S_ISREG(mode)
    
    def S_ISLNK(self, mode):
        return os.path.stat.S_ISLNK(mode)
    
    def rm(self, path, *, recursively=False):
        raise NotImplementedError()
    
    def mv(self, source, destination, *, recursively=False):
        raise NotImplementedError()
    
    def push(self, source, destination, *, recursively=False, overwrite=False):
        raise NotImplementedError()


class LocalFileSystem(BaseFileSystem):
    def get_mdtime(self, path, default=None):
        return os.path.getmtime(path)
    
    def join(self, *args):
        return os.path.join(*args)
    
    def exists(self, path):
        return os.path.exists(path)
    
    def stat(self, path):
        return os.stat(path)
    
    def lstat(self, path):
        return os.lstat(path)
    
    def rm(self, path, *, recursively=False):
        if os.path.isfile(path):
            os.remove(path)
        elif recursively:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
    
    def mv(self, source, destination, *, recursively=False):
        if recursively:  # makedirs if parent directories do not exist
            os.renames(source, destination)
        else:
            os.rename(source, destination)
    
    def push(self, local, remote, *, recursively=False, overwrite=False):
        raise NotImplementedError()


class RemoteFileSystem(BaseFileSystem):
    def __init__(self, host, port, username, password, *args, **kwargs):
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        self._settings = {
            "host": host, 
            "port": port, 
            "username": username, 
            "password": password
        }
        self._transport = transport
        self._sftp = sftp
        
        super().__init__(*args, **kwargs)
    
    @property
    def settings(self):
        return self._settings
    
    @property
    def transport(self):
        return self._transport
    
    @property
    def sftp(self):
        return self._sftp
    
    def get_mdtime(self, path, default=None):
        return self.logger.get_mdtime(path, default=default)
    
    def join(self, *args):
        return r'/'.join(args)
    
    def exists(self, path):
        try:
            self.sftp.stat(path)
        except FileNotFoundError:
            return False
        return True
    
    def stat(self, path):
        return self.sftp.stat(path)
    
    def lstat(self, path):
        return self.sftp.lstat(path)

