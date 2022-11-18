#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 21:34:40 2022

@author: tungchentsai
"""


import paramiko


class SFTP(paramiko.SFTPClient):
    def __init__(self, host, port=22, username='', password=None):
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = super().from_transport(transport)
        self.__dict__.update(sftp.__dict__)
        
        self._settings = {
            "host": host,
            "port": port,
            "username": username,
            "password": password
        }
        self._transport = transport
    
    @property
    def settings(self):
        return self._settings
    
    @property
    def transport(self):
        return self._transport

