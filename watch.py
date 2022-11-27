#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

def main(*args):
    from sftp_sync.watch.watcher import Watcher
    from sftp_sync.watch.parser import parse_arguments
    
    watch_path, ignore_patterns = parse_arguments(*args)
    watcher = Watcher(watch_path, ignore_patterns=ignore_patterns)
    
    watcher.watch()


if __name__ == '__main__':
    import sys
        
    main(*sys.argv[1:])

