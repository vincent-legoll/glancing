#! /usr/bin/env python

from __future__ import print_function

import os
import sys

from contextlib import contextmanager

def mod_path():
    file_myself = __file__ or sys.argv[0]
    ret_path = os.path.dirname(file_myself)
    if not os.path.isabs(ret_path):
        ret_path = os.path.join(os.getcwd(), ret_path)
    return os.path.realpath(ret_path)

def get_local_path(*args):
    return os.path.realpath(os.path.join(mod_path(), *args))

class devnull(object):
    
    def __init__(self, iodesc_name):
        self._oldiodesc_name = iodesc_name

    def __enter__(self):
        self._oldiodesc = sys.__dict__[self._oldiodesc_name]
        sys.__dict__[self._oldiodesc_name] = open(os.devnull, 'w+b')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.__dict__[self._oldiodesc_name].close()
        sys.__dict__[self._oldiodesc_name] = self._oldiodesc
