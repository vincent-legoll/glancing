#! /usr/bin/env python

from __future__ import print_function

import sys
import uuid
import argparse

import utils
import openstack_out

from utils import vprint, vprint_lines

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
        vprint('failed to import image into glance: %s from %s' % (name, base))
        vprint_lines('stdout=' + out)
        vprint_lines('stderr=' + err)
    return ok

def glance_exists(name):
    if type(name) not in (str, unicode):
        vprint('glance_exists(name=%s): name is not a string, but a %s' % (name, str(type(name))))
        raise TypeError
    return len(glance_ids([name])) > 0

def glance_image_list():
    cmd = _GLANCE_CMD + ['image-list']
    ok, retcode, out, err = utils.run(cmd, out=True, err=True)
    if not ok:
        vprint('failed to get image-list from glance')
        vprint_lines('stdout=' + out)
        vprint_lines('stderr=' + err)
        return None
    return out

def glance_ids(names):
    ret = set()
    # Some are already IDs
    if type(names) in (str, unicode):
        names = [names]
    if names and utils.is_iter(names):
        il = glance_image_list()
        if il:
            h, b = openstack_out.parse_block(il)
            for image_id, image_name, _, _, _, _ in b:
                if image_name in names or image_id in names:
                    ret.add(image_id)
    return ret

def glance_delete_all(names, quiet=False):
    ret = False
    all_images_ids = glance_ids(names)
    if all_images_ids:
        ret = glance_delete_ids(all_images_ids, quiet=quiet)
    return ret

def glance_delete_ids(ids, quiet=False):
    ret = True
    for image_id in ids:
        ret &= glance_delete(image_id, quiet=quiet)
    return ret

def glance_delete(name, quiet=False):
    cmd = _GLANCE_CMD + ['image-delete', name]
    out, err = True, True
    if quiet:
        out, err = False, False
    ok, retcode, out, err = utils.run(cmd, out=out, err=err)
    if not ok:
        vprint('failed to delete image from glance: ' + name)
        if not quiet:
            vprint_lines('stdout=' + out)
            vprint_lines('stderr=' + err)
    return ok

def glance_download(name, fn_local):
    cmd = _GLANCE_CMD + ['image-download', '--file', fn_local, name]
    ok, retcode, out, err = utils.run(cmd, out=True, err=True)
    if not ok:
        vprint('failed to download image from glance: ' + name)
        vprint_lines('stdout=' + out)
        vprint_lines('stderr=' + err)
    return ok

# Handle CLI options
def do_argparse(sys_argv):
    parser = argparse.ArgumentParser(description='Manage glance VM images')

    # Global options
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display additional information')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--delete', dest='delete', metavar='NAME', nargs='+',
                       help='delete all images with the same name as '
                            'the specified VM')

    args = parser.parse_args(sys_argv)

    if args.verbose:
        utils.set_verbose(True)
        vprint('verbose mode')

    return args

def main(sys_argv=sys.argv):
    args = do_argparse(sys_argv)
    if args.delete:
        glance_delete_all(args.delete)
    return True

if __name__ == '__main__':
    main()
