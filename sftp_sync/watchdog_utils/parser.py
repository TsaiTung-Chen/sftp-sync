#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:47:17 2022

@author: tungchentsai
"""

def parse_arguments(*args):
    args = list(args)
    if len(args) < 1:
        raise TypeError(f'The script {__file__} expected the first arument ' \
                        'as `watch_path` and the rest as `ignore_patterns` ' \
                        f'(optional), but got {args}.')
    
    watch_path = get_watch_path(args)
    ignore_patterns = get_ignore_patterns(args)
    
    return watch_path, ignore_patterns


def get_watch_path(args):
    import os
    
    return os.path.expanduser(args[0])


def get_ignore_patterns(args):
    import os
    
    patterns = args[1:]
    for i, pattern in enumerate(patterns):
        patterns[i] = os.path.expanduser(pattern)
    
    return patterns

