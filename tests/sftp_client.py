#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 23:02:47 2022

@author: tungchentsai
"""

HOST = 'localhost'
PORT = 23
USERNAME = 'username'
PASSWORD = 'password'

LOCALPATH = 'temp.txt'
REMOTEPATH = r"/sftp_test/temp.txt"


import paramiko


transport = paramiko.Transport((HOST, PORT))
transport.connect(username=USERNAME, password=PASSWORD)
sftp = paramiko.SFTPClient.from_transport(transport)
sftp.put(LOCALPATH, REMOTEPATH)
sftp.close()

