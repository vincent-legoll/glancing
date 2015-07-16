#! /usr/bin/env python

import sys

from utils import get_local_path

# Setup PYTHONPATH for multihash
sys.path.append(get_local_path('..', '..', 'src'))

import multihash

def multihash_test():
    pass
