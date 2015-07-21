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
        # Prepare
        self._oldiodesc_name = iodesc_name

    def __enter__(self):
        # Backup
        self._oldiodesc = sys.__dict__[self._oldiodesc_name]
        # Modify
        sys.__dict__[self._oldiodesc_name] = open(os.devnull, 'w+b')

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        sys.__dict__[self._oldiodesc_name].close()
        # Restore
        sys.__dict__[self._oldiodesc_name] = self._oldiodesc

class environ(object):

    def __init__(self, envvar_name, envvar_val=''):
        # Prepare
        self._envvar_name = envvar_name
        self._envvar_val = envvar_val
        self._not_present = False

    def __enter__(self):
        # Backup current state
        if self._envvar_name not in os.environ:
            self._not_present = True
        else:
            self._old_envvar_val = os.environ[self._envvar_name]
        # Modify
        os.environ[self._envvar_name] = self._envvar_val

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore
        if self._not_present:
            del os.environ[self._envvar_name]
        else:
            os.environ[self._envvar_name] = self._old_envvar_val
