#! /usr/bin/env python

import os
import sys

from utils import get_local_path

# Setup PYTHONPATH for decompressor
sys.path.append(get_local_path('..', '..', 'src'))

import decompressor

def decompressor_test():
    files = ['random_1M_bz2.bin.bz2', 'random_1M_gz.bin.gz']
    for fn in files:
        local_path = get_local_path('..', 'data', fn)
        d = decompressor.Decompressor(local_path)
        d.doit()
        name, sext = os.path.splitext(local_path)
        os.remove(name)
