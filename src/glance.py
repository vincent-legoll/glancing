#! /usr/bin/env python

import utils

from utils import vprint

_GLANCE_CMD = ['glance']

# Check glance availability early
def glance_ok():
    ok, retcode, out, err = utils.run(_GLANCE_CMD)
    if not ok:
        return False
    return True

# Import VM image into glance
def glance_import(base, md5=None, name=None, diskformat=None):
    cmd = _GLANCE_CMD + ['image-create', '--container-format', 'bare', '--file', base]
    if diskformat is not None:
        cmd += ['--disk-format', diskformat]
    if name is not None:
        cmd += ['--name', name]
    if md5 is not None:
        cmd += ['--checksum', md5]
    ok, retcode, out, err = utils.run(cmd, out=True, err=True)
    if not ok:
        vprint('failed to import image into glance: %s %s' % (name, base))
        vprint('stdout=' + out)
        vprint('stderr=' + err)
    return ok

def glance_exists(name):
    cmd = _GLANCE_CMD + ['image-show', name]
    ok, retcode, out, err = utils.run(cmd, out=True, err=True)
    if not ok:
        vprint('failed to test existence from glance: ' + name)
        vprint('stdout=' + out)
        vprint('stderr=' + err)
    return ok

def glance_delete(name, quiet=False):
    cmd = _GLANCE_CMD + ['image-delete', name]
    out, err = True, True
    if quiet:
        out, err = False, False
    ok, retcode, out, err = utils.run(cmd, out=out, err=err)
    if not ok:
        vprint('failed to delete image from glance: ' + name)
        if not quiet:
            vprint('stdout=' + out)
            vprint('stderr=' + err)
    return ok

def glance_download(name, fn_local):
    cmd = _GLANCE_CMD + ['image-download', '--file', fn_local, name]
    ok, retcode, out, err = utils.run(cmd, out=True, err=True)
    if not ok:
        vprint('failed to download image from glance: ' + name)
        vprint('stdout=' + out)
        vprint('stderr=' + err)
    return ok
