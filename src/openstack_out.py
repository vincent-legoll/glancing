#! /usr/bin/env python

from __future__ import print_function

import os
import re
import sys

re_sep_line = re.compile(r'^[+-]+$')

def parse_block(block):
    header = []
    ret = []
    seps = 0
    length = 0
    for line in block.splitlines():
        if not line:
            continue
        if re_sep_line.match(line):
            seps += 1
            continue
        if seps == 0:
            continue
        elif seps == 3:
            break
        line_split = [i.strip() for i in line.split('|')][1:-1]
        ls_len = len(line_split)
        if seps == 1:
            header = line_split
            length = ls_len
        elif seps == 2:
            if length == ls_len:
                ret.append(line_split)
            else:
                print('wrong line length')
                continue
            
    return header, ret

def map_block(block):
    ret = {}
    h, b = parse_block(block)
    if len(h) == 2:
        for i in range(len(b)):
            if len(h) == len(b[i]):
                ret[b[i][0]] = b[i][1]
    elif len(h) > 2:
        for i in range(len(b)):
            if len(h) == len(b[i]):
                ret[b[i][0]] = b[i][1:]
    return ret
