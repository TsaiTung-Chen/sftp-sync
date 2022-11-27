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
    def set_logger(self, logger):
        self._logger = logger
    
    @property
    def logger(self):
        if hasattr(self, '_logger'):
            return self._logger
        raise ValueError("Set the logger with method `set_logger` first")
    
    @property
    def local_fs(self):
        if hasattr(self, '_local_fs'):
            return self._local_fs
        raise ValueError("Set the local file system with method "
                         "`set_local_file_system` first")
    
    @property
    def remote_fs(self):
        if hasattr(self, '_remote_fs'):
            return self._remote_fs
        raise ValueError("Set the remote file system with method "
                         "`set_remote_file_system` first")
    
    def S_ISDIR(self, mode):
        return os.path.stat.S_ISDIR(mode)
    
    def S_ISREG(self, mode):
        return os.path.stat.S_ISREG(mode)
    
    def S_ISLNK(self, mode):
        return os.path.stat.S_ISLNK(mode)
    
    def get_rmtime(self, path, default=None):
        return self.logger.get_rmtime(path, default=default)
    
#TODO    @staticmethod
#    def get_mvtime(path, default=None):
#        raise NotImplementedError()


class LocalFileSystem(BaseFileSystem):
    def set_remote_file_system(self, remote_fs):
        self._remote_fs = remote_fs
    
    def get_mdtime(self, path, default=None):
        if self.exists(path):
            return os.path.getmtime(path)
        return default
    
    def normpath(self, path):
        return os.path.normpath(path)
    
    def join(self, *args):
        return self.normpath(os.path.join(*args))
    
    def exists(self, path):
        return os.path.exists(path)
    
    def stat(self, path):
        return os.stat(path)
    
    def lstat(self, path):
        return os.lstat(path)
    
    def list_attr(self, path):  # not recursively
        parent, folders, files = next(os.walk(path))
        for filename in (folders + files):
            yield self.join(parent, filename), self.stat(filename)
    
    def mkdir(self, path, mode=511):
        os.mkdir(path, mode=mode)
    
    def remove(self, path, *, recursively=False, _st_mode=None):
        # `_st_mode` not used. It's for signature consistency of FileSystems
        
        mode = self.stat(path).st_mode
        if not self.S_ISDIR(mode):
            os.remove(path)
            return
        elif recursively:
            shutil.rmtree(path)
            return
        os.rmdir(path)
    
    def rename(self, source, destination, *, overwrite=False):
        if overwrite and self.exists(destination):
            self.remove(destination, recursively=True)
        os.rename(source, destination)
    
    # Upload
    def transfer(self, local_path, remote_path, *, overwrite=False, **kwargs):
        if overwrite and self.remote_fs.exists(remote_path):
            self.remote_fs.remove(remote_path, recursively=True)
        self.remote_fs.upload(local_path, remote_path, **kwargs)


class RemoteFileSystem(BaseFileSystem):
    def __init__(self, host, port=22, username='', password=None, slash=r'/'):
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
        self._slash = slash
    
    def set_local_file_system(self, local_fs):
        self._local_fs = local_fs
    
    @property
    def slash(self):
        return self._slash
    
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
    
    def normpath(self, path):
        if path.startswith(self.slash * 2):
            prefix = self.slash * 2
        elif path.startswith(self.slash):
            prefix = self.slash
        else:
            prefix = ''
        
        return prefix + self.slash.join( filter(None, path.split(self.slash)) )
    
    def join(self, *args):
        return self.normpath(self.slash.join(args))
    
    def exists(self, path):
        try:
            self.stat(path)
        except FileNotFoundError:
            return False
        return True
    
    def stat(self, path):
        return self.sftp.stat(path)
    
    def lstat(self, path):
        return self.sftp.lstat(path)
    
    def list_attr(self, path):
        for attr in self.sftp.listdir_attr(path):
            yield attr.filename, attr
    
    def mkdir(self, path, mode=511):
        self.sftp.mkdir(path, mode=mode)
    
    def remove(self, path, *, recursively=False, _st_mode=None):
        st_mode = _st_mode or self.stat(path).st_mode
        
        if self.S_ISREG(st_mode):
            self.sftp.remove(path)
            return
        elif self.S_ISDIR(st_mode):
            if recursively:
                for entry, attr in self.listdir_attr(path):
                    entry = self.join(path, entry)
                    self.remove(entry, recursively=True, _st_mode=attr.st_mode)
            self.sftp.rmdir(path)
            return
        raise TypeError(f'{path} should be a folder or file.')
    
    def rename(self, source, destination, *, overwrite=False):
        if overwrite and self.exists(destination):
            self.remove(destination, recursively=True)
        self.sftp.rename(source, destination)
    
    # Download
    def transfer(self, remote_path, local_path, *, overwrite=False, **kwargs):
        if overwrite and self.local_fs.exists(local_path):
            self.local_fs.remove(local_path, recursively=True)
        self.download(remote_path, local_path, **kwargs)
    
    def download(self, remote_path, local_path, *args, **kwargs):
        return self.sftp.get(remote_path, local_path, *args, **kwargs)
    
    def upload(self, local_path, remote_path, *args, **kwargs):
        return self.sftp.put(local_path, remote_path, *args, **kwargs)

