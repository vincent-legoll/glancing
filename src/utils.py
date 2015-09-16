#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import uuid
import math
import types
import shutil
import inspect
import argparse
import tempfile
import textwrap
import functools
import subprocess
import collections

try:
    import StringIO
except ImportError:
    import io as StringIO

from contextlib import contextmanager

if 'DEVNULL' not in dir(subprocess):
    subprocess.DEVNULL = open(os.devnull, 'r+b')

_VERBOSE = False

def set_verbose(v=None):
    global _VERBOSE
    if v is None:
        _VERBOSE = not _VERBOSE
    else:
        _VERBOSE = True if v else False

def get_verbose():
    global _VERBOSE
    return _VERBOSE

def vprint(msg, prog=sys.argv[0]):
    if _VERBOSE:
        print("%s: %s" % (prog, msg))

def vprint_lines(msg, prog=sys.argv[0]):
    for line in msg.split('\n'):
        vprint(line, prog=prog)

def test_name():
    return inspect.stack()[1][3]

def is_uuid(x):
    if type(x) == uuid.UUID:
        return True
    try:
        uuid.UUID(x)
        return True
    except Exception:
        pass
    return False

def is_iter(x):
    try:
        it = iter(x)
        return True
    except TypeError:
        pass
    return False

class size_t(object):

    # This is not S.I. compliant prefix, this is power-of-two based
    _UNIT_PREFIX = ['', 'K', 'M', 'G', 'T', 'P']

    # This class does no rounding: 2047 => 1K, 2048 => 2K
    def __init__(self, n, suffix=''):
        self._n = n
        self.suffix = suffix
        self.exp = int(math.log(n, 2) / 10) if n != 0 else 0
        self.n = long(long(n) / long(2 ** long(10 * self.exp)))

    def __repr__(self):
        return '<size_t %d%s>' % (self._n, self.suffix)

    def __str__(self):
        return '%d%s%s' % (self.n, self._UNIT_PREFIX[self.exp], self.suffix)

def output(out, quiet):
    if out:
        stdout = subprocess.PIPE
    elif quiet is None or quiet is True:
        stdout = subprocess.DEVNULL
    else:
        stdout = None
    return stdout

def run(cmd, out=False, err=False, quiet_out=None, quiet_err=None):
    stdout = output(out, quiet_out)
    stderr = output(err, quiet_err)
    stdoutdata, stderrdata = None, None
    try:
        subp = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr)
        stdoutdata, stderrdata = subp.communicate()
        return (subp.returncode == 0, subp.returncode,
                stdoutdata if out else None, stderrdata if err else None)
    except OSError as e:
        vprint("'%s': Cannot execute, please check it is properly"
               " installed, and available through your PATH environment "
               "variable." % (cmd[0],))
        vprint(e)
    return False, None, None, None

class chdir(object):

    def __init__(self, dir_path):
        if not os.path.isdir(dir_path):
            raise ValueError('Not a directory')
        self.dir_path = dir_path

    def __enter__(self):
        self.oldcwd = os.getcwd()
        os.chdir(self.dir_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.oldcwd)

class tempdir(chdir):

    def __init__(self, prefix='glancing-'):
        super(tempdir, self).__init__(tempfile.mkdtemp(prefix=prefix))

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(tempdir, self).__exit__(exc_type, exc_val, exc_tb)
        shutil.rmtree(self.dir_path)

class redirect(object):

    def __init__(self, iodesc_name, iofile=None):
        # Prepare
        self._oldiodesc_name = iodesc_name
        if iofile is None:
            self._opened = True
            self._iofile = open(os.devnull, 'r+b')
        else:
            self._opened = False
            self._iofile = iofile

    def __enter__(self):
        # Backup
        self._oldiodesc = sys.__dict__[self._oldiodesc_name]
        # Modify
        sys.__dict__[self._oldiodesc_name] = self._iofile

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        if self._opened:
            self._iofile.close()
        # Restore
        sys.__dict__[self._oldiodesc_name] = self._oldiodesc

class devnull(redirect):

    def __init__(self, iodesc_name):
        super(devnull, self).__init__(iodesc_name, None)

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

class cleanup(object):

    def __init__(self, cleanup_cmd):
        # Prepare
        self._cleanup_cmd = cleanup_cmd

    def _cleanup(self):
        run(self._cleanup_cmd)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore
        self._cleanup()

class clean(cleanup):

    def __enter__(self):
        self._cleanup()

class stringio(object):

    def __init__(self):
        self._iofile = StringIO.StringIO()

    def __enter__(self):
        return self._iofile

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._iofile.close()

def block_read_filename(filename, callback, block_size=4096):
    with open(filename, 'rb') as f:
        block_read_filedesc(f, callback, block_size)

def block_read_filedesc(filedesc, callback, block_size=4096):
    chunk_reader = functools.partial(filedesc.read, block_size)
    for block in iter(chunk_reader, ''):
        callback(block)

class Exceptions(object):

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], collections.Iterable):
            keys = args[0]
        else:
            keys = args
        self._excs = []
        for item in keys:
            if type(item) == type(Exception):
                item = item()
            if isinstance(item, Exception):
                self._excs.append(item)

    def __contains__(self, other):
        for item in self._excs:
            if (item.__class__ == other.__class__ and
               item.args == other.args):
                return True
        return False

class AlmostRawFormatter(argparse.HelpFormatter):

    '''
    Based on code from:
    http://dolinked.com/questions/12720/python-argparse-how-to-insert-newline-the-help-text
    '''
    _PREFIX = '>>>'

    def _split_lines(self, text, width):
        if text.strip().startswith(self._PREFIX):
            return textwrap.dedent(text[len(self._PREFIX):]).strip().splitlines()
        return super(AlmostRawFormatter, self)._split_lines(text, width)
