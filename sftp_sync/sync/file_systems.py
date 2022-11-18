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
    def __init__(self, slash=None, logger=None):
        self._slash = slash
        self._logger = logger
    
    @property
    def slash(self):
        return self._slash
    
    @property
    def logger(self):
        return self._logger
    
    def S_ISDIR(self, mode):
        return os.path.stat.S_ISDIR(mode)
    
    def S_ISREG(self, mode):
        return os.path.stat.S_ISREG(mode)
    
    def S_ISLNK(self, mode):
        return os.path.stat.S_ISLNK(mode)
    
    def get_rmtime(self, path, default=None):
        return self.logger.get_rmtime(path, default=default)
    
    def get_mdtime(self, path, default=None): raise NotImplementedError()
    
#TODO    @staticmethod
#    def get_mvtime(path, default=None):
#        raise NotImplementedError()
    
    def join(self, *args): raise NotImplementedError()
    
    def exists(self, path): raise NotImplementedError()
    
    def stat(self, path): raise NotImplementedError()
    
    def lstat(self, path): raise NotImplementedError()
    
    def remove(self, path, *, recursively=True): raise NotImplementedError()
    
    def move(self, source, destination, *, overwrite=False):
        raise NotImplementedError()
    
    def transfer(self, source, destination, *, overwrite=False, **kwargs):
        raise NotImplementedError()


class LocalFileSystem(BaseFileSystem):
    def __init__(self, slash=os.path.sep, **kwargs):
        super().__init__(slash=slash, **kwargs)
    
    def set_remote_file_system(self, remote_file_system):
        self._remote_file_system = remote_file_system

    @property
    def remote_file_system(self):
        return self._remote_file_system
    
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
    
    def listdir_attr(self, path):
        for parent, folders, files in os.walk(path):
            for filename in (folders + files):
                yield filename, self.stat(filename)
            
            return  # not recursively
    
    def remove(self, path, *, st_mode=None, recursively=False):
        # `st_mode` not used. It's for signature consistency of FileSystems
        
        if os.path.isfile(path):
            os.remove(path)
            return
        elif recursively:
            shutil.rmtree(path)
            return
        os.rmdir(path)
    
    def move(self, source, destination, *, overwrite=False):
        if overwrite and self.exists(destination):
            self.remove(destination, recursively=True)
        os.rename(source, destination)
    
    # Upload
    def transfer(self, localpath, remotepath, *, overwrite=False, **kwargs):
        if overwrite and self.remote_file_system.exists(remotepath):
            self.remote_file_system.remove(remotepath, recursively=True)
        self.remote_file_system._put(localpath, remotepath, **kwargs)


class RemoteFileSystem(BaseFileSystem):
    def __init__(self, host, port=22, username='', password=None, 
                 slash=r'/', **kwargs):
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        super().__init__(slash=slash, **kwargs)
        
        self._settings = {
            "host": host,
            "port": port,
            "username": username,
            "password": password
        }
        self._transport = transport
        self._sftp = sftp
    
    def set_local_file_system(self, local_file_system):
        self._local_file_system = local_file_system
    
    @property
    def local_file_system(self):
        return self._local_file_system
    
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
        
        return prefix + '/'.join([ s for s in path.split(r'/') if s ])
    
    def join(self, *args):
        return self.normpath(r'/'.join(args))
    
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
    
    def listdir_attr(self, path):
        for attr in self.sftp.listdir_attr(path):
            yield attr.filename, attr
    
    def remove(self, path, *, st_mode=None, recursively=False):
        st_mode = st_mode or self.stat(path).st_mode
        
        if self.S_ISREG(st_mode):
            self.sftp.remove(path)
            return
        elif self.S_ISDIR(st_mode):
            if recursively:
                for entry, attr in self.listdir_attr(path):
                    entry = self.join(path, entry)
                    self.remove(entry, st_mode=attr.st_mode, recursively=True)
            self.sftp.rmdir(path)
            return
        raise TypeError(f'{path} should be a folder or file.')
    
    def move(self, source, destination, *, overwrite=False):
        if overwrite and self.exists(destination):
            self.remove(destination, recursively=True)
        os.rename(source, destination)
    
    # Download
    def transfer(self, remotepath, localpath, *, overwrite=False, **kwargs):
        if overwrite and self.local_file_system.exists(localpath):
            self.local_file_system.remove(localpath, recursively=True)
        self._get(remotepath, localpath, **kwargs)
    
    def _get(self, remotepath, localpath, *args, **kwargs):
        self.sftp.get(remotepath, localpath, *args, **kwargs)
    
    def _put(self, localpath, remotepath, *args, **kwargs):
        return self.sftp.put(localpath, remotepath, *args, **kwargs)

