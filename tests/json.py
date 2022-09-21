#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 22:15:08 2022

@author: tungchentsai
"""

import sys
import json


dic = {
       "file path 1": {"status": 'removed', "hooks_left": 2}, 
       "file path 2": {"status": 'removed', "hooks_left": 1}
}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise TypeError(
            f'{__file__} expected a json file path input argument.')
    
    fpath = sys.argv[1]
    
    with open(fpath, 'w') as jsonfile:
        json.dump(dic, jsonfile, ensure_ascii=False, indent=4)
    
    with open(fpath) as jsonfile:
        dic2 = json.load(jsonfile)
    
    print(dic2)

